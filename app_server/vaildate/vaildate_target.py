import json
from config.config import Config
from app_server.utils.coze import run_coze_workflow
# 文本内容安全识别
# https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/sec-center/sec-check/msgSecCheck.html
from config.config import Config


def validate_target_data(data):
    title = data.get('title')
    if not title:
        return '愿望不能为空'
    
    likes_goal = data.get('likes_goal')
    if not isinstance(likes_goal, int) or likes_goal < 0:
        return '祝福数必须是一个大于等于0的正整数'
    
    # 限制标题字数，最长不超过124个字
    if len(title) > 124:
        return '愿望最长不超过124个字'
        
    # 调用Coze工作流
    parameters = {
        "input": title
    }
    result = run_coze_workflow(Config.WorkFlowID_ZFSH, parameters)
        
    if result['code'] != 0:
        return (f"工作流调用失败: {result['msg']}")
    try:
        data_dict = json.loads(result['data'])   
           
    except json.JSONDecodeError as e:
        return (f"工作流返回数据格式错误: {e}")  
    # 解析返回的数据
    res = data_dict['result']
    # print('res',res,type(res))
    if res == False:
        reason  = data_dict['reason']
        if reason:
            return reason
        else:
            return '审核没通过'      
    return None 