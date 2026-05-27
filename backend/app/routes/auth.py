from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.utils.response import success, error

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return error('请求数据为空', 400)

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return error('用户名和密码不能为空', 400)

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return error('用户名或密码错误', 401)

    if user.status != 1:
        return error('账号已被禁用', 403)

    token = create_access_token(identity=str(user.id))
    return success(data={
        'token': token,
        'user': user.to_dict()
    }, message='登录成功')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return error('请求数据为空', 400)

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    email = data.get('email', '').strip()
    role = data.get('role', 'user')

    if not username or not password or not email:
        return error('用户名、密码和邮箱不能为空', 400)

    if len(username) < 3 or len(username) > 50:
        return error('用户名长度需在3-50个字符之间', 400)

    if len(password) < 6:
        return error('密码长度不能少于6个字符', 400)

    if User.query.filter_by(username=username).first():
        return error('用户名已存在', 409)

    if User.query.filter_by(email=email).first():
        return error('邮箱已被注册', 409)

    user = User(username=username, email=email, role=role, nickname=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return success(data=user.to_dict(), message='注册成功')


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return error('用户不存在', 404)
    return success(data=user.to_dict())


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return error('用户不存在', 404)

    data = request.get_json()
    if data.get('nickname'):
        user.nickname = data['nickname']
    if data.get('email'):
        existing = User.query.filter(User.email == data['email'], User.id != user_id).first()
        if existing:
            return error('邮箱已被使用', 409)
        user.email = data['email']
    if data.get('avatar'):
        user.avatar = data['avatar']

    db.session.commit()
    return success(data=user.to_dict(), message='更新成功')
