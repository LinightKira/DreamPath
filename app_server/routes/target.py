from http import HTTPStatus

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc

from app_server import db
from app_server.models.target import Target
from app_server.vaildate.vaildate_target import validate_target_data

target_bp = Blueprint('target', __name__)


@target_bp.route('/target', methods=['POST'])
@jwt_required()
def create_target():
    try:
        data = request.get_json()

        # 参数校验
        err = validate_target_data(data)
        if err is not None:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})
        
        target = Target(**data)
        uid = get_jwt_identity()
        target.user_id = uid

        target.create()
        return jsonify({"code": HTTPStatus.OK, "msg": "success", "datas": target.to_dict()})

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@target_bp.route('/target/<int:tid>', methods=['GET'])
@jwt_required()
def get_target(tid):
    try:
        target = Target.query.get(tid)

        if not target or target.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "目标不存在"
            })

        data = target.to_dict()
        uid = get_jwt_identity()
        if target.user_id == uid:
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


@target_bp.route('/target', methods=['PUT'])
@jwt_required()
def update_target():
    try:
        data = request.get_json()
        tid = data.get('id')
        target = Target.query.get(tid)

        if not target or target.status == 0:
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "目标不存在"
            })

        # 权限校验
        uid = get_jwt_identity()
        if uid != target.user_id:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "无权限修改"})

        # 必填校验
        err = validate_target_data(data)
        if err is not None:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})

        # 排除create_time和update_time
        data.pop("create_time", None)
        data.pop("update_time", None)

        Target.query.filter_by(id=data.pop("id")).update(data)
        db.session.commit()

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success"
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@target_bp.route('/target/<int:tid>', methods=['DELETE'])
@jwt_required()
def delete_target(tid):
    try:
        target = Target.query.get(tid)
        uid = get_jwt_identity()
        
        if not target or target.user_id != uid:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "无权限删除"})

        # 逻辑删除
        target.status = 0
        db.session.commit()

        return jsonify({'code': HTTPStatus.OK, 'msg': '删除成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@target_bp.route('/targets', methods=['GET'])
@jwt_required()
def get_targets():
    try:
        uid = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # 查询条件过滤
        query = Target.query.filter(Target.user_id == uid, Target.status > 0)

        # 按创建时间倒序
        query = query.order_by(desc(Target.create_time))

        # 分页
        pagination = query.paginate(page=page, per_page=per_page)
        targets = pagination.items

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "datas": {
                'targets': [t.to_dict() for t in targets],
                'page': page,
                'total': pagination.pages,
                'total_count': pagination.total
            }
        })
    except Exception as e:
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)}) 