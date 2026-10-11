"""宠物宝 (PetCare) — AI 用量配额（滑窗计数，按用户 / 按IP）

背景：AI 端点可匿名调用（保留游客体验），但火山方舟按 token 计费，
必须防止匿名刷量。策略：登录用户按 user_id 配额，匿名按客户端 IP 配额。
单进程部署（uvicorn workers=1）下内存计数即可；多进程时退化为每进程独立计数（保守可接受）。
"""
import os
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import Depends, HTTPException, Request

from app.auth import get_current_user

# 24 小时滑窗上限
AI_DAILY_LIMIT_USER = int(os.getenv("AI_DAILY_LIMIT_USER", "100"))
AI_DAILY_LIMIT_IP = int(os.getenv("AI_DAILY_LIMIT_IP", "20"))

_lock = Lock()
_counters: dict[str, deque] = defaultdict(deque)  # key -> 调用时间戳队列


def _check_and_record(key: str, limit: int) -> None:
    now = time.time()
    with _lock:
        q = _counters[key]
        cutoff = now - 86400
        while q and q[0] < cutoff:
            q.popleft()
        if len(q) >= limit:
            raise HTTPException(429, "AI 用量已达上限，请稍后再试或登录解锁更多")
        q.append(now)


def client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def require_ai_quota(request: Request, user=Depends(get_current_user)):
    """FastAPI 依赖：登录用户按 user_id 计配额，匿名按 IP 计配额。"""
    if user is not None:
        _check_and_record(f"u:{user.id}", AI_DAILY_LIMIT_USER)
    else:
        _check_and_record(f"ip:{client_ip(request)}", AI_DAILY_LIMIT_IP)
    return user
