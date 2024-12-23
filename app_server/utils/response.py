from flask import jsonify
from typing import Any, Optional, Union, Dict


def success_response(
    data: Any = None,
    message: str = "操作成功",
    code: int = 200
) -> Dict:
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
        code: 状态码
    """
    response = {
        "code": code,
        "msg": message,
        "success": True
    }
    
    if data is not None:
        response["datas"] = data
        
    return jsonify(response)


def error_response(
    message: str = "操作失败",
    code: int = 400,
    data: Optional[Any] = None
) -> Dict:
    """
    错误响应
    
    Args:
        message: 错误消息
        code: 错误码
        data: 额外的错误数据
    """
    response = {
        "code": code,
        "msg": message,
        "success": False
    }
    
    if data is not None:
        response["datas"] = data
        
    return jsonify(response)


def general_response(
    success: bool = True,
    code: int = 200,
    message: str = "",
    data: Any = None
) -> Dict:
    """
    通用响应函数
    
    Args:
        success: 是否成功
        code: 状态码
        message: 响应消息
        data: 响应数据
    """
    response = {
        "code": code,
        "msg": message,
        "success": success
    }
    
    if data is not None:
        response["datas"] = data
        
    return jsonify(response) 