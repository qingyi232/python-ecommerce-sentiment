"""
京东商品评论爬虫模块
使用 Scrapy 框架实现评论数据采集
"""
import json
import re
import time
import random
import requests
from fake_useragent import UserAgent


class JDReviewSpider:
    """京东商品评论爬虫"""

    BASE_URL = 'https://club.jd.com/comment/productPageComments.action'

    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.headers = {
            'Referer': 'https://item.jd.com/',
            'Accept': 'application/json, text/javascript, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

    def _get_headers(self):
        headers = self.headers.copy()
        headers['User-Agent'] = self.ua.random
        return headers

    def crawl_reviews(self, product_id, max_pages=10, callback=None):
        """爬取指定商品的评论"""
        all_reviews = []

        for page in range(max_pages):
            try:
                params = {
                    'callback': 'fetchJSON_comment98',
                    'productId': product_id,
                    'score': 0,
                    'sortType': 5,
                    'page': page,
                    'pageSize': 10,
                    'isShadowSku': 0,
                    'fold': 1,
                }

                response = self.session.get(
                    self.BASE_URL,
                    params=params,
                    headers=self._get_headers(),
                    timeout=10,
                )

                text = response.text
                json_str = re.search(r'fetchJSON_comment98\((.*)\);', text)
                if not json_str:
                    break

                data = json.loads(json_str.group(1))
                comments = data.get('comments', [])

                if not comments:
                    break

                for comment in comments:
                    review = {
                        'content': comment.get('content', ''),
                        'rating': comment.get('score', 5),
                        'reviewer_name': comment.get('nickname', '匿名用户'),
                        'review_time': comment.get('creationTime', ''),
                        'product_name': comment.get('referenceName', ''),
                    }
                    all_reviews.append(review)

                if callback:
                    callback(page + 1, len(all_reviews))

                time.sleep(random.uniform(1, 3))

            except Exception as e:
                print(f'爬取第{page + 1}页失败: {e}')
                continue

        return all_reviews

    def search_product(self, keyword, max_results=10):
        """搜索商品"""
        try:
            search_url = 'https://search.jd.com/Search'
            params = {'keyword': keyword, 'enc': 'utf-8'}
            response = self.session.get(
                search_url,
                params=params,
                headers=self._get_headers(),
                timeout=10,
            )

            product_ids = re.findall(r'data-sku="(\d+)"', response.text)
            return product_ids[:max_results]
        except Exception as e:
            print(f'搜索商品失败: {e}')
            return []
