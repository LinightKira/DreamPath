from app_server.utils.coze import chat_with_coze_bot

def test_simple_chat():
    """
    简单的coze机器人对话测试
    """
    bot_id = "7436719685871353868"  # 替换为实际的机器人ID
    user_id = "test_user_001"
    message = "你好，请介绍一下你自己"
    
    response = chat_with_coze_bot(
        bot_id=bot_id,
        user_id=user_id,
        message=message
    )
    
    print("机器人回复：")
    print(response)
    if response.get("messages"):
        print(response["messages"][-1]["content"])
    else:
        print("错误响应:", response)

if __name__ == "__main__":
    test_simple_chat()
