import json
from datetime import datetime
from app import db
from app.models.crawl_task import CrawlTask
from app.models.product import Product
from app.models.review import Review


class CrawlService:

    @staticmethod
    def run_task(task_id, use_scrapy=False):
        from flask import current_app
        task = CrawlTask.query.get(task_id)
        if not task:
            return

        try:
            if use_scrapy and task.target_url:
                count = CrawlService._scrapy_crawl(task)
            elif task.target_url:
                count = CrawlService._requests_crawl(task)
            else:
                count = CrawlService._simulate_crawl(task)
            task.status = 'completed'
            task.success_count = count
            task.total_count = count
            task.finished_at = datetime.utcnow()
        except Exception as e:
            task.status = 'failed'
            task.error_msg = str(e)
            task.finished_at = datetime.utcnow()

        db.session.commit()

    @staticmethod
    def _scrapy_crawl(task):
        """使用 Scrapy 框架爬取评论"""
        from crawler.jd_spider import JDReviewSpider
        spider = JDReviewSpider()
        import re
        product_id_match = re.search(r'(\d{5,})', task.target_url or '')
        if not product_id_match:
            raise Exception('无法从URL中解析商品ID')

        jd_product_id = product_id_match.group(1)
        raw_reviews = spider.crawl_reviews(jd_product_id, max_pages=5)
        return CrawlService._save_reviews(task, raw_reviews)

    @staticmethod
    def _requests_crawl(task):
        """使用 requests 爬取评论"""
        from crawler.jd_spider import JDReviewSpider
        spider = JDReviewSpider()
        import re
        product_id_match = re.search(r'(\d{5,})', task.target_url or '')
        if not product_id_match:
            raise Exception('无法从URL中解析商品ID')

        jd_product_id = product_id_match.group(1)
        raw_reviews = spider.crawl_reviews(jd_product_id, max_pages=5)
        return CrawlService._save_reviews(task, raw_reviews)

    @staticmethod
    def _save_reviews(task, raw_reviews):
        """将爬取的评论保存到数据库"""
        if not raw_reviews:
            raise Exception('未爬取到任何评论')

        product_name = raw_reviews[0].get('product_name', task.keyword)
        product = Product(
            name=product_name or f'{task.keyword} - 商品',
            category='其他',
            source_platform=task.platform,
            review_count=len(raw_reviews),
        )
        db.session.add(product)
        db.session.flush()

        for r in raw_reviews:
            review = Review(
                product_id=product.id,
                content=r['content'],
                rating=r.get('rating', 5),
                reviewer_name=r.get('reviewer_name', '匿名用户'),
                source_platform=task.platform,
            )
            db.session.add(review)

        return len(raw_reviews)

    @staticmethod
    def _simulate_crawl(task):
        """使用预置示例数据模拟爬取"""
        SAMPLE_PRODUCTS = {
            '手机': {
                'name': f'华为Mate 60 Pro - {task.keyword}',
                'category': '手机数码',
                'brand': '华为',
                'price': 6999.00,
                'image_url': '',
            },
            '笔记本': {
                'name': f'联想ThinkPad X1 Carbon - {task.keyword}',
                'category': '电脑办公',
                'brand': '联想',
                'price': 9999.00,
                'image_url': '',
            },
        }

        SAMPLE_REVIEWS = [
            {'content': '手机很不错，拍照效果非常好，系统流畅，电池续航也很给力', 'rating': 5, 'reviewer': '数码爱好者'},
            {'content': '屏幕显示效果出色，色彩还原准确，看视频追剧体验很棒', 'rating': 5, 'reviewer': '影音发烧友'},
            {'content': '做工精细，手感温润，颜值在线，朋友们都说好看', 'rating': 4, 'reviewer': '时尚达人'},
            {'content': '收到货了，包装完整，物流很快，第二天就到了', 'rating': 5, 'reviewer': '网购达人'},
            {'content': '性价比很高，功能齐全，满足日常使用需求', 'rating': 4, 'reviewer': '理性消费者'},
            {'content': '质量一般，用了一周就出现卡顿现象，有点失望', 'rating': 2, 'reviewer': '普通用户小王'},
            {'content': '发热比较严重，玩游戏的时候特别明显，希望能改进', 'rating': 3, 'reviewer': '游戏玩家'},
            {'content': '客服态度非常好，耐心解答了我的各种问题', 'rating': 5, 'reviewer': '新手用户'},
            {'content': '价格有点贵，同配置的其他品牌便宜不少', 'rating': 3, 'reviewer': '价格敏感型'},
            {'content': '整体满意，就是充电速度比宣传的慢一些', 'rating': 4, 'reviewer': '实事求是者'},
        ]

        product_template = SAMPLE_PRODUCTS.get('手机', list(SAMPLE_PRODUCTS.values())[0])
        product = Product(
            name=product_template['name'],
            category=product_template['category'],
            brand=product_template['brand'],
            price=product_template['price'],
            image_url=product_template['image_url'],
            source_platform=task.platform,
            review_count=len(SAMPLE_REVIEWS),
        )
        db.session.add(product)
        db.session.flush()

        for r in SAMPLE_REVIEWS:
            review = Review(
                product_id=product.id,
                content=r['content'],
                rating=r['rating'],
                reviewer_name=r['reviewer'],
                source_platform=task.platform,
            )
            db.session.add(review)

        return len(SAMPLE_REVIEWS)
