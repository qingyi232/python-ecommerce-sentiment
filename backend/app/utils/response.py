from flask import jsonify


def success(data=None, message='操作成功', code=200):
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    }), 200


def error(message='操作失败', code=400, data=None):
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    }), code if code < 600 else 400


def paginate_response(query, page, per_page, schema_func=None):
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    if schema_func:
        items = [schema_func(item) for item in items]
    else:
        items = [item.to_dict() for item in items]

    return success(data={
        'items': items,
        'total': pagination.total,
        'page': pagination.page,
        'per_page': pagination.per_page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
    })
