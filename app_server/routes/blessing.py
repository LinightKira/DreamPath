from flask import Blueprint
from app_server.controllers.blessing import generate_blessings
from app_server.utils.response import success_response, error_response
from app_server.models.target import Target
from flask_jwt_extended import jwt_required
from app_server.utils import get_current_user_id

blessing_bp = Blueprint('blessing', __name__)

@blessing_bp.route('/blessing/<int:target_id>', methods=['POST'])
@jwt_required()
def generate_system_blessings(target_id):
    """
    生成系统祝福接口
    
    Args:
        target_id: int - 目标ID
        
    Returns:
        JSON响应，包含生成的祝福列表
    """

    try:
        user_id = get_current_user_id()

        target = Target.get_target_by_id(target_id)
        if not target:
            raise Exception(f"未找到ID为{target_id}的目标")
        
        if user_id != target.user_id:
            return error_response("无权限访问该目标")

        blessings = generate_blessings(target_id, target.title)
        # 将blessing对象列表转换为字典列表
        blessing_list = [blessing.to_dict() for blessing in blessings]
        return success_response(data=blessing_list)
    except Exception as e:
        return error_response(str(e))