import json
from app_server.utils.coze import run_coze_workflow
from config.config import Config
from app_server.models.blessing import Blessing
from app_server.models.target import Target

def generate_blessings(target:Target, uid:int, scene: str) -> list:
    """
    根据目标ID生成系统祝福并保存到数据库
    
    Args:
        target: int - 目标
        uid: int - 祝福的用户ID
        scene: str - 场景描述
    
    Returns:
        list - Blessing对象列表
    """
    title = target.title
    user_id = None
    if scene == "like":
        user_id = uid
    try:
        # 调用Coze工作流
        parameters = {
            "input": title,
            "scene": scene
        }
        result = run_coze_workflow(Config.WorkFlowID_ZF, parameters)
        
        if result['code'] != 0:
            raise Exception(f"Coze工作流调用失败: {result['msg']}")
            
        # 解析返回的数据
        data = json.loads(result['data'])
        blessings_list = json.loads(data['output']) if isinstance(data['output'], str) else data['output']
        
        # 创建blessing对象列表
        blessing_objects = []
        for blessing_text in blessings_list:
            # 分割祝福者名字和内容,支持全角和半角冒号
            parts = blessing_text.split('：', 1) if '：' in blessing_text else blessing_text.split(':', 1)
            
            if len(parts) == 2:
                blesser_name = parts[0].strip()
                content = parts[1].strip()
            else:
                blesser_name = "匿名仙友"
                content = blessing_text.strip()
            
            blessing = Blessing(
                blesser_name=blesser_name,
                content=content,
                target_id=target.id,
                user_id=user_id,
                is_system=True

            )
            blessing_objects.append(blessing)
        
        # 批量创建数据库记录
        Blessing.bulk_create(blessing_objects)
        
        return blessing_objects
        
    except Exception as e:
        raise Exception(f"生成祝福失败: {str(e)}")
