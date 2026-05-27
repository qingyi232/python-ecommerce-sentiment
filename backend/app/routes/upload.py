import os
import uuid
from flask import Blueprint, request, send_from_directory, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from app.utils.response import success, error

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_upload_dir():
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


@upload_bp.route('/image', methods=['POST'])
@jwt_required()
def upload_image():
    if 'file' not in request.files:
        return error('请选择要上传的文件', 400)

    file = request.files['file']
    if file.filename == '':
        return error('文件名为空', 400)

    if not allowed_file(file.filename):
        return error(f'不支持的文件格式，仅支持 {", ".join(ALLOWED_EXTENSIONS)}', 400)

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f'{uuid.uuid4().hex}.{ext}'
    upload_dir = get_upload_dir()
    file.save(os.path.join(upload_dir, filename))

    file_url = f'/api/upload/files/{filename}'
    return success(data={'url': file_url, 'filename': filename}, message='上传成功')


@upload_bp.route('/files/<filename>', methods=['GET'])
def get_file(filename):
    upload_dir = get_upload_dir()
    safe_name = secure_filename(filename)
    if not os.path.exists(os.path.join(upload_dir, safe_name)):
        return error('文件不存在', 404)
    return send_from_directory(upload_dir, safe_name)
