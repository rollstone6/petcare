"""爬虫基类 — 通用请求、重试、限速、日志"""
import asyncio
import random
import time
import logging
import httpx
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger("crawler")


class BaseCrawler(ABC):
    """爬虫基类"""

    # 常见桌面 UA 池
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    ]

    # 移动端 UA（用于 H5 API）
    MOBILE_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"

    def __init__(self, request_delay: float = 2.0, max_retries: int = 3):
        self.request_delay = request_delay
        self.max_retries = max_retries
        self._client: Optional[httpx.AsyncClient] = None
        self._last_request_time = 0.0

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            limits=httpx.Limits(max_connections=5, max_keepalive_connections=3),
        )
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    def _random_ua(self, mobile: bool = False) -> str:
        if mobile:
            return self.MOBILE_UA
        return random.choice(self.USER_AGENTS)

    async def _rate_limit(self):
        """限速：确保两次请求之间至少有 request_delay 秒间隔"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_delay:
            wait = self.request_delay - elapsed + random.uniform(0, 1.0)
            await asyncio.sleep(wait)
        self._last_request_time = time.time()

    async def fetch(
        self,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        mobile: bool = False,
        referer: Optional[str] = None,
    ) -> Optional[httpx.Response]:
        """带重试和限速的 GET 请求"""
        if headers is None:
            headers = {}

        headers.setdefault("User-Agent", self._random_ua(mobile))
        headers.setdefault("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
        headers.setdefault("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8")
        if referer:
            headers["Referer"] = referer

        for attempt in range(self.max_retries):
            try:
                await self._rate_limit()
                resp = await self._client.get(url, headers=headers, params=params)

                if resp.status_code == 200:
                    return resp
                elif resp.status_code == 403:
                    logger.warning(f"[{self.__class__.__name__}] 403 被拦截, url={url}, attempt={attempt+1}")
                    await asyncio.sleep(random.uniform(5, 15))
                elif resp.status_code == 429:
                    logger.warning(f"[{self.__class__.__name__}] 429 限速, url={url}, attempt={attempt+1}")
                    await asyncio.sleep(random.uniform(10, 30))
                else:
                    logger.warning(f"[{self.__class__.__name__}] HTTP {resp.status_code}, url={url}")
                    await asyncio.sleep(random.uniform(2, 5))

            except httpx.TimeoutException:
                logger.warning(f"[{self.__class__.__name__}] 请求超时, url={url}, attempt={attempt+1}")
                await asyncio.sleep(random.uniform(3, 8))
            except Exception as e:
                logger.error(f"[{self.__class__.__name__}] 请求异常: {e}, url={url}")
                await asyncio.sleep(random.uniform(2, 5))

        logger.error(f"[{self.__class__.__name__}] 请求失败（已重试{self.max_retries}次）: {url}")
        return None

    async def fetch_json(
        self,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        mobile: bool = False,
    ) -> Optional[dict]:
        """GET 请求并解析 JSON"""
        if headers is None:
            headers = {}
        headers["Accept"] = "application/json"

        resp = await self.fetch(url, headers=headers, params=params, mobile=mobile)
        if resp:
            try:
                return resp.json()
            except Exception as e:
                logger.error(f"[{self.__class__.__name__}] JSON 解析失败: {e}")
        return None

    @abstractmethod
    async def search_products(self, keyword: str, max_pages: int = 3) -> list[dict]:
        """搜索产品，返回产品列表（原始数据）"""
        ...

    @abstractmethod
    async def get_product_detail(self, product_id: str) -> Optional[dict]:
        """获取产品详情"""
        ...

    @abstractmethod
    def get_source_name(self) -> str:
        """数据源名称"""
        ...
