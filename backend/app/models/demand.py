from app import db
from datetime import datetime


class DemandTopic(db.Model):
    __tablename__ = 'demand_topics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    topic_id = db.Column(db.Integer, nullable=False)
    topic_name = db.Column(db.String(100), default='')
    topic_words = db.Column(db.Text, default='')
    weight = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    sentiment_tendency = db.Column(db.String(20), default='neutral')
    description = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref='demand_topics')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else '',
            'topic_id': self.topic_id,
            'topic_name': self.topic_name,
            'topic_words': self.topic_words,
            'weight': round(self.weight, 4),
            'review_count': self.review_count,
            'sentiment_tendency': self.sentiment_tendency,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }


class DemandKeyword(db.Model):
    __tablename__ = 'demand_keywords'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    keyword = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.Integer, default=1)
    tfidf_score = db.Column(db.Float, default=0.0)
    category = db.Column(db.String(50), default='general')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'keyword': self.keyword,
            'frequency': self.frequency,
            'tfidf_score': round(self.tfidf_score, 4),
            'category': self.category,
        }
