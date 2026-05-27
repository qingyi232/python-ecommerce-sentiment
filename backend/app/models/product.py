from app import db
from datetime import datetime


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, default='其他')
    brand = db.Column(db.String(100), default='')
    price = db.Column(db.Numeric(10, 2), default=0)
    image_url = db.Column(db.String(500), default='')
    source_url = db.Column(db.String(500), default='')
    source_platform = db.Column(db.String(50), default='京东')
    source_id = db.Column(db.String(100), default='')
    review_count = db.Column(db.Integer, default=0)
    avg_sentiment = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text, default='')
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reviews = db.relationship('Review', backref='product', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'brand': self.brand,
            'price': float(self.price) if self.price else 0,
            'image_url': self.image_url,
            'source_url': self.source_url,
            'source_platform': self.source_platform,
            'source_id': self.source_id,
            'review_count': self.review_count,
            'avg_sentiment': round(self.avg_sentiment, 2) if self.avg_sentiment else 0,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
