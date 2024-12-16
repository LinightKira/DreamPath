import json
from app_server.utils.coze import run_coze_workflow
from config import Config
from app_server.models.blessing import Blessing
from app_server.models.target import Target

def generate_blessings(target_id: int, title: str) -> list:
    """
    根据目标ID生成系统祝福并保存到数据库
    
    Args:
        target_id: int - 目标用户ID
        title: str - 标题
    
    Returns:
        list - Blessing对象列表
    """

    print('start blessings')
    try:
        # 调用Coze工作流
        parameters = {
            "input": title
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
                blesser_name = "一位不愿意透露姓名的网友"
                content = blessing_text.strip()
            
            blessing = Blessing(
                blesser_name=blesser_name,
                content=content,
                target_id=target_id,
            )
            blessing_objects.append(blessing)
        
        # 批量创建数据库记录
        Blessing.bulk_create(blessing_objects)
        
        return blessing_objects
        
    except Exception as e:
        raise Exception(f"生成祝福失败: {str(e)}")
