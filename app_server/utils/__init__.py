from flask_jwt_extended import get_jwt_identity

def get_current_user_id():
    """
    获取当前JWT token中的用户ID
    返回: int 类型的用户ID
    """
    user_id = get_jwt_identity()  # 获取字符串类型的user_id
    return int(user_id) if user_id is not None else None
