"""微信登录互通测试：wx-login / bind-wx / 账号互认

覆盖场景：
1. 新微信用户一键登录 → 自动注册
2. 同一微信二次登录 → 复用同一账号
3. 账密用户绑定微信后，微信登录直达同一账号（三端互通核心）
4. openid 已绑其他账号时再次绑定 → 400 冲突
5. 微信返回错误（无效 code）→ 400
6. /auth/me 返回 has_wx_bind
7. set-password：微信用户设置账密后可在 PC/H5 登录同一账号（全端互通闭环）
8. set-password：已有密码用户改密必须验证原密码

运行：cd backend && python -m pytest tests/test_wx_auth.py -v
"""
import os
import sys
import tempfile

# 必须在导入 app 之前设置环境变量：隔离临时数据库 + 注入微信测试配置
_TMP_DB = os.path.join(tempfile.gettempdir(), "petcare_test_wx_auth.db")
if os.path.exists(_TMP_DB):
    os.remove(_TMP_DB)
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB}"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["WX_APPID"] = "wx_test_appid"
os.environ["WX_APP_SECRET"] = "wx_test_secret"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient

from app.main import app  # noqa: E402（import 时自动 create_all 建表）
from app.routers import users as users_router


class FakeWxResponse:
    """模拟微信 jscode2session 的响应"""

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


@pytest.fixture()
def client(monkeypatch):
    """TestClient + 默认把 code2session mock 成 code→openid 直接映射"""

    def fake_code2session(code):
        if code == "bad_code":
            from fastapi import HTTPException
            raise HTTPException(400, "微信登录凭证无效，请重试")
        return {"openid": "openid_" + code, "session_key": "sk_" + code}

    monkeypatch.setattr(users_router, "code2session", fake_code2session)
    with TestClient(app) as c:
        yield c


def register_and_login(client, username="alice", password="Passw0rd123"):
    r = client.post("/api/auth/register", json={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["data"]


def test_wx_login_new_user_auto_register(client):
    """场景1：新微信用户 → 自动注册并返回可用 token"""
    r = client.post("/api/auth/wx-login", json={"code": "code_a"})
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["is_new"] is True
    assert data["token"]
    assert data["user"]["has_wx_bind"] is True
    assert data["user"]["username"].startswith("wx_")

    # token 可正常访问受保护接口
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {data['token']}"})
    assert me.status_code == 200
    assert me.json()["data"]["id"] == data["user"]["id"]


def test_wx_login_same_user_reuse(client):
    """场景2：同一微信二次登录 → 同一账号"""
    r1 = client.post("/api/auth/wx-login", json={"code": "code_b"})
    r2 = client.post("/api/auth/wx-login", json={"code": "code_b"})
    u1 = r1.json()["data"]["user"]
    d2 = r2.json()["data"]
    assert d2["is_new"] is False
    assert d2["user"]["id"] == u1["id"]


def test_bind_then_wx_login_same_account(client):
    """场景3（互通核心）：账密注册 → 绑定微信 → 微信登录直达同一账号"""
    reg = register_and_login(client, username="bob", password="Passw0rd123")
    token = reg["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 绑定前 has_wx_bind = False
    assert reg["user"]["has_wx_bind"] is False

    # 绑定微信
    r = client.post("/api/auth/bind-wx", json={"code": "code_c"}, headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["data"]["has_wx_bind"] is True

    # 此后微信一键登录应落到同一账号（PC/H5 账密账号 ↔ 微信身份打通）
    r2 = client.post("/api/auth/wx-login", json={"code": "code_c"})
    d2 = r2.json()["data"]
    assert d2["is_new"] is False
    assert d2["user"]["id"] == reg["user"]["id"]
    assert d2["user"]["username"] == "bob"


def test_bind_conflict_when_openid_taken(client):
    """场景4：openid 已绑其他账号 → 400"""
    # 微信用户先登录（自动注册并占用 openid_code_d）
    client.post("/api/auth/wx-login", json={"code": "code_d"})
    # 另一个账密用户尝试绑定同一微信
    reg = register_and_login(client, username="carol", password="Passw0rd123")
    r = client.post(
        "/api/auth/bind-wx",
        json={"code": "code_d"},
        headers={"Authorization": f"Bearer {reg['token']}"},
    )
    assert r.status_code == 400
    assert "已绑定其他账号" in r.json()["detail"]


def test_wx_login_invalid_code(client):
    """场景5：微信侧返回错误 → 400 且不透传内部细节"""
    r = client.post("/api/auth/wx-login", json={"code": "bad_code"})
    assert r.status_code == 400
    assert r.json()["detail"] == "微信登录凭证无效，请重试"


def test_bind_wx_requires_login(client):
    """场景6：未登录调用 bind-wx → 401"""
    r = client.post("/api/auth/bind-wx", json={"code": "code_e"})
    assert r.status_code == 401


def test_me_has_wx_bind_flag(client):
    """场景7：/auth/me 的 has_wx_bind 与实际绑定状态一致"""
    reg = register_and_login(client, username="dave", password="Passw0rd123")
    headers = {"Authorization": f"Bearer {reg['token']}"}
    assert client.get("/api/auth/me", headers=headers).json()["data"]["has_wx_bind"] is False
    client.post("/api/auth/bind-wx", json={"code": "code_f"}, headers=headers)
    assert client.get("/api/auth/me", headers=headers).json()["data"]["has_wx_bind"] is True


# ===== 设置/修改密码（微信用户 → PC/H5 互通的最后一环） =====

def test_set_password_for_wx_user_enables_pc_login(client):
    """场景8：微信自动注册用户设置用户名+密码后，即可在 PC/H5 用账密登录同一账号"""
    r = client.post("/api/auth/wx-login", json={"code": "code_pw"})
    data = r.json()["data"]
    assert data["user"]["has_password"] is False

    headers = {"Authorization": f"Bearer {data['token']}"}
    # 微信用户无需 old_password，可同时把 wx_xxx 随机名改成好记的用户名
    r2 = client.post(
        "/api/auth/set-password",
        json={"username": "wxuser_pc", "password": "WxPc1234"},
        headers=headers,
    )
    assert r2.status_code == 200, r2.text
    body = r2.json()["data"]
    assert body["has_password"] is True
    assert body["username"] == "wxuser_pc"

    # 用 PC/H5 的账密方式登录：成功且是同一账号（跨端互通闭环）
    r3 = client.post("/api/auth/login", json={"username": "wxuser_pc", "password": "WxPc1234"})
    assert r3.status_code == 200, r3.text
    assert r3.json()["data"]["user"]["id"] == data["user"]["id"]


def test_change_password_requires_old_password(client):
    """场景9：已有密码的用户改密必须验证原密码"""
    reg = register_and_login(client, username="changepw", password="OldPass123")
    headers = {"Authorization": f"Bearer {reg['token']}"}

    # 不提供 / 提供错误的原密码 → 400
    for payload in ({"password": "NewPass456"},
                    {"password": "NewPass456", "old_password": "wrong"}):
        r = client.post("/api/auth/set-password", json=payload, headers=headers)
        assert r.status_code == 400

    # 正确原密码 → 修改成功
    r = client.post(
        "/api/auth/set-password",
        json={"password": "NewPass456", "old_password": "OldPass123"},
        headers=headers,
    )
    assert r.status_code == 200, r.text

    # 旧密码失效，新密码生效
    assert client.post("/api/auth/login", json={"username": "changepw", "password": "OldPass123"}).status_code == 401
    assert client.post("/api/auth/login", json={"username": "changepw", "password": "NewPass456"}).status_code == 200


def test_set_password_requires_login(client):
    """场景10：未登录调用 set-password → 401"""
    r = client.post("/api/auth/set-password", json={"password": "Abcd1234"})
    assert r.status_code == 401


def test_me_includes_has_password(client):
    """场景11：/auth/me 的 has_password 与实际状态一致"""
    reg = register_and_login(client, username="meflag", password="Pass1234")
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {reg['token']}"})
    assert me.status_code == 200
    assert me.json()["data"]["has_password"] is True


# ===== code2session 错误码细分（按微信开放文档《微信登录开发指南》） =====
# 这里直接测真实的 code2session 函数（mock httpx.get），而不是上面被替换的假函数
from fastapi import HTTPException  # noqa: E402
import app.routers.users as users_mod  # noqa: E402


def _mock_wx(monkeypatch, payload):
    class _Resp:
        def json(self):
            return payload

    monkeypatch.setattr(users_mod.httpx, "get", lambda *a, **kw: _Resp())


def test_code2session_success_returns_openid_and_unionid(monkeypatch):
    """正常返回 openid（绑定开放平台时还会有 unionid）"""
    _mock_wx(monkeypatch, {"openid": "o123", "session_key": "sk", "unionid": "u456"})
    data = users_mod.code2session("any_code")
    assert data["openid"] == "o123"
    assert data["unionid"] == "u456"


def test_code2session_invalid_code_40029(monkeypatch):
    """40029 code 无效 → 400（前端可换新 code 重试）"""
    _mock_wx(monkeypatch, {"errcode": 40029, "errmsg": "invalid code"})
    with pytest.raises(HTTPException) as ei:
        users_mod.code2session("stale_code")
    assert ei.value.status_code == 400


def test_code2session_code_reused_40163(monkeypatch):
    """40163 code 已被使用（code 一次性）→ 400"""
    _mock_wx(monkeypatch, {"errcode": 40163, "errmsg": "code been used"})
    with pytest.raises(HTTPException) as ei:
        users_mod.code2session("used_code")
    assert ei.value.status_code == 400


def test_code2session_rate_limited_45011(monkeypatch):
    """45011 频率限制 → 503（提示稍后重试，避免立即重试加剧频控）"""
    _mock_wx(monkeypatch, {"errcode": 45011, "errmsg": "api freq control"})
    with pytest.raises(HTTPException) as ei:
        users_mod.code2session("any_code")
    assert ei.value.status_code == 503


def test_code2session_bad_secret_40125(monkeypatch):
    """40125 AppSecret 错误 → 500（服务端配置问题，不应让客户端反复重试）"""
    _mock_wx(monkeypatch, {"errcode": 40125, "errmsg": "invalid appsecret"})
    with pytest.raises(HTTPException) as ei:
        users_mod.code2session("any_code")
    assert ei.value.status_code == 500


def test_code2session_wx_busy_minus1(monkeypatch):
    """-1 微信系统繁忙 → 502"""
    _mock_wx(monkeypatch, {"errcode": -1, "errmsg": "system busy"})
    with pytest.raises(HTTPException) as ei:
        users_mod.code2session("any_code")
    assert ei.value.status_code == 502