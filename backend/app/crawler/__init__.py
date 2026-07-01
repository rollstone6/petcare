"""宠物宝爬虫模块 — 从京东/淘宝抓取真实产品数据"""
from app.crawler.base import BaseCrawler
from app.crawler.jd_crawler import JDCrawler
from app.crawler.taobao_crawler import TaobaoCrawler
from app.crawler.processor import DataProcessor
