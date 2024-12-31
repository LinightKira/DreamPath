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
from app_server.logger import logger
from config.config import Config
from app_server.models.user import User  # 添加这行导入语句
from app_server.utils.redis import redis_client as r

target_bp = Blueprint('target', __name__)


@target_bp.route('/target', methods=['POST'])
@jwt_required()
def create_target():
    try:
        logger.info("开始创建新愿望")
        data = request.get_json()
        
        # 只接受指定字段
        allowed_fields = {'title', 'likes_goal', 'parent_id','image_url'}
        filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        # 如果 image_url 为空，添加默认地址
        if not filtered_data.get('image_url'):
            filtered_data['image_url'] = Config.DEFAULT_TARGET_IMAGE_URL  # 从Config中获取默认地址
        
        # 打印过滤后的数据
        logger.debug(f"过滤后的愿望数据: {filtered_data}")
        
        # 参数校验
        err = validate_target_data(filtered_data)
        if err is not None:
            logger.warning(f"愿望数据验证失败: {err}")
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": err})
        
        target = Target(**filtered_data)
        target.user_id = get_current_user_id()  # 使用工具函数获取整数类型的user_id
        
        target.save()
         # 在Redis中增加愿望计数器
        r.incr('targets_count')
        logger.info(f"愿望创建成功，ID: {target.id}")

        return jsonify({"code": HTTPStatus.OK, "msg": "success", "datas": target.to_dict()})

    except Exception as e:
        logger.error(f"创建愿望时发生错误: {str(e)}")
        db.session.rollback()
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


@target_bp.route('/target/<int:tid>', methods=['GET'])
@jwt_required()
def get_target(tid):
    try:
        logger.info(f"获取愿望详情，愿望ID: {tid}")
        target = Target.query.get(tid)

        if not target or target.status == 0:
            logger.warning(f"愿望不存在或已删除，愿望ID: {tid}")
            return jsonify({
                "code": HTTPStatus.NOT_FOUND,
                "msg": "愿望不存在"
            })

        uid = get_current_user_id()  # 使用工具函数
        user = User.query.get(target.user_id)  # 获取愿望用户的信息

        # 如果用户状态为0，则不返回愿望内容
        if user and user.status == 0:
            logger.warning(f"用户状态为0，无法获取愿望详情，愿望ID: {tid}")
            return jsonify({
                "code": HTTPStatus.FORBIDDEN,
                "msg": "用户状态不允许访问"
            })

        data = target.to_dict()
        logger.debug(f"当前用户ID: {uid}, 愿望所有者ID: {target.user_id}")
        
        # 默认设置为False True 表示为自己的
        data['is_edit'] = False
        if target.user_id == uid:
            data['is_edit'] = True
            
        # 查询当前用户是否祝福过该愿望
        target_like = TargetLike.query.filter_by(
            target_id=tid,
            user_id=uid
        ).first()
        data['is_liked'] = True if target_like else False

        # 获取愿望关联用户的头像和昵称
        if user:
            data['user_avatar'] = user.avatar  # 假设User模型有avatar字段
            data['user_nickname'] = user.nickname  # 假设User模型有nickname字段
            data['user_id'] = user.id 

        logger.info(f"成功获取愿望详情，愿望ID: {tid}")
        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "datas": data
        })

    except Exception as e:
        logger.error(f"获取愿望详情时发生错误: {str(e)}")
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
#                 "msg": "愿望不存在"
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
# 获取最新愿望：/targets?sort=latest
# 获取最热愿望：/targets?sort=hottest
# 分页和排序组合：/targets?sort=hottest&page=2&per_page=10
# 查询所有用户的愿望：/targets
# 查询特定用户的愿望：/targets?uid=123
# 组合查询：/targets?uid=123&sort=hottest&page=2&per_page=10
@target_bp.route('/targets', methods=['GET'])
def get_targets():
    try:
        logger.info("开始获取愿望列表")
        # 获取查询参数
        # 页码，默认为第1页
        page = request.args.get('page', 1, type=int)
        # 每页显示数量，默认为10条
        per_page = request.args.get('per_page', 10, type=int)
        # 排序类型，默认为最新（latest），可选最热（hottest）
        sort_type = request.args.get('sort', 'latest', type=str)
        # 愿望用户ID，可选
        target_uid = request.args.get('uid', type=int)
        
        # 基础查询条件
        # 仅显示状态为1（激活）且未完成的愿望
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
            # 1. 首先按祝福数降序排序
            # 2. 对于祝福数相同的愿望，按创建时间降序排序（确保最新的愿望排在前面）
            query = query.order_by(
                desc(Target.likes_count), 
                desc(Target.create_time)
            )
        else:  # 默认为最新排序
            # 按创建时间降序排序，显示最新创建的愿望
            query = query.order_by(desc(Target.create_time))
        
        # 执行分页查询
        pagination = query.paginate(page=page, per_page=per_page)
        # 获取当前页的愿望列表
        targets = pagination.items
        
        # 修改返回数据处理部分
        target_list = []
        for target in targets:
            target_dict = target.to_dict()
            # 获取愿望关联用户信息
            user = User.query.get(target.user_id)
            if user:
                target_dict['user_id'] = user.id
                target_dict['user_avatar'] = user.avatar
                target_dict['user_nickname'] = user.nickname
            target_list.append(target_dict)

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "datas": {
                'targets': target_list,  # 使用包含用户信息的愿望列表
                'page': page,
                'total_pages': pagination.pages,
                'total_count': pagination.total
            }
        })
    
    except PermissionError as e:
        # 处理权限相关的异常
        return jsonify({
            "code": HTTPStatus.FORBIDDEN, 
            "msg": "没有权限访问该用户的愿望"
        })
    except Exception as e:
        # 处理其他异常情况
        logger.error(f"获取愿望列表时发生错误: {str(e)}")
        return jsonify({
            "code": HTTPStatus.INTERNAL_SERVER_ERROR, 
            "msg": str(e)
        })






# @target_bp.route('/target/<int:target_id>/like', methods=['DELETE'])
# @jwt_required()
# def unlike_target(target_id):
#     """取消祝福"""
#     try:
#         uid = get_current_user_id() 
        
#         # 检查愿望是否存在
#         target = Target.query.get(target_id)
#         if not target:
#             return error_response('愿望不存在')
            
#         # 删除祝福
#         sucess = delete_target_like(target_id=target_id, user_id=uid)
#         if not sucess:
#             return error_response('未找到祝福记录')
            
#         return success_response(message='取消祝福成功')
#     except Exception as e:
#         return error_response(f'取消祝福失败: {str(e)}')



@target_bp.route('/target/<int:target_id>/complete', methods=['POST'])
@jwt_required()
def complete_target(target_id):
    """完成愿望"""
    try:
        uid = get_current_user_id()
        
        # 检查愿望是否存在
        target = Target.query.get(target_id)
        if not target:
            return error_response('愿望不存在')
            
        # 检查是否是愿望的创建者
        if target.user_id != uid:
            return error_response('无权限完成此愿望')
            
        # 检查愿望是否已经完成
        if target.is_completed:
            return error_response('愿望已经完成')
        
        # 尝试获取请求参数，如果没有传递 JSON，则默认为 True
        require_likes_condition = True
        if request.is_json:
            require_likes_condition = request.json.get('require_condition', True)
        
        
        # 如果限制还愿条件，检查点赞数是否达到目标
        if require_likes_condition and target.likes_count < target.likes_goal:
            return error_response('还没达成还愿条件噢')
            
        # 更新愿望状态为已完成，使用服务器当前时间
        target.is_completed = True
        target.complete_time = datetime.now()
        db.session.commit()
        r.incr('completed_targets_count')
        return success_response(message='还愿成功！')
    except Exception as e:
        db.session.rollback()
        return error_response(f'完成愿望失败: {str(e)}') 


@target_bp.route('/target/<int:target_id>/like', methods=['POST'])
@jwt_required()
def like_target(target_id):
    """祝福愿望"""
    logger.info(f"用户开始祝福愿望，愿望ID: {target_id}")
    try:
        uid = get_current_user_id() 
        
        # 检查愿望是否存在
        target = Target.query.get(target_id)
        if not target or target.status == 0:
            logger.warning(f"祝福失败，愿望不存在，愿望ID: {target_id}")
            return error_response('愿望不存在')
            
        # 检查是否已经祝福
        existing_like = TargetLike.query.filter_by(
            target_id=target_id,
            user_id=uid
        ).first()
        
        if existing_like:
            logger.warning(f"用户已经祝福过该愿望，用户ID: {uid}, 愿望ID: {target_id}")
            return error_response('已经祝福过啦')
            
        # 创建祝福
        success= create_target_like(target_id=target_id, user_id=uid)
        if not success:
            logger.error(f"创建祝福记录失败，用户ID: {uid}, 愿望ID: {target_id}")
            return error_response(f"祝福失败，等会再试试吧")
        
        logger.info(f"祝福成功，用户ID: {uid}, 愿望ID: {target_id}")
        return success_response(message='收到祝福啦，感恩遇见你')
    except Exception as e:
        logger.error(f"祝福过程中发生错误: {str(e)}")
        return error_response(f'祝福失败: {str(e)}')


@target_bp.route('/targets/my', methods=['GET'])
@jwt_required()
def get_my_targets():
    """查看我的愿望"""
    try:
        logger.info("开始获取我的愿望列表")
        uid = get_current_user_id()  # 获取当前用户ID
        
        # 检查用户是否存在以及用户状态
        user = User.query.get(uid)
        if not user or user.status == 0:
            return jsonify({
                "code": HTTPStatus.FORBIDDEN,
                "msg": "用户不存在或已禁用"
            })
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)  # 页码，默认为第1页
        per_page = request.args.get('per_page', 10, type=int)  # 每页显示数量，默认为10条
        sort_type = request.args.get('sort', 'latest', type=str)  # 排序类型，默认为最新（latest）
        include_completed = request.args.get('isclude_completed', 'false', type=str).lower() == 'true'  # 是否包含已完成的
        
        # 基础查询条件
        query = Target.query.filter(Target.user_id == uid)
        
        # 过滤已完成或未完成的愿望
        if not include_completed:
            query = query.filter(Target.is_completed == False)
        
        # 根据排序类型应用不同的排序规则
        if sort_type == 'hottest':
            query = query.order_by(desc(Target.likes_count), desc(Target.create_time))
        else:  # 默认为最新排序
            query = query.order_by(desc(Target.create_time))
        
        # 执行分页查询
        pagination = query.paginate(page=page, per_page=per_page)
        targets = pagination.items
        
        # 修改返回数据处理部分
        target_list = [target.to_dict() for target in targets]

        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "datas": {
                'targets': target_list,
                'page': page,
                'total_pages': pagination.pages,
                'total_count': pagination.total
            }
        })
    
    except Exception as e:
        logger.error(f"获取我的愿望列表时发生错误: {str(e)}")
        return jsonify({
            "code": HTTPStatus.INTERNAL_SERVER_ERROR, 
            "msg": str(e)
        })