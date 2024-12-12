from http import HTTPStatus

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc

from app_server import db
from app_server.models.target import Target
from app_server.vaildate.vaildate_target import validate_target_data
from app_server.models.target_like import create_target_like, delete_target_like, TargetLike
from app_server.utils.response import success_response, error_response

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


@target_bp.route('/target/<int:target_id>/like', methods=['POST'])
@jwt_required()
def like_target(target_id):
    """点赞目标"""
    try:
        uid = get_jwt_identity()
        
        # 检查目标是否存在
        target = Target.query.get(target_id)
        if not target:
            return error_response('目标不存在')
            
        # 检查是否已经点赞
        existing_like = TargetLike.query.filter_by(
            target_id=target_id,
            user_id=uid
        ).first()
        
        if existing_like:
            return error_response('已经点赞过该目标')
            
        # 创建点赞
        create_target_like(target_id=target_id, user_id=uid)
        
        return success_response(message='点赞成功')
    except Exception as e:
        return error_response(f'点赞失败: {str(e)}')


@target_bp.route('/target/<int:target_id>/like', methods=['DELETE'])
@jwt_required()
def unlike_target(target_id):
    """取消点赞"""
    try:
        uid = get_jwt_identity()
        
        # 检查目标是否存在
        target = Target.query.get(target_id)
        if not target:
            return error_response('目标不存在')
            
        # 删除点赞
        like = delete_target_like(target_id=target_id, user_id=uid)
        if not like:
            return error_response('未找到点赞记录')
            
        return success_response(message='取消点赞成功')
    except Exception as e:
        return error_response(f'取消点赞失败: {str(e)}')


@target_bp.route('/target/<int:target_id>/like/status', methods=['GET'])
@jwt_required()
def get_like_status(target_id):
    """获取当前用户的点赞状态"""
    try:
        uid = get_jwt_identity()
        
        # 检查目标是否存在
        target = Target.query.get(target_id)
        if not target:
            return error_response('目标不存在')
            
        # 查询点赞状态
        is_liked = TargetLike.query.filter_by(
            target_id=target_id,
            user_id=uid
        ).first() is not None
        
        return success_response(data={
            'is_liked': is_liked,
            'likes_count': target.likes_count
        })
    except Exception as e:
        return error_response(f'获取点赞状态失败: {str(e)}') 