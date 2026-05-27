from flask import Blueprint
from flask_jwt_extended import jwt_required
from app import db
from app.models.user import User
from app.models.product import Product
from app.models.review import Review
from app.models.sentiment import SentimentResult
from app.models.crawl_task import CrawlTask
from app.utils.response import success

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    total_users = User.query.count()
    total_products = Product.query.count()
    total_reviews = Review.query.count()
    analyzed_reviews = Review.query.filter_by(is_analyzed=True).count()
    total_tasks = CrawlTask.query.count()
    completed_tasks = CrawlTask.query.filter_by(status='completed').count()

    positive_reviews = Review.query.filter_by(sentiment_label='positive').count()
    negative_reviews = Review.query.filter_by(sentiment_label='negative').count()
    neutral_reviews = Review.query.filter_by(sentiment_label='neutral').count()

    return success(data={
        'total_users': total_users,
        'total_products': total_products,
        'total_reviews': total_reviews,
        'analyzed_reviews': analyzed_reviews,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'sentiment_distribution': {
            'positive': positive_reviews,
            'negative': negative_reviews,
            'neutral': neutral_reviews,
        },
        'analysis_rate': round(analyzed_reviews / total_reviews * 100, 1) if total_reviews > 0 else 0,
    })


@dashboard_bp.route('/recent-reviews', methods=['GET'])
@jwt_required()
def get_recent_reviews():
    reviews = Review.query.order_by(Review.created_at.desc()).limit(10).all()
    return success(data=[r.to_dict() for r in reviews])


@dashboard_bp.route('/top-products', methods=['GET'])
@jwt_required()
def get_top_products():
    products = Product.query.order_by(Product.review_count.desc()).limit(10).all()
    result = []
    for p in products:
        sentiment = SentimentResult.query.filter_by(product_id=p.id).order_by(
            SentimentResult.analyzed_at.desc()
        ).first()
        result.append({
            'product': p.to_dict(),
            'sentiment': sentiment.to_dict() if sentiment else None,
        })
    return success(data=result)


@dashboard_bp.route('/category-stats', methods=['GET'])
@jwt_required()
def get_category_stats():
    categories = db.session.query(
        Product.category,
        db.func.count(Product.id).label('product_count'),
        db.func.sum(Product.review_count).label('review_count'),
        db.func.avg(Product.avg_sentiment).label('avg_sentiment'),
    ).group_by(Product.category).all()

    return success(data=[{
        'category': c.category,
        'product_count': c.product_count,
        'review_count': int(c.review_count or 0),
        'avg_sentiment': round(float(c.avg_sentiment or 0), 2),
    } for c in categories])


@dashboard_bp.route('/sentiment-trend', methods=['GET'])
@jwt_required()
def get_sentiment_trend():
    results = db.session.query(
        db.func.date(Review.created_at).label('date'),
        db.func.count(Review.id).label('total'),
        db.func.sum(db.case((Review.sentiment_label == 'positive', 1), else_=0)).label('positive'),
        db.func.sum(db.case((Review.sentiment_label == 'negative', 1), else_=0)).label('negative'),
        db.func.sum(db.case((Review.sentiment_label == 'neutral', 1), else_=0)).label('neutral'),
    ).filter(
        Review.is_analyzed == True
    ).group_by(
        db.func.date(Review.created_at)
    ).order_by(
        db.func.date(Review.created_at)
    ).limit(30).all()

    return success(data=[{
        'date': str(r.date),
        'total': r.total,
        'positive': int(r.positive or 0),
        'negative': int(r.negative or 0),
        'neutral': int(r.neutral or 0),
    } for r in results])
