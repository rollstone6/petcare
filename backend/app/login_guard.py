"""宠物宝 (PetCare) — 登录失败锁定（按 IP + 用户名，内存计数）

规则：同一 (IP, 用户名) 组合连续失败 5 次 → 锁定 15 分钟；
同一 IP 对不同用户名累计失败 20 次（撞库特征）→ 该 IP 锁定 30 分钟。
成功登录清零。重启进程即重置（可接受，nginx 层另有全局限速兜底）。
"""
import os
import time
from threading import Lock

LOCK_THRESHOLD_USER = int(os.getenv("LOGIN_LOCK_THRESHOLD_USER", "5"))
LOCK_SECONDS_USER = int(os.getenv("LOGIN_LOCK_SECONDS_USER", "900"))       # 15 分钟
LOCK_THRESHOLD_IP = int(os.getenv("LOGIN_LOCK_THRESHOLD_IP", "20"))
LOCK_SECONDS_IP = int(os.getenv("LOGIN_LOCK_SECONDS_IP", "1800"))          # 30 分钟

_lock = Lock()
_fail_user: dict[str, list] = {}   # key -> [fail_count, locked_until_ts]
_fail_ip: dict[str, list] = {}


def check_locked(ip: str, username: str) -> None:
    """在验证密码前调用；处于锁定期则抛 429。"""
    now = time.time()
    with _lock:
        for rec, until_msg in (
            (_fail_user.get(f"{ip}|{username}"), "失败次数过多，请 15 分钟后再试"),
            (_fail_ip.get(ip), "该 IP 失败次数过多，请 30 分钟后再试"),
        ):
            if rec and rec[1] > now:
                from fastapi import HTTPException
                raise HTTPException(429, f"登录尝试被暂时锁定：{until_msg}")


def record_failure(ip: str, username: str) -> None:
    now = time.time()
    with _lock:
        rec = _fail_user.setdefault(f"{ip}|{username}", [0, 0.0])
        rec[0] += 1
        if rec[0] >= LOCK_THRESHOLD_USER:
            rec[1] = now + LOCK_SECONDS_USER
        iprec = _fail_ip.setdefault(ip, [0, 0.0])
        iprec[0] += 1
        if iprec[0] >= LOCK_THRESHOLD_IP:
            iprec[1] = now + LOCK_SECONDS_IP


def record_success(ip: str, username: str) -> None:
    with _lock:
        _fail_user.pop(f"{ip}|{username}", None)
        iprec = _fail_ip.get(ip)
        if iprec:
            iprec[0] = max(0, iprec[0] - 1)
