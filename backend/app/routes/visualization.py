import io
import base64
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required
from app import db
from app.models.product import Product
from app.models.review import Review
from app.models.sentiment import SentimentResult
from app.models.demand import DemandKeyword
from app.utils.response import success, error
from wordcloud import WordCloud
from collections import Counter

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

visualization_bp = Blueprint('visualization', __name__)


def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64


@visualization_bp.route('/sentiment-pie/<int:product_id>', methods=['GET'])
@jwt_required()
def sentiment_pie(product_id):
    result = SentimentResult.query.filter_by(product_id=product_id).order_by(
        SentimentResult.analyzed_at.desc()
    ).first()
    if not result:
        return error('暂无分析结果', 404)

    labels = ['正面', '负面', '中性']
    sizes = [result.positive_count, result.negative_count, result.neutral_count]
    colors = ['#52c41a', '#ff4d4f', '#faad14']

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct='%1.1f%%',
        startangle=90, textprops={'fontsize': 14}
    )
    ax.set_title(f'情感分布饼图 (共{result.total_reviews}条评论)', fontsize=16, fontweight='bold')
    plt.tight_layout()

    return success(data={'image': fig_to_base64(fig), 'format': 'png'})


@visualization_bp.route('/sentiment-bar', methods=['GET'])
@jwt_required()
def sentiment_bar():
    results = SentimentResult.query.join(Product).all()
    if not results:
        return error('暂无分析结果', 404)

    names = [r.product.name[:10] for r in results]
    positive = [r.positive_count for r in results]
    negative = [r.negative_count for r in results]
    neutral = [r.neutral_count for r in results]

    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(names))
    width = 0.25
    ax.bar([i - width for i in x], positive, width, label='正面', color='#52c41a')
    ax.bar(x, neutral, width, label='中性', color='#faad14')
    ax.bar([i + width for i in x], negative, width, label='负面', color='#ff4d4f')
    ax.set_xlabel('商品', fontsize=12)
    ax.set_ylabel('评论数', fontsize=12)
    ax.set_title('各商品情感对比柱状图', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha='right', fontsize=10)
    ax.legend(fontsize=12)
    plt.tight_layout()

    return success(data={'image': fig_to_base64(fig), 'format': 'png'})


@visualization_bp.route('/sentiment-trend-chart', methods=['GET'])
@jwt_required()
def sentiment_trend_chart():
    results = db.session.query(
        db.func.date(Review.created_at).label('date'),
        db.func.sum(db.case((Review.sentiment_label == 'positive', 1), else_=0)).label('positive'),
        db.func.sum(db.case((Review.sentiment_label == 'negative', 1), else_=0)).label('negative'),
        db.func.sum(db.case((Review.sentiment_label == 'neutral', 1), else_=0)).label('neutral'),
    ).filter(Review.is_analyzed == True).group_by(
        db.func.date(Review.created_at)
    ).order_by(db.func.date(Review.created_at)).limit(30).all()

    if not results:
        return error('暂无数据', 404)

    dates = [str(r.date) for r in results]
    pos = [int(r.positive or 0) for r in results]
    neg = [int(r.negative or 0) for r in results]
    neu = [int(r.neutral or 0) for r in results]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(dates, pos, 'g-o', label='正面', linewidth=2, markersize=5)
    ax.plot(dates, neg, 'r-s', label='负面', linewidth=2, markersize=5)
    ax.plot(dates, neu, 'y-^', label='中性', linewidth=2, markersize=5)
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('评论数', fontsize=12)
    ax.set_title('情感趋势折线图', fontsize=16, fontweight='bold')
    ax.legend(fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.tight_layout()

    return success(data={'image': fig_to_base64(fig), 'format': 'png'})


@visualization_bp.route('/wordcloud/<int:product_id>', methods=['GET'])
@jwt_required()
def wordcloud_chart(product_id):
    keywords = DemandKeyword.query.filter_by(product_id=product_id).all()
    if not keywords:
        reviews = Review.query.filter_by(product_id=product_id).all()
        if not reviews:
            return error('暂无数据', 404)
        from app.services.text_processor import TextProcessor
        all_words = Counter()
        for r in reviews:
            words = TextProcessor.segment(TextProcessor.clean_text(r.content))
            all_words.update(words)
        word_freq = dict(all_words.most_common(100))
    else:
        word_freq = {k.keyword: k.frequency for k in keywords}

    if not word_freq:
        return error('暂无关键词数据', 404)

    wc = WordCloud(
        font_path='simhei.ttf' if __import__('os').path.exists('simhei.ttf') else None,
        width=800, height=400,
        background_color='white',
        max_words=100,
        colormap='viridis',
    )
    try:
        wc.generate_from_frequencies(word_freq)
    except Exception:
        return error('词云生成失败，可能缺少中文字体', 500)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    ax.set_title('关键词词云图', fontsize=16, fontweight='bold')
    plt.tight_layout()

    return success(data={'image': fig_to_base64(fig), 'format': 'png'})


@visualization_bp.route('/category-pie', methods=['GET'])
@jwt_required()
def category_pie():
    categories = db.session.query(
        Product.category,
        db.func.count(Product.id).label('count'),
    ).group_by(Product.category).all()

    if not categories:
        return error('暂无商品数据', 404)

    labels = [c.category for c in categories]
    sizes = [c.count for c in categories]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
           textprops={'fontsize': 12})
    ax.set_title('商品分类占比饼图', fontsize=16, fontweight='bold')
    plt.tight_layout()

    return success(data={'image': fig_to_base64(fig), 'format': 'png'})
