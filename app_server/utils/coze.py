import json
import requests
from config import Config
from app_server.logger import logger_runner


# https://www.coze.cn/docs/developer_guides/workflow_run
def run_coze_workflow(workflow_id: str, parameters: dict) -> dict:
    """
    执行Coze workflow
    
    Args:
        workflow_id: workflow的ID
        parameters: 传递给workflow的参数
        
    Returns:
        dict: API响应结果
    """
    logger_runner.info(f"开始执行Coze workflow, workflow_id: {workflow_id}, parameters: {parameters}")
    
    try:
        url = "https://api.coze.cn/v1/workflow/run"
        
        headers = {
            "Authorization": f"Bearer {Config.COZE_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "workflow_id": workflow_id,
            "parameters": parameters
        }
        
        logger_runner.debug(f"发送请求到Coze API, url: {url}, payload: {payload}")
        
        response = requests.post(
            url=url,
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            result = response.json()
            logger_runner.info(f"Coze workflow执行成功, 响应结果: {result}")
            return result
        else:
            error_msg = f"Coze API调用失败: {response.status_code} - {response.text}"
            logger_runner.error(error_msg)
            return {
                "success": False,
                "error": f"API调用失败: {response.status_code}"
            }
            
    except Exception as e:
        error_msg = f"执行Coze workflow时发生错误: {str(e)}"
        logger_runner.error(error_msg)
        return {
            "success": False,
            "error": f"执行出错: {str(e)}"
        }


def chat_with_coze_bot(bot_id: str, user_id: str, message: str, auto_save_history: bool = True) -> dict:
    """
    与Coze聊天机器人进行对话
    
    Args:
        bot_id: 聊天机器人的ID
        user_id: 用户ID
        message: 用户发送的消息
        auto_save_history: 是否自动保存对话历史，默认为True
        
    Returns:
        dict: API响应结果
    """
    logger_runner.info(f"开始与Coze机器人对话, bot_id: {bot_id}, user_id: {user_id}, message: {message}")
    
    try:
        url = "https://api.coze.cn/v3/chat"
        
        headers = {
            "Authorization": f"Bearer {Config.COZE_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "bot_id": bot_id,
            "user_id": user_id,
            "stream": False,
            "auto_save_history": auto_save_history,
            "additional_messages": [
                {
                    "role": "user",
                    "content": message,
                    "content_type": "text"
                }
            ]
        }
        
        logger_runner.debug(f"发送请求到Coze聊天API, url: {url}, payload: {payload}")
        
        response = requests.post(
            url=url,
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            result = response.json()
            logger_runner.info(f"Coze聊天请求成功, 响应结果: {result}")
            return result
        else:
            error_msg = f"Coze聊天API调用失败: {response.status_code} - {response.text}"
            logger_runner.error(error_msg)
            return {
                "success": False,
                "error": f"API调用失败: {response.status_code}"
            }
            
    except Exception as e:
        error_msg = f"调用Coze聊天机器人时发生错误: {str(e)}"
        logger_runner.error(error_msg)
        return {
            "success": False,
            "error": f"执行出错: {str(e)}"
        }


