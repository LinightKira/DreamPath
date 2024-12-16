import json
from config import Config
from app_server.utils.coze import run_coze_workflow
# 文本内容安全识别
# https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/sec-center/sec-check/msgSecCheck.html
from config import Config


def validate_target_data(data):
    title = data.get('title')
    if not title:
        return '目标标题不能为空'
        
    # 调用Coze工作流
    parameters = {
            "input": title
    }
    result = run_coze_workflow(Config.WorkFlowID_ZFSH, parameters)
        
    if result['code'] != 0:
        return (f"Coze工作流调用失败: {result['msg']}")
    try:
        data_dict = json.loads(result['data'])   
           
    except json.JSONDecodeError as e:
        return (f"Coze工作流返回数据格式错误: {e}")  
    # 解析返回的数据
    res = data_dict['result']
    print('res',res,type(res))
    if res == False:
        reason  = data_dict['reason']
        if reason:
            return reason
        else:
            return '审核没通过'      
    return None 