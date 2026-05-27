from app import db
from datetime import datetime


class SentimentResult(db.Model):
    __tablename__ = 'sentiment_results'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    total_reviews = db.Column(db.Integer, default=0)
    positive_count = db.Column(db.Integer, default=0)
    negative_count = db.Column(db.Integer, default=0)
    neutral_count = db.Column(db.Integer, default=0)
    avg_score = db.Column(db.Float, default=0.0)
    positive_ratio = db.Column(db.Float, default=0.0)
    negative_ratio = db.Column(db.Float, default=0.0)
    neutral_ratio = db.Column(db.Float, default=0.0)
    top_positive_words = db.Column(db.Text, default='')
    top_negative_words = db.Column(db.Text, default='')
    algorithm = db.Column(db.String(50), default='snownlp')  # snownlp / bert
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref='sentiment_results')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else '',
            'total_reviews': self.total_reviews,
            'positive_count': self.positive_count,
            'negative_count': self.negative_count,
            'neutral_count': self.neutral_count,
            'avg_score': round(self.avg_score, 4),
            'positive_ratio': round(self.positive_ratio, 2),
            'negative_ratio': round(self.negative_ratio, 2),
            'neutral_ratio': round(self.neutral_ratio, 2),
            'top_positive_words': self.top_positive_words,
            'top_negative_words': self.top_negative_words,
            'algorithm': self.algorithm,
            'analyzed_at': self.analyzed_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
