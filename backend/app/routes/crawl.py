from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.crawl_task import CrawlTask
from app.utils.response import success, error, paginate_response

crawl_bp = Blueprint('crawl', __name__)


@crawl_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')

    query = CrawlTask.query
    if status:
        query = query.filter_by(status=status)
    query = query.order_by(CrawlTask.created_at.desc())
    return paginate_response(query, page, per_page)


@crawl_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data:
        return error('请求数据为空', 400)

    task_name = data.get('task_name', '').strip()
    keyword = data.get('keyword', '').strip()

    if not task_name:
        return error('任务名称不能为空', 400)

    task = CrawlTask(
        task_name=task_name,
        platform=data.get('platform', '京东'),
        keyword=keyword,
        target_url=data.get('target_url', ''),
        created_by=user_id,
    )
    db.session.add(task)
    db.session.commit()

    return success(data=task.to_dict(), message='爬取任务创建成功')


@crawl_bp.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    task = CrawlTask.query.get(task_id)
    if not task:
        return error('任务不存在', 404)
    return success(data=task.to_dict())


@crawl_bp.route('/tasks/<int:task_id>/start', methods=['POST'])
@jwt_required()
def start_task(task_id):
    task = CrawlTask.query.get(task_id)
    if not task:
        return error('任务不存在', 404)

    if task.status == 'running':
        return error('任务正在执行中', 400)

    from datetime import datetime
    task.status = 'running'
    task.started_at = datetime.utcnow()
    db.session.commit()

    from app.services.crawl_service import CrawlService
    CrawlService.run_task(task.id)

    return success(data=task.to_dict(), message='任务已启动')


@crawl_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    task = CrawlTask.query.get(task_id)
    if not task:
        return error('任务不存在', 404)

    if task.status == 'running':
        return error('任务正在执行中，无法删除', 400)

    db.session.delete(task)
    db.session.commit()
    return success(message='任务已删除')
