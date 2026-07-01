"""宠物宝爬虫主入口 — 从京东/淘宝抓取真实产品数据"""
import asyncio
import logging
import argparse
import sys
from app.crawler.jd_crawler import JDCrawler
from app.crawler.taobao_crawler import TaobaoCrawler
from app.crawler.processor import DataProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("crawler.main")


async def run_crawler(source: str, keyword: str, max_pages: int = 2, fetch_details: bool = False):
    """运行爬虫并处理数据"""
    logger.info(f"开始爬取: {source} - '{keyword}' (最多{max_pages}页)")

    # 选择爬虫
    if source == "jd":
        crawler_class = JDCrawler
    elif source == "taobao":
        crawler_class = TaobaoCrawler
    else:
        logger.error(f"未知的数据源: {source}")
        return

    # 执行爬取
    async with crawler_class(request_delay=2.0) as crawler:
        products = await crawler.crawl_category(
            keyword=keyword,
            max_pages=max_pages,
            fetch_details=fetch_details,
        )

    logger.info(f"爬取完成: 获取 {len(products)} 个产品")

    # 处理数据
    with DataProcessor() as processor:
        stats = processor.process_batch(products)

    logger.info(f"数据处理完成: {stats}")
    return stats


async def main():
    parser = argparse.ArgumentParser(description="宠物宝产品数据爬虫")
    parser.add_argument("--source", "-s", choices=["jd", "taobao", "all"], default="all",
                        help="数据源: jd(京东), taobao(淘宝), all(全部)")
    parser.add_argument("--keyword", "-k", default="猫粮",
                        help="搜索关键词 (默认: 猫粮)")
    parser.add_argument("--pages", "-p", type=int, default=2,
                        help="每个关键词最多爬取页数 (默认: 2)")
    parser.add_argument("--details", "-d", action="store_true",
                        help="是否获取产品详情（耗时较长）")

    args = parser.parse_args()

    # 搜索关键词列表
    keywords = [
        "猫粮", "狗粮", "猫零食", "狗零食",
        "宠物驱虫", "宠物益生菌", "宠物营养膏",
    ]

    # 如果指定了单个关键词，只爬这个
    if args.keyword != "猫粮" or len(sys.argv) > 2:
        keywords = [args.keyword]

    all_stats = {"total": 0, "added": 0, "skipped": 0, "failed": 0}

    for keyword in keywords:
        sources = [args.source] if args.source != "all" else ["jd", "taobao"]

        for source in sources:
            try:
                stats = await run_crawler(
                    source=source,
                    keyword=keyword,
                    max_pages=args.pages,
                    fetch_details=args.details,
                )
                if stats:
                    for key in all_stats:
                        all_stats[key] += stats.get(key, 0)
            except Exception as e:
                logger.error(f"爬取失败: {source}/{keyword} - {e}")

            # 不同数据源之间休息一下
            await asyncio.sleep(5)

    logger.info("=" * 60)
    logger.info(f"全部完成! 总计: {all_stats}")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
