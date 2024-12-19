from datetime import datetime, timezone
from http import HTTPStatus
from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

from app_server.logger import logger_runner
from app_server.models.user import User

user_bp = Blueprint('user', __name__)


# 获取用户信息接口-进供测试用
@user_bp.route('/user/userinfo')
def get_userInfo():
    uid = request.args.get('uid')
    if not uid:
        return {
            "code": 400,
            "msg": "参数错误！",
        }
    try:
        user = User.query.filter(User.id == uid).first()
        if not user:
            print("user 不存在")
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
            # "refresh_token": create_refresh_token(identity=user.id)
        }

        return jsonify({"code": HTTPStatus.OK, "msg": "success", "datas": res})

    except Exception as e:
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
        logger_runner.info(
            f"User {current_user_id} refreshed access token at {datetime.now(timezone.utc)}"
        )
        user.last_active_time = datetime.now()
        user.save()
        return jsonify({
            'code': 200,
            'msg': '刷新成功',
            'data': {
                'access_token': access_token
            }
        })

    except Exception as e:
        logger_runner.error(f"Token refresh failed: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '服务器内部错误'
        }), 500
