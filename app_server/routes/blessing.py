from flask import Blueprint,request
from app_server.controllers.blessing import generate_blessings
from app_server.utils.response import success_response, error_response
from app_server.models.target import Target
from app_server.models.blessing import Blessing
from flask_jwt_extended import jwt_required
from app_server.utils import get_current_user_id
from app_server.models.user import User

blessing_bp = Blueprint('blessing', __name__)

@blessing_bp.route('/blessing/<int:target_id>', methods=['POST'])
@jwt_required()
def generate_system_blessings(target_id):
    """
    生成系统祝福接口
    
    Args:
        target_id: int - 目标ID
        scene: str - 场景类型 (通过请求体传入)
    
    Returns:
        JSON响应，包含生成的祝福列表
    """
    
    try:
        # 从请求体中获取scene参数
        request_data = request.get_json()
        scene = request_data.get('scene', None)  # 允许scene参数缺失
        
        # 验证scene参数
        if scene is None:  # 允许scene为空或缺失
            scene = "default"  # 设置默认场景或其他处理逻辑
            
        user_id = get_current_user_id()

        target = Target.get_target_by_id(target_id)
        if not target:
            raise Exception(f"未找到ID为{target_id}的目标")

        if scene == "create" and target.user_id != user_id:
            raise Exception("无权限创建祝福") 
            
        # 将scene参数传入generate_blessings函数
        blessings = generate_blessings(target, user_id, scene)
        
        # 将blessing对象列表转换为字典列表
        blessing_list = [blessing.to_dict() for blessing in blessings]
        return success_response(data=blessing_list)
        
    except Exception as e:
        return error_response(str(e))


@blessing_bp.route('/blessings/<int:target_id>', methods=['GET'])
@jwt_required()
def get_blessings(target_id):
    """
    获取祝福详情接口（支持分页）
    
    Args:
        target_id: int - 目标ID
        page: int - 页码（通过查询参数传入，默认1）
        per_page: int - 每页数量（通过查询参数传入，默认10）
    
    Returns:
        JSON响应，包含祝福列表和分页信息
    """
    try:
        # 获取分页参数
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        
        # 验证目标是否存在
        target = Target.get_target_by_id(target_id)
        if not target:
            raise Exception(f"未找到ID为{target_id}的目标")
            
         # 获取祝福列表（按最新排序），并关联用户信息
        blessings = Blessing.query.filter_by(target_id=target_id)\
            .join(User, Blessing.user_id == User.id)\
            .add_columns(User.avatar, User.nickname)\
            .order_by(Blessing.create_time.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
            
        # 构建返回数据，包含用户信息
        blessing_list = [{
            **blessing.Blessing.to_dict(),
            'user_avatar': blessing.avatar,
            'user_nickname': blessing.nickname
        } for blessing in blessings.items]
        
        return success_response(data={
                'blessings': blessing_list,
                'page': blessings.page,
                'total_pages': blessings.pages,
                'total_count': blessings.total
        })
        
    except Exception as e:
        return error_response(str(e))