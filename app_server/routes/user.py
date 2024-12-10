from http import HTTPStatus
from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

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
            "access_token": create_access_token(identity=user.id)
            # "refresh_token": create_refresh_token(identity=user.id)
        }

        return jsonify({"code": HTTPStatus.OK, "msg": "success", "datas": res})

    except Exception as e:
        return jsonify({"code": HTTPStatus.INTERNAL_SERVER_ERROR, "msg": str(e)})


# 刷新Token
@user_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    print("uid:", identity)
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)
