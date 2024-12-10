# 新增或更新character时的必填字段校验函数
def validate_theme_data(data):

    if not data.get('title'):
        return 'title is required'

    return None
