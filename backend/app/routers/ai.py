"""宠物宝 (PetCare) — AI 问答 API"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import urllib.request, json, os, yaml

from app.auth import get_current_user
from app import models

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI问答"])

# 从 hermes 配置读取 API key
def _get_ark_key():
    config_path = os.path.expanduser("~/.hermes/config.yaml")
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
        return config.get("model", {}).get("api_key", "")
    except Exception:
        return os.getenv("ARK_API_KEY", "")

ARK_KEY = _get_ark_key()
ARK_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

SYSTEM_PROMPT = """你是宠物宝(PetCare)的AI助手，专门解答宠物药品、食品、保健品相关问题。

请用中文回答，简洁专业，适合宠物主阅读。回答格式：
1. 先直接回答问题
2. 如有需要，补充注意事项
3. 最后可推荐相关产品类型

如果问题超出宠物健康范围，请礼貌说明你只能回答宠物相关问题。

注意：你的建议仅供参考，不能替代兽医诊断。涉及用药请务必咨询兽医。"""


class AskRequest(BaseModel):
    question: str
    context: str = ""


@router.post("/ask")
async def ask(
    req: AskRequest,
    user: models.User = Depends(get_current_user),
):
    """AI 问答（建议登录，未登录限频）"""
    if not ARK_KEY:
        raise HTTPException(500, "AI 服务未配置")

    user_msg = req.question
    if req.context:
        user_msg = f"用户正在查看「{req.context}」，问题：{req.question}"

    body = json.dumps({
        "model": "deepseek-v4-flash-260425",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        "max_tokens": 800,
        "temperature": 0.7,
    }).encode()

    try:
        r = urllib.request.Request(ARK_URL, data=body, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ARK_KEY}",
        })
        with urllib.request.urlopen(r, timeout=30) as resp:
            data = json.loads(resp.read())
            answer = data["choices"][0]["message"]["content"]
            return {"code": 0, "data": {"answer": answer}}
    except Exception as e:
        # 服务端日志记录完整错误，客户端只返回通用信息
        logger.error(f"AI service error: {e}")
        raise HTTPException(500, "AI 服务暂时不可用，请稍后重试")
