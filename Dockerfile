# 基础构建阶段
FROM python:3.10.12-slim as builder

WORKDIR /install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -t /install/packages

# 运行阶段
FROM python:3.10.12-slim

WORKDIR /app

# 从builder阶段复制已安装的依赖
COPY --from=builder /install/packages /usr/local/lib/python3.10/site-packages/

# 复制应用代码
COPY app_server ./app_server

# 创建配置文件和证书目录
RUN mkdir -p /app/config /app/logs

# 复制启动脚本
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 设置环境变量
ENV PYTHONPATH=/app:/app/config

# 使用启动脚本
ENTRYPOINT ["/app/entrypoint.sh"]

# flask db migrate 
# flask db upgrade