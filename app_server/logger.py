"""
@Time        : 2024/12/23 9:47
@Author      : LinightX
@File        : logger.py
@Description : 日志包
"""

# 创建日志器
import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger("dreampath")

# 设置日志级别
logger.setLevel(logging.INFO)

# 自动创建目录
if not os.path.exists('logs'):
    os.makedirs('logs')

# 定义日志文件的名称和位置
log_file = 'dreampath__{date}.log'.format(date=datetime.now().strftime('%Y-%m-%d'))
log_dir = 'logs'

# 创建 handlers
f_handler = TimedRotatingFileHandler(os.path.join(log_dir, log_file), when='midnight', interval=1, backupCount=30,
                                     encoding='utf-8')
f_handler.setLevel(logging.INFO)

# 创建格式器并添加到handlers
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_format.encoding = 'utf-8'  # 设置编码

f_handler.setFormatter(f_format)

# 添加 handlers到日志器
logger.addHandler(f_handler)

# 添加控制台输出
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.INFO)
c_handler.setFormatter(f_format)
logger.addHandler(c_handler)
