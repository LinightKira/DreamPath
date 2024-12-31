from flask import Blueprint, jsonify
from app_server.models.target import Target
from flask_jwt_extended import jwt_required
from app_server.utils.redis import redis_client as r
from app_server.logger import logger
from app_server.utils.response import success_response, error_response  # 新增导入
start_bp = Blueprint('start', __name__)

@start_bp.route('/start', methods=['GET'])
@jwt_required()
def start():
    try:
        targets_count = r.get('targets_count')
        completed_targets_count = r.get('completed_targets_count')

        if targets_count is None or completed_targets_count is None:
            # 从数据库中统计
            targets_count = Target.count_targets()
            completed_targets_count = Target.count_completed_targets()

            print("从数据库中统计")
            
            # 保存到 Redis
            r.set('targets_count', targets_count)
            r.set('completed_targets_count', completed_targets_count)
        else :
            print("从 Redis 中获取")
             # 将从 Redis 获取的 bytes 转换为整数
            targets_count = int(targets_count)
            completed_targets_count = int(completed_targets_count)           

    except Exception as e:
        logger.error(f"发生错误: {e}")
        return error_response('无法获取数据', status_code=500)  # 修改为统一错误响应


    return success_response(data={  # 修改为统一成功响应
        'targets_count': targets_count,
        'completed_targets_count': completed_targets_count
    })