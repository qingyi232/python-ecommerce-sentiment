from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.review import Review
from app.models.product import Product
from app.utils.response import success, error, paginate_response

review_bp = Blueprint('review', __name__)


@review_bp.route('/', methods=['GET'])
@jwt_required()
def get_reviews():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    product_id = request.args.get('product_id', type=int)
    sentiment = request.args.get('sentiment', '')
    keyword = request.args.get('keyword', '')

    query = Review.query
    if product_id:
        query = query.filter_by(product_id=product_id)
    if sentiment:
        query = query.filter_by(sentiment_label=sentiment)
    if keyword:
        query = query.filter(Review.content.like(f'%{keyword}%'))

    query = query.order_by(Review.created_at.desc())
    return paginate_response(query, page, per_page)


@review_bp.route('/<int:review_id>', methods=['GET'])
@jwt_required()
def get_review(review_id):
    review = Review.query.get(review_id)
    if not review:
        return error('评论不存在', 404)
    return success(data=review.to_dict())


@review_bp.route('/', methods=['POST'])
@jwt_required()
def create_review():
    data = request.get_json()
    if not data:
        return error('请求数据为空', 400)

    product_id = data.get('product_id')
    content = data.get('content', '').strip()

    if not product_id or not content:
        return error('商品ID和评论内容不能为空', 400)

    product = Product.query.get(product_id)
    if not product:
        return error('商品不存在', 404)

    review = Review(
        product_id=product_id,
        content=content,
        rating=data.get('rating', 5),
        reviewer_name=data.get('reviewer_name', '匿名用户'),
        source_platform=data.get('source_platform', '手动录入'),
    )
    db.session.add(review)
    product.review_count = Review.query.filter_by(product_id=product_id).count() + 1
    db.session.commit()

    return success(data=review.to_dict(), message='评论添加成功')


@review_bp.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    review = Review.query.get(review_id)
    if not review:
        return error('评论不存在', 404)

    product = Product.query.get(review.product_id)
    db.session.delete(review)
    if product:
        product.review_count = max(0, product.review_count - 1)
    db.session.commit()
    return success(message='删除成功')


@review_bp.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')

    query = Product.query
    if keyword:
        query = query.filter(
            db.or_(
                Product.name.like(f'%{keyword}%'),
                Product.brand.like(f'%{keyword}%')
            )
        )
    if category:
        query = query.filter_by(category=category)

    query = query.order_by(Product.created_at.desc())
    return paginate_response(query, page, per_page)


@review_bp.route('/products/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return error('商品不存在', 404)
    return success(data=product.to_dict())


@review_bp.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    data = request.get_json()
    if not data or not data.get('name'):
        return error('商品名称不能为空', 400)

    product = Product(
        name=data['name'],
        category=data.get('category', '其他'),
        brand=data.get('brand', ''),
        price=data.get('price', 0),
        image_url=data.get('image_url', ''),
        source_url=data.get('source_url', ''),
        source_platform=data.get('source_platform', '京东'),
        description=data.get('description', ''),
    )
    db.session.add(product)
    db.session.commit()
    return success(data=product.to_dict(), message='商品添加成功')


@review_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return error('商品不存在', 404)

    data = request.get_json()
    if data.get('name'):
        product.name = data['name']
    if 'category' in data:
        product.category = data['category']
    if 'brand' in data:
        product.brand = data['brand']
    if 'price' in data:
        product.price = data['price']
    if 'image_url' in data:
        product.image_url = data['image_url']
    if 'description' in data:
        product.description = data['description']

    db.session.commit()
    return success(data=product.to_dict(), message='更新成功')


@review_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return error('商品不存在', 404)

    Review.query.filter_by(product_id=product_id).delete()
    db.session.delete(product)
    db.session.commit()
    return success(message='商品删除成功')


@review_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    categories = db.session.query(Product.category).distinct().all()
    return success(data=[c[0] for c in categories if c[0]])
