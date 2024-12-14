
from app_server.utils.coze import run_coze_workflow

# 测试函数
def test_coze_workflow():
    """测试Coze workflow执行"""
    workflow_id = '7448110390871212082'
    parameters = {
        "input": "创业成功",
    }
    
    result = run_coze_workflow(workflow_id, parameters)
    print("测试结果:", result)


if __name__ == "__main__":
    test_coze_workflow()


# 测试结果: {'code': 0, 'cost': '0', 'data': '{"output":"Hello World"}', 'debug_url': 'https://www.coze.cn/work_flow?execute_id=7446974137510608933&space_id=7394713883296432182&workflow_id=7446712246850306075', 'msg': 'Success', 'token': 0}