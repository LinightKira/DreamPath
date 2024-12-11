
from app_server.utils.coze import run_coze_workflow

# 测试函数
def test_coze_workflow():
    """测试Coze workflow执行"""
    workflow_id = '7446712246850306075'
    parameters = {
        "param1": "value1",
        "param2": "value2"
    }
    
    result = run_coze_workflow(workflow_id, parameters)
    print("测试结果:", result)


if __name__ == "__main__":
    test_coze_workflow()
