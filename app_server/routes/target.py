from http import HTTPStatus
from datetime import datetime

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required
from sqlalchemy import desc

from app_server import db
from app_server.models.target import Target
from app_server.vaildate.vaildate_target import validate_target_data
from app_server.models.target_like import create_target_like, TargetLike
from app_server.utils.response import success_response, error_response
from app_server.utils import get_current_user_id
from app_server.logger import logger_runner

target_bp = Blueprint('target', __name__)


@target_bp.route('/target', methods=['POST'])
@jwt_required()
def create_target():
    try:
        logger_runner.info("开始创建新目标")
        data = request.get_json()
        
        # 只接受指定字段
        allowed_fields = {'title', 'desc', 'deadline','c_type', 'parent_id'}
        filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        # 打印过滤后的数据
        logger_runner.debug(f"过滤后的目标数据: {filtered_data}")
        
        # 参数校验
        err = validate_target_data(filtered_data)
        if err is not None:
            logger_runner.warning(f"目标数据验证失败: {err}")
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})
        
        target = Target(**filtered_data)
        target.user_id = get_current_user_id()  # 使用工具函数获取整数类型的user_id
        
        target.create()
        logger_runner.info(f"目标创建成功，ID: {target.id}")
        return jsonify({"code": HTTPStatus.OK, "msg": "success", "datas": target.to_dict()})

    except Exception as e:
        logger_runner.error(f"创建目标时发生错误: {str(e)}")
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@target_bp.route('/target/<int:tid>', methods=['GET'])
@jwt_required()
def get_target(tid):
    try:
        logger_runner.info(f"获取目标详情，目标ID: {tid}")
        target = Target.query.get(tid)

        if not target or target.status == 0:
            logger_runner.warning(f"目标不存在或已删除，目标ID: {tid}")
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "目标不存在"
            })

        data = target.to_dict()
        uid = get_current_user_id()  # 使用工具函数
        logger_runner.debug(f"当前用户ID: {uid}, 目标所有者ID: {target.user_id}")
        print('uid:',uid,type(uid))
        print('targetuser_id',target.user_id,type(target.user_id))
        
        # 默认设置为False True 表示为自己的
        data['is_edit'] = False
        if target.user_id == uid:
            data['is_edit'] = True
            
        # 查询当前用户是否点赞过该目标
        target_like = TargetLike.query.filter_by(
            target_id=tid,
            user_id=uid
        ).first()
        data['is_liked'] = True if target_like else False

        logger_runner.info(f"成功获取目标详情，目标ID: {tid}")
        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "datas": data
        })

    except Exception as e:
        logger_runner.error(f"获取目标详情时发生错误: {str(e)}")
        return jsonify({
            "code": HTTPStatus.INTERNAL_SERVER_ERROR,
            "msg": str(e)
        })


# @target_bp.route('/target', methods=['PUT'])
# @jwt_required()
# def update_target():
#     try:
#         data = request.get_json()
#         tid = data.get('id')
#         target = Target.query.get(tid)

#         if not target or target.status == 0:
#             return jsonify({
#                 "code": HTTPStatus.NOT_FOUND,
#                 "msg": "目标不存在"
#             })

#         # 权限校验
#         uid = get_current_user_id() 
#         if uid != target.user_id:
#             return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "无权限修改"})

#         # 必填校验
#         err = validate_target_data(data)
#         if err is not None:
#             return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})

#         # 排除create_time和update_time
#         data.pop("create_time", None)
#         data.pop("update_time", None)

#         Target.query.filter_by(id=data.pop("id")).update(data)
#         db.session.commit()

#         return jsonify({
#             "code": HTTPStatus.OK,
#             "msg": "success"
#         })

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@target_bp.route('/target/<int:tid>', methods=['DELETE'])
@jwt_required()
def delete_target(tid):
    try:
        target = Target.query.get(tid)
        uid = get_current_user_id() 
        
        if not target or target.user_id != uid:
            return jsonify({"code": HTTPStatus.FORBIDDEN, "msg": "无权限删除"})

        # 逻辑删除
        target.status = 0
        db.session.commit()

        return jsonify({'code': HTTPStatus.OK, 'msg': '删除成功'})

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})

# 使用示例：
# 获取最新目标：/targets?sort=latest
# 获取最热目标：/targets?sort=hottest
# 分页和排序组合：/targets?sort=hottest&page=2&per_page=10
# 查询所有用户的目标：/targets
# 查询特定用户的目标：/targets?uid=123
# 组合查询：/targets?uid=123&sort=hottest&page=2&per_page=10
@target_bp.route('/targets', methods=['GET'])
@jwt_required()
def get_targets():
    try:
        logger_runner.info("开始获取目标列表")
        # 获取查询参数
        # 页码，默认为第1页
        page = request.args.get('page', 1, type=int)
        # 每页显示数量，默认为10条
        per_page = request.args.get('per_page', 10, type=int)
        # 排序类型，默认为最新（latest），可选最热（hottest）
        sort_type = request.args.get('sort', 'latest', type=str)
        # 目标用户ID，可选
        target_uid = request.args.get('uid', type=int)
        
        # 基础查询条件
        # 仅显示状态为1（激活）且未完成的目标
        query = Target.query.filter(
            Target.status == 1, 
            Target.is_completed == False
        )
        
        # 如果提供了特定用户ID，则按该用户ID过滤
        if target_uid:           
            query = query.filter(Target.user_id == target_uid)
        
        # 根据排序类型应用不同的排序规则
        if sort_type == 'hottest':
            # 最热排序：
            # 1. 首先按点赞数降序排序
            # 2. 对于点赞数相同的目标，按创建时间降序排序（确保最新的目标排在前面）
            query = query.order_by(
                desc(Target.likes_count), 
                desc(Target.create_time)
            )
        else:  # 默认为最新排序
            # 按创建时间降序排序，显示最新创建的目标
            query = query.order_by(desc(Target.create_time))
        
        # 执行分页查询
        pagination = query.paginate(page=page, per_page=per_page)
        # 获取当前页的目标列表
        targets = pagination.items
        
        # 返回JSON响应
        logger_runner.info(f"成功获取目标列表，总数: {pagination.total}")
        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "datas": {
                # 将目标列表转换为字典格式
                'targets': [t.to_dict() for t in targets],
                # 当前页码
                'page': page,
                # 总页数
                'total': pagination.pages,
                # 总目标数
                'total_count': pagination.total
            }
        })
    
    except PermissionError as e:
        # 处理权限相关的异常
        return jsonify({
            "code": HTTPStatus.FORBIDDEN, 
            "msg": "没有权限访问该用户的目标"
        })
    except Exception as e:
        # 处理其他异常情况
        logger_runner.error(f"获取目标列表时发生错误: {str(e)}")
        return jsonify({
            "code": HTTPStatus.INTERNAL_SERVER_ERROR, 
            "msg": str(e)
        })



@target_bp.route('/target/<int:target_id>/like', methods=['POST'])
@jwt_required()
def like_target(target_id):
    """点赞目标"""
    logger_runner.info(f"用户开始点赞目标，目标ID: {target_id}")
    try:
        uid = get_current_user_id() 
        
        # 检查目标是否存在
        target = Target.query.get(target_id)
        if not target:
            logger_runner.warning(f"点赞失败，目标不存在，目标ID: {target_id}")
            return error_response('目标不存在')
            
        # 检查是否已经点赞
        existing_like = TargetLike.query.filter_by(
            target_id=target_id,
            user_id=uid
        ).first()
        
        if existing_like:
            logger_runner.warning(f"用户已经点赞过该目标，用户ID: {uid}, 目标ID: {target_id}")
            return error_response('已经点赞过该目标')
            
        # 创建点赞
        success= create_target_like(target_id=target_id, user_id=uid)
        if not success:
            logger_runner.error(f"创建点赞记录失败，用户ID: {uid}, 目标ID: {target_id}")
            return error_response(f"点赞失败")
        
        logger_runner.info(f"点赞成功，用户ID: {uid}, 目标ID: {target_id}")
        return success_response(message='点赞成功')
    except Exception as e:
        logger_runner.error(f"点赞过程中发生错误: {str(e)}")
        return error_response(f'点赞失败: {str(e)}')


# @target_bp.route('/target/<int:target_id>/like', methods=['DELETE'])
# @jwt_required()
# def unlike_target(target_id):
#     """取消点赞"""
#     try:
#         uid = get_current_user_id() 
        
#         # 检查目标是否存在
#         target = Target.query.get(target_id)
#         if not target:
#             return error_response('目标不存在')
            
#         # 删除点赞
#         sucess = delete_target_like(target_id=target_id, user_id=uid)
#         if not sucess:
#             return error_response('未找到点赞记录')
            
#         return success_response(message='取消点赞成功')
#     except Exception as e:
#         return error_response(f'取消点赞失败: {str(e)}')



@target_bp.route('/target/<int:target_id>/complete', methods=['POST'])
@jwt_required()
def complete_target(target_id):
    """完成目标"""
    try:
        uid = get_current_user_id()
        
        # 检查目标是否存在
        target = Target.query.get(target_id)
        if not target:
            return error_response('目标不存在')
            
        # 检查是否是目标的创建者
        if target.user_id != uid:
            return error_response('无权限完成此目标')
            
        # 检查目标是否已经完成
        if target.is_completed:
            return error_response('目标已经完成')
            
        # 更新目标状态为已完成，使用服务器当前时间
        target.is_completed = True
        target.complete_time = datetime.now()
        db.session.commit()
        
        return success_response(message='目标完成成功')
    except Exception as e:
        db.session.rollback()
        return error_response(f'完成目标失败: {str(e)}') 