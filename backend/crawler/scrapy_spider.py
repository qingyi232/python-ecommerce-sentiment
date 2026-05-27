"""
基于 Scrapy 框架的京东商品评论爬虫
按照开题报告要求使用 Scrapy 框架实现数据爬取
"""
import json
import re
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class JDReviewScrapySpider(scrapy.Spider):
    """京东商品评论 Scrapy 爬虫"""
    name = 'jd_reviews'
    allowed_domains = ['club.jd.com', 'jd.com']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
        'COOKIES_ENABLED': False,
        'LOG_LEVEL': 'INFO',
        'RETRY_TIMES': 3,
    }

    def __init__(self, product_id=None, max_pages=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_id = product_id
        self.max_pages = int(max_pages) if max_pages else 10
        self.reviews = []

    def start_requests(self):
        if not self.product_id:
            self.logger.error('未指定商品ID')
            return

        for page in range(self.max_pages):
            url = (
                f'https://club.jd.com/comment/productPageComments.action'
                f'?callback=fetchJSON_comment98'
                f'&productId={self.product_id}'
                f'&score=0&sortType=5&page={page}&pageSize=10'
                f'&isShadowSku=0&fold=1'
            )
            yield scrapy.Request(
                url=url,
                callback=self.parse_comments,
                headers={
                    'Referer': f'https://item.jd.com/{self.product_id}.html',
                    'Accept': 'application/json, text/javascript, */*',
                },
                meta={'page': page},
            )

    def parse_comments(self, response):
        text = response.text
        json_match = re.search(r'fetchJSON_comment98\((.*)\);', text)
        if not json_match:
            return

        try:
            data = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            return

        comments = data.get('comments', [])
        if not comments:
            return

        for comment in comments:
            review = {
                'content': comment.get('content', ''),
                'rating': comment.get('score', 5),
                'reviewer_name': comment.get('nickname', '匿名用户'),
                'review_time': comment.get('creationTime', ''),
                'product_name': comment.get('referenceName', ''),
            }
            self.reviews.append(review)
            yield review

    def closed(self, reason):
        self.logger.info(f'爬取完成，共获取 {len(self.reviews)} 条评论')


def run_scrapy_spider(product_id, max_pages=10):
    """运行 Scrapy 爬虫并返回结果"""
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'LOG_LEVEL': 'WARNING',
    })

    reviews = []

    class CollectorPipeline:
        def process_item(self, item, spider):
            reviews.append(item)
            return item

    process.crawl(
        JDReviewScrapySpider,
        product_id=product_id,
        max_pages=max_pages,
    )

    try:
        process.start()
    except Exception as e:
        print(f'Scrapy 爬虫执行异常: {e}')

    return reviews
