from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    CORS(app, supports_credentials=True)
    db.init_app(app)
    jwt.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.review import review_bp
    from app.routes.analysis import analysis_bp
    from app.routes.crawl import crawl_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.user import user_bp
    from app.routes.upload import upload_bp
    from app.routes.visualization import visualization_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(review_bp, url_prefix='/api/reviews')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(crawl_bp, url_prefix='/api/crawl')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(visualization_bp, url_prefix='/api/visualization')

    with app.app_context():
        db.create_all()

    return app
