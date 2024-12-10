def validate_target_data(data):
    if not data.get('title'):
        return '目标标题不能为空'
    
    if not data.get('deadline'):
        return '截止时间不能为空'
        
    return None 