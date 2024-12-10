from http import HTTPStatus

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc

from app_server import db
from app_server.models.theme import Theme
from app_server.vaildate.vaildate_theme import validate_theme_data

theme_bp = Blueprint('theme', __name__)


@theme_bp.route('/theme', methods=['POST'])
@jwt_required()
def create_theme():
    try:
        data = request.get_json()

        # 参数校验
        err = validate_theme_data(data)
        # 如果err有内容
        if err is not None:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})
        else:
            theme = Theme(**data)
            uid = get_jwt_identity()
            theme.user_id = uid

            theme.create()
            return jsonify({"code": HTTPStatus.OK, "msg": "success", "datas": theme.to_dict()})

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@theme_bp.route('/theme/<int:aid>', methods=['GET'])
@jwt_required()
def get_theme(aid):
    try:
        theme = Theme.query.get(aid)

        if not theme or theme.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "theme not found."
            })

        data = theme.to_dict()

        uid = get_jwt_identity()
        if theme.user_id == uid:
            # 可以进行编辑
            data['is_edit'] = True

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "datas": data
        })

    except Exception as e:
        return jsonify({
            "code": HTTPStatus.INTERNAL_SERVER_ERROR,
            "msg": str(e)
        })


@theme_bp.route('/theme/', methods=['PUT'])
@jwt_required()
def update_theme():
    try:
        data = request.get_json()
        aid = data.get('id')
        theme = Theme.query.get(aid)

        if not theme or theme.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "theme not found."
            })

        err = ""
        uid = get_jwt_identity()
        if uid != theme.user_id:
            err = "uid error."

        if uid != data.get('user_id'):
            err = "user_id error"

        if len(err) != 0:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})

        # 必填校验
        err = validate_theme_data(data)
        # 如果err有内容
        if err is not None:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})

        # Exclude create_time and update_time from the update
        data.pop("create_time", None)
        data.pop("update_time", None)

        theme.query.filter_by(id=data.pop("id")).update(data)
        db.session.commit()

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@theme_bp.route('/theme/<int:cid>', methods=['DELETE'])
@jwt_required()
def delete_theme(aid):
    try:
        theme = Theme.query.get(aid)
        uid = get_jwt_identity()
        if not theme or theme.user_id != uid:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "Permission denied"})

        # 逻辑删除角色
        theme.status = 0
        db.session.commit()

        return jsonify({'code': HTTPStatus.OK, 'msg': 'theme deleted'})

    except Exception as e:

        db.session.rollback()

        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@theme_bp.route('/theme', methods=['GET'])
@jwt_required()
def get_themes():
    try:
        uid = get_jwt_identity()
        last_id = request.args.get('last_id')
        page = request.args.get('page', 1, type=int)

        # 查询条件应始终过滤状态
        query = Theme.query.filter(Theme.user_id == uid, Theme.status > 0)

        # 设置排序方式为id降序
        query = query.order_by(desc(Theme.id))

        if last_id:
            # 根据last_id分页
            query = query.filter(Theme.id < last_id)
            # 分页
        pagination = query.paginate(page=page, per_page=10)

        theme = pagination.items

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "datas": {
                'theme': [c.to_dict() for c in theme],
                'page': page,
                'total': pagination.pages
            }
        })
    except Exception as e:
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})
