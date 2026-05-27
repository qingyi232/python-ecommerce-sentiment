from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.utils.response import success, error, paginate_response

user_bp = Blueprint('user', __name__)


@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)
    if not current_user or current_user.role != 'admin':
        return error('无权限访问', 403)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')
    role = request.args.get('role', '')

    query = User.query
    if keyword:
        query = query.filter(
            db.or_(
                User.username.like(f'%{keyword}%'),
                User.nickname.like(f'%{keyword}%'),
                User.email.like(f'%{keyword}%')
            )
        )
    if role:
        query = query.filter_by(role=role)

    query = query.order_by(User.created_at.desc())
    return paginate_response(query, page, per_page)


@user_bp.route('/<int:uid>', methods=['PUT'])
@jwt_required()
def update_user(uid):
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)
    if not current_user or current_user.role != 'admin':
        return error('无权限操作', 403)

    target = User.query.get(uid)
    if not target:
        return error('用户不存在', 404)

    data = request.get_json()
    if 'status' in data:
        target.status = data['status']
    if 'role' in data:
        target.role = data['role']
    if 'nickname' in data:
        target.nickname = data['nickname']

    db.session.commit()
    return success(data=target.to_dict(), message='更新成功')


@user_bp.route('/<int:uid>', methods=['DELETE'])
@jwt_required()
def delete_user(uid):
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)
    if not current_user or current_user.role != 'admin':
        return error('无权限操作', 403)

    if uid == user_id:
        return error('不能删除自己的账号', 400)

    target = User.query.get(uid)
    if not target:
        return error('用户不存在', 404)

    db.session.delete(target)
    db.session.commit()
    return success(message='删除成功')
