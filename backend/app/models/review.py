from app import db
from datetime import datetime


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    cleaned_content = db.Column(db.Text, default='')
    rating = db.Column(db.Integer, default=5)  # 1-5
    reviewer_name = db.Column(db.String(100), default='匿名用户')
    review_time = db.Column(db.DateTime, default=datetime.utcnow)
    source_platform = db.Column(db.String(50), default='京东')
    sentiment_score = db.Column(db.Float, default=None)
    sentiment_label = db.Column(db.String(20), default=None)  # positive / negative / neutral
    is_analyzed = db.Column(db.Boolean, default=False)
    keywords = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else '',
            'content': self.content,
            'cleaned_content': self.cleaned_content,
            'rating': self.rating,
            'reviewer_name': self.reviewer_name,
            'review_time': self.review_time.strftime('%Y-%m-%d %H:%M:%S') if self.review_time else '',
            'source_platform': self.source_platform,
            'sentiment_score': round(self.sentiment_score, 4) if self.sentiment_score is not None else None,
            'sentiment_label': self.sentiment_label,
            'is_analyzed': self.is_analyzed,
            'keywords': self.keywords,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
