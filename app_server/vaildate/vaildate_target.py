
# 文本内容安全识别
# https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/sec-center/sec-check/msgSecCheck.html


def validate_target_data(data):
    if not data.get('title'):
        return '目标标题不能为空'

        
    return None 