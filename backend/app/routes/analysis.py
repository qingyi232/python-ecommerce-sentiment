from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app import db
from app.models.review import Review
from app.models.product import Product
from app.models.sentiment import SentimentResult
from app.models.demand import DemandTopic, DemandKeyword
from app.services.sentiment_service import SentimentService
from app.services.demand_service import DemandService
from app.utils.response import success, error

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/sentiment/run', methods=['POST'])
@jwt_required()
def run_sentiment():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    algorithm = data.get('algorithm', 'snownlp')

    if not product_id:
        return error('请指定商品ID', 400)

    product = Product.query.get(product_id)
    if not product:
        return error('商品不存在', 404)

    reviews = Review.query.filter_by(product_id=product_id).all()
    if not reviews:
        return error('该商品暂无评论数据', 400)

    result = SentimentService.analyze(product_id, reviews, algorithm)
    return success(data=result, message='情感分析完成')


@analysis_bp.route('/sentiment/results', methods=['GET'])
@jwt_required()
def get_sentiment_results():
    product_id = request.args.get('product_id', type=int)
    query = SentimentResult.query
    if product_id:
        query = query.filter_by(product_id=product_id)
    query = query.order_by(SentimentResult.analyzed_at.desc())
    results = query.all()
    return success(data=[r.to_dict() for r in results])


@analysis_bp.route('/sentiment/detail/<int:product_id>', methods=['GET'])
@jwt_required()
def get_sentiment_detail(product_id):
    result = SentimentResult.query.filter_by(product_id=product_id).order_by(
        SentimentResult.analyzed_at.desc()
    ).first()
    if not result:
        return error('暂无分析结果', 404)

    reviews = Review.query.filter_by(product_id=product_id, is_analyzed=True).all()
    review_sentiments = []
    for r in reviews:
        review_sentiments.append({
            'id': r.id,
            'content': r.content[:100],
            'sentiment_score': r.sentiment_score,
            'sentiment_label': r.sentiment_label,
            'rating': r.rating,
        })

    return success(data={
        'summary': result.to_dict(),
        'reviews': review_sentiments,
    })


@analysis_bp.route('/demand/run', methods=['POST'])
@jwt_required()
def run_demand():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    num_topics = data.get('num_topics', 5)

    if not product_id:
        return error('请指定商品ID', 400)

    product = Product.query.get(product_id)
    if not product:
        return error('商品不存在', 404)

    reviews = Review.query.filter_by(product_id=product_id).all()
    if len(reviews) < 5:
        return error('评论数据不足，至少需要5条评论', 400)

    result = DemandService.analyze(product_id, reviews, num_topics)
    return success(data=result, message='需求挖掘完成')


@analysis_bp.route('/demand/results', methods=['GET'])
@jwt_required()
def get_demand_results():
    product_id = request.args.get('product_id', type=int)
    if not product_id:
        return error('请指定商品ID', 400)

    topics = DemandTopic.query.filter_by(product_id=product_id).order_by(
        DemandTopic.weight.desc()
    ).all()
    keywords = DemandKeyword.query.filter_by(product_id=product_id).order_by(
        DemandKeyword.frequency.desc()
    ).limit(50).all()

    return success(data={
        'topics': [t.to_dict() for t in topics],
        'keywords': [k.to_dict() for k in keywords],
    })


@analysis_bp.route('/comparison', methods=['GET'])
@jwt_required()
def get_comparison():
    product_ids = request.args.get('product_ids', '')
    if not product_ids:
        return error('请指定商品ID列表', 400)

    ids = [int(x) for x in product_ids.split(',') if x.strip().isdigit()]
    results = []
    for pid in ids:
        product = Product.query.get(pid)
        sentiment = SentimentResult.query.filter_by(product_id=pid).order_by(
            SentimentResult.analyzed_at.desc()
        ).first()
        if product and sentiment:
            results.append({
                'product': product.to_dict(),
                'sentiment': sentiment.to_dict(),
            })

    return success(data=results)
