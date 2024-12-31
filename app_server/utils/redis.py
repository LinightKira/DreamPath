
from redis import Redis
from config.config import Config

# 初始化redis
redis_client = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DB, password=Config.REDIS_PASSWORD)
