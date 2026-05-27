"""初始化数据库并插入示例数据"""
import json
import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.product import Product
from app.models.review import Review
from app.models.sentiment import SentimentResult
from app.models.demand import DemandTopic, DemandKeyword
from app.models.crawl_task import CrawlTask


def init_database():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        print('数据库表已创建')

        create_users()
        create_products()
        create_reviews()
        create_crawl_tasks()

        print('示例数据初始化完成！（请在前端手动执行情感分析和需求挖掘）')


def create_users():
    users = [
        {'username': 'admin', 'password': 'admin123', 'email': 'admin@example.com', 'role': 'admin', 'nickname': '系统管理员'},
        {'username': 'merchant1', 'password': '123456', 'email': 'merchant1@example.com', 'role': 'merchant', 'nickname': '华为官方旗舰店'},
        {'username': 'merchant2', 'password': '123456', 'email': 'merchant2@example.com', 'role': 'merchant', 'nickname': '苹果授权专卖店'},
        {'username': 'user1', 'password': '123456', 'email': 'user1@example.com', 'role': 'user', 'nickname': '数码爱好者小李'},
        {'username': 'user2', 'password': '123456', 'email': 'user2@example.com', 'role': 'user', 'nickname': '购物达人小张'},
    ]
    for u in users:
        user = User(username=u['username'], email=u['email'], role=u['role'], nickname=u['nickname'])
        user.set_password(u['password'])
        db.session.add(user)
    db.session.commit()
    print(f'已创建 {len(users)} 个用户')


def create_products():
    products = [
        {
            'name': '华为Mate 60 Pro 昆仑玻璃版',
            'category': '手机数码',
            'brand': '华为',
            'price': 6999.00,
            'image_url': '',
            'source_platform': '京东',
            'description': '麒麟9000S芯片，超可靠玄武架构，XMAGE影像系统，卫星通信',
        },
        {
            'name': 'iPhone 15 Pro Max 256GB',
            'category': '手机数码',
            'brand': '苹果',
            'price': 9999.00,
            'image_url': '',
            'source_platform': '京东',
            'description': 'A17 Pro芯片，钛金属设计，4800万像素主摄，USB-C接口',
        },
        {
            'name': '小米14 Ultra 影像旗舰',
            'category': '手机数码',
            'brand': '小米',
            'price': 5999.00,
            'image_url': '',
            'source_platform': '京东',
            'description': '骁龙8 Gen3，徕卡光学Summilux镜头，1英寸大底主摄',
        },
        {
            'name': '联想ThinkPad X1 Carbon 2024',
            'category': '电脑办公',
            'brand': '联想',
            'price': 12999.00,
            'image_url': '',
            'source_platform': '京东',
            'description': 'Intel Ultra 7处理器，14英寸2.8K OLED屏，32GB内存',
        },
        {
            'name': 'MacBook Pro 14英寸 M3 Pro',
            'category': '电脑办公',
            'brand': '苹果',
            'price': 16999.00,
            'image_url': '',
            'source_platform': '京东',
            'description': 'M3 Pro芯片，18GB统一内存，Liquid Retina XDR显示屏',
        },
        {
            'name': '索尼WH-1000XM5头戴式降噪耳机',
            'category': '影音设备',
            'brand': '索尼',
            'price': 2499.00,
            'image_url': '',
            'source_platform': '京东',
            'description': '行业领先降噪，30小时续航，自适应声音控制',
        },
        {
            'name': '戴森V15 Detect无绳吸尘器',
            'category': '生活电器',
            'brand': '戴森',
            'price': 4990.00,
            'image_url': '',
            'source_platform': '京东',
            'description': '激光探测微尘，压电式传感器，240AW强劲吸力',
        },
        {
            'name': '海尔BCD-510WDPZ冰箱',
            'category': '大家电',
            'brand': '海尔',
            'price': 3999.00,
            'image_url': '',
            'source_platform': '京东',
            'description': '510升大容量，风冷无霜，一级能效，智能变频压缩机',
        },
    ]

    for p in products:
        product = Product(**p)
        db.session.add(product)
    db.session.commit()
    print(f'已创建 {len(products)} 个商品')


def create_reviews():
    REVIEW_TEMPLATES = {
        '手机数码': {
            'positive': [
                '手机非常好用，系统流畅，拍照效果出色，值得购买！',
                '屏幕显示效果非常棒，色彩鲜艳，看视频很享受',
                '电池续航给力，一天重度使用还能剩下不少电量',
                '做工精致，手感特别好，颜值很高，爱了',
                '信号特别稳定，通话质量清晰，网速快',
                '拍照真的太强了，夜景模式简直绝了',
                '充电速度快得离谱，半小时就能充满',
                '系统功能丰富，操作流畅不卡顿，体验很好',
                '性价比超高，这个价格能买到这个配置太值了',
                '外放音质不错，低音有力，听歌很棒',
                '人脸识别速度非常快，安全又方便',
                '游戏性能强悍，大型游戏全开高画质毫无压力',
            ],
            'negative': [
                '手机用了没几天就开始卡了，很失望',
                '发热问题严重，玩一会儿游戏烫得不行',
                '拍照效果一般，跟宣传差距太大了',
                '信号不太好，偶尔会断网，影响使用',
                '电池不耐用，半天就没电了，需要随身带充电宝',
                '系统广告太多了，推送通知根本关不掉',
            ],
            'neutral': [
                '整体还行吧，没有特别惊艳也没什么大问题',
                '价格偏贵了一些，不过质量确实不错',
                '功能中规中矩，能满足基本使用需求',
                '包装一般，手机本身还可以',
            ],
        },
        '电脑办公': {
            'positive': [
                '性能非常强大，编程开发效率大幅提升',
                '屏幕素质很高，色彩准确，适合设计工作',
                '键盘手感极佳，打字很舒服，长时间办公不累',
                '轻薄便携，出差携带非常方便',
                '散热效果好，长时间高负载运行也不会太热',
                '做工精致，商务范十足，开会拿出来很有面子',
                '多任务处理能力强，同时开很多软件也不卡',
                '接口丰富，满足各种外设连接需求',
            ],
            'negative': [
                '风扇声音有点大，安静环境下比较明显',
                '价格偏高，同配置其他品牌便宜不少',
                '内存焊死不能升级，后期扩展性差',
                '触控板偶尔有误触的情况',
            ],
            'neutral': [
                '中规中矩的商务本，没有特别突出的地方',
                '续航一般，出门还是得带充电器',
            ],
        },
        '影音设备': {
            'positive': [
                '降噪效果非常好，戴上瞬间安静，通勤必备',
                '音质出色，低音浑厚，高音通透，听感舒适',
                '佩戴舒适，耳罩柔软，长时间戴也不夹头',
                '续航给力，充一次电能用好几天',
                '连接稳定，切换设备很方便，多设备用户福音',
                '通话质量清晰，对方听得很清楚',
            ],
            'negative': [
                '价格偏贵，性价比一般',
                '夏天戴着有点闷热，不太透气',
            ],
            'neutral': [
                '整体不错，但跟上一代相比提升不大',
            ],
        },
        '生活电器': {
            'positive': [
                '吸力非常强劲，地上的灰尘毛发一扫而光',
                '激光探测功能很实用，能看到肉眼看不到的灰尘',
                '噪音比想象中小，不会打扰到家人休息',
                '续航还不错，打扫全屋足够用',
                '拆卸清洗方便，维护简单省心',
            ],
            'negative': [
                '价格真的太贵了，普通家庭有点吃不消',
                '机身稍微有点重，长时间使用手臂酸',
            ],
            'neutral': [
                '功能够用，但跟同价位竞品相比优势不明显',
            ],
        },
        '大家电': {
            'positive': [
                '冰箱容量大，全家人的食材都能放下',
                '运行安静，几乎听不到声音，不影响休息',
                '节能效果好，一天耗电量很少',
                '保鲜效果出色，蔬菜水果放几天还是新鲜的',
                '外观大气美观，跟家里装修风格很搭',
                '制冷均匀，每一层温度都很稳定',
            ],
            'negative': [
                '送货安装服务态度一般，师傅有点敷衍',
                '门缝偶尔有凝露现象，需要擦拭',
            ],
            'neutral': [
                '中规中矩的冰箱，该有的功能都有',
            ],
        },
    }

    products = Product.query.all()
    total = 0
    for product in products:
        templates = REVIEW_TEMPLATES.get(product.category, REVIEW_TEMPLATES['手机数码'])
        all_reviews = []

        for content in templates['positive']:
            all_reviews.append((content, random.randint(4, 5), 'positive'))
        for content in templates['negative']:
            all_reviews.append((content, random.randint(1, 3), 'negative'))
        for content in templates['neutral']:
            all_reviews.append((content, 3, 'neutral'))

        reviewers = ['小明', '小红', '大伟', '小芳', '阿杰', '婷婷', '浩然', '思思',
                     '老张', '小刘', '王哥', '李姐', '赵大叔', '小陈', '周同学']

        for content, rating, _ in all_reviews:
            days_ago = random.randint(1, 90)
            review = Review(
                product_id=product.id,
                content=content,
                rating=rating,
                reviewer_name=random.choice(reviewers),
                review_time=datetime.utcnow() - timedelta(days=days_ago),
                source_platform='京东',
            )
            db.session.add(review)
            total += 1

        product.review_count = len(all_reviews)

    db.session.commit()
    print(f'已创建 {total} 条评论')


def create_crawl_tasks():
    tasks = [
        {'task_name': '华为手机评论采集', 'keyword': '华为Mate60', 'status': 'completed',
         'total_count': 150, 'success_count': 148, 'fail_count': 2, 'created_by': 1},
        {'task_name': 'iPhone评论采集', 'keyword': 'iPhone15Pro', 'status': 'completed',
         'total_count': 200, 'success_count': 195, 'fail_count': 5, 'created_by': 1},
        {'task_name': '笔记本电脑评论采集', 'keyword': 'ThinkPad笔记本', 'status': 'completed',
         'total_count': 120, 'success_count': 118, 'fail_count': 2, 'created_by': 1},
        {'task_name': '耳机评论采集', 'keyword': '索尼降噪耳机', 'status': 'pending',
         'total_count': 0, 'success_count': 0, 'fail_count': 0, 'created_by': 1},
    ]
    for t in tasks:
        task = CrawlTask(**t)
        if t['status'] == 'completed':
            task.started_at = datetime.utcnow() - timedelta(hours=2)
            task.finished_at = datetime.utcnow() - timedelta(hours=1)
        db.session.add(task)
    db.session.commit()
    print(f'已创建 {len(tasks)} 个爬取任务')


def run_analysis():
    from app.services.sentiment_service import SentimentService
    products = Product.query.all()
    for product in products:
        reviews = Review.query.filter_by(product_id=product.id).all()
        if reviews:
            SentimentService.analyze(product.id, reviews, 'snownlp')
    print('已完成情感分析')

    from app.services.demand_service import DemandService
    for product in products:
        reviews = Review.query.filter_by(product_id=product.id).all()
        if len(reviews) >= 5:
            try:
                DemandService.analyze(product.id, reviews, 5)
            except Exception as e:
                print(f'商品 {product.name} LDA分析失败: {e}')
    print('已完成需求挖掘')


if __name__ == '__main__':
    init_database()
    app = create_app()
    with app.app_context():
        run_analysis()
