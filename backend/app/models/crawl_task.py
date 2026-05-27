from app import db
from datetime import datetime


class CrawlTask(db.Model):
    __tablename__ = 'crawl_tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_name = db.Column(db.String(200), nullable=False)
    platform = db.Column(db.String(50), default='京东')
    keyword = db.Column(db.String(200), default='')
    target_url = db.Column(db.String(500), default='')
    status = db.Column(db.String(20), default='pending')  # pending / running / completed / failed
    total_count = db.Column(db.Integer, default=0)
    success_count = db.Column(db.Integer, default=0)
    fail_count = db.Column(db.Integer, default=0)
    error_msg = db.Column(db.Text, default='')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    started_at = db.Column(db.DateTime, default=None)
    finished_at = db.Column(db.DateTime, default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    creator = db.relationship('User', backref='crawl_tasks')

    def to_dict(self):
        return {
            'id': self.id,
            'task_name': self.task_name,
            'platform': self.platform,
            'keyword': self.keyword,
            'target_url': self.target_url,
            'status': self.status,
            'total_count': self.total_count,
            'success_count': self.success_count,
            'fail_count': self.fail_count,
            'error_msg': self.error_msg,
            'created_by': self.created_by,
            'creator_name': self.creator.username if self.creator else '',
            'started_at': self.started_at.strftime('%Y-%m-%d %H:%M:%S') if self.started_at else None,
            'finished_at': self.finished_at.strftime('%Y-%m-%d %H:%M:%S') if self.finished_at else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
