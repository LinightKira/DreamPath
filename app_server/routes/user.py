from datetime import datetime, timezone
from http import HTTPStatus
from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

from app_server.logger import logger
from app_server.models.user import User
from app_server.utils import get_current_user_id
from config import Config
from app_server import db

user_bp = Blueprint('user', __name__)


# 获取用户信息接口-进供测试用
@user_bp.route('/user/userinfo')
def get_userInfo():
    # 检查是否在测试模式
    if not Config.TESTING_MODE:
        logger.warning("非测试环境尝试访问测试接口")
        return jsonify({
            "code": HTTPStatus.FORBIDDEN,
            "msg": "该接口仅在测试环境可用"
        })
        
    uid = request.args.get('uid')
    if not uid:
        return {
            "code": 400,
            "msg": "参数错误！",
        }
    
    try:
        user = User.query.filter(User.id == uid).first()
        if not user:
            logger.warning(f"用户不存在，用户ID: {uid}")
            return {
                "code": 200,
                "msg": "用户不存在"
            }
            
        res = {
            "userInfo": {
                "nickname": user.nickname,
                "avatar": user.avatar
            },
            "access_token": create_access_token(identity=str(user.id))
        }

        return jsonify({"code": HTTPStatus.OK, "msg": "success", "datas": res})

    except Exception as e:
        logger.error(f"获取用户信息时发生错误: {str(e)}")
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


# 刷新Token
@user_bp.route('/user/refresh', methods=['POST'])
@jwt_required()
def refresh():
    try:
        # 获取当前用户身份
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({
                'code': 401,
                'msg': '无效的刷新令牌'
            }), 401

        # 可以在这里添加额外的用户验证逻辑
        user = User.query.get(current_user_id)
        if not user or not user.status==1:
            return jsonify({
                'code': 401,
                'msg': '用户状态异常'
            }), 401

        
        access_token = create_access_token(
            identity=current_user_id
        )

        # 记录刷新token的操作日志
        logger.info(
            f"User {current_user_id} refreshed access token at {datetime.now(timezone.utc)}"
        )
        user.last_active_time = datetime.now()
        user.save()
        return jsonify({
            'code': 200,
            'msg': '刷新成功',
            'datas': {
                "nickname": user.nickname,
                "avatar": user.avatar, 
                'access_token': access_token
            }
        })

    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '服务器内部错误'
        }), 500

# 更新用户信息
@user_bp.route('/user/info', methods=['PUT'])
@jwt_required()
def update_user():
    try:
        logger.info("开始更新用户信息")
        data = request.get_json()
        
        # 只允许更新指定字段,且过滤掉空值
        allowed_fields = {'nickname', 'avatar', 'gender', 'birthday', 'phone', 'qq'}
        filtered_data = {k: v for k, v in data.items() if k in allowed_fields and v is not None}
        
        logger.debug(f"过滤后的用户数据: {filtered_data}")
        
        # 如果没有需要更新的数据
        if not filtered_data:
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": "没有需要更新的数据"})
        
        # 数据验证
        if 'gender' in filtered_data and filtered_data['gender'] not in [0, 1, 2]:
            logger.warning("性别参数无效")
            return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": "性别参数无效"})
            
        if 'birthday' in filtered_data:
            try:
                filtered_data['birthday'] = datetime.strptime(filtered_data['birthday'], '%Y-%m-%d').date()
            except ValueError:
                logger.warning("生日格式无效")
                return jsonify({"code": HTTPStatus.BAD_REQUEST, "msg": "生日格式无效，应为YYYY-MM-DD"})
        
        # 获取当前用户
        uid = get_current_user_id()
        user = User.query.get(uid)
        
        if not user:
            logger.error(f"未找到用户，用户ID: {uid}")
            return jsonify({"code": HTTPStatus.NOT_FOUND, "msg": "用户不存在"})
        
        # 使用父类的update方法更新用户信息
        user.update(**filtered_data)
        logger.info(f"用户信息更新成功，用户ID: {uid}")
        
        # 返回更新后的用户信息
        return jsonify({
            "code": HTTPStatus.OK,
            "msg": "success",
            "datas": user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"更新用户信息时发生错误: {str(e)}")
        return jsonify({
            "code": HTTPStatus.INTERNAL_SERVER_ERROR,
            "msg": str(e)
        })
