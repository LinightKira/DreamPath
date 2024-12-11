import requests
import json

def msg_sec_check(access_token, content, openid, scene=1):
    """
    调用微信内容安全检测接口 2.0版本
    
    :param access_token: 微信接口调用凭证
    :param content: 需要检测的文本内容（最大2500字，UTF-8编码）
    :param openid: 用户的openid（用户需在近两小时访问过小程序）
    :param scene: 场景值（1 资料；2 评论；3 论坛；4 社交日志）
    :return: 检测结果
    """
    # 微信内容安全检测API地址
    url = f"https://api.weixin.qq.com/wxa/msg_sec_check?access_token={access_token}"
    
    # 请求体
    data = {
        "content": content,
        "version": 2,  # 2.0版本固定值
        "scene": scene,
        "openid": openid
    }
    
    # 发送请求
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        # 解析检测结果
        if result.get('errcode') == 0:
            print("内容安全检测通过")
            return True
        else:
            print(f"内容可能存在安全风险：{result}")
            return False
    
    except requests.RequestException as e:
        print(f"请求发生错误：{e}")
        return False

# 使用示例
def main():
    # 注意：access_token需要提前获取
    ACCESS_TOKEN = "your_access_token_here"
    TEST_OPENID = "test_user_openid"  # 添加测试用户openid
    
    # 测试文本
    test_contents = [
        "这是一个正常的测试文本",
        "这是一个包含敏感词的文本"
    ]
    
    for content in test_contents:
        print(f"\n正在检测内容：{content}")
        msg_sec_check(ACCESS_TOKEN, content, TEST_OPENID, scene=1)

if __name__ == "__main__":
    main()