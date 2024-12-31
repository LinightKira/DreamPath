from datetime import timedelta


class Config:

    TESTING_MODE = False  # 默认关闭测试模式

    # mysql
    MYSQL_HOST = 'host.docker.internal'  # 127.0.0.1/localhost/host.docker.internal
    MYSQL_PORT = 3306
    MYSQL_DATA_BASE = 'tablename'
    MYSQL_USER = 'root'  # root
    MYSQL_PWD = ''  # Freedom7
    MYSQL_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PWD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATA_BASE}?charset=utf8'

    # wx_app
    APP_ID = 'w'
    SECRET = ''

    # JWT
    JWT_KEY = '12345'
    JWT_EXPIRE = timedelta(days=1)

    # Coze
    COZE_TOKEN = ''
    WorkFlowID_ZF = ''
    WorkFlowID_ZFSH = ''    
    WorkFlowID_Image= ''

    # redis
    REDIS_HOST = '127.0.0.1'  # Redis 服务器地址
    REDIS_PORT = 6379          # Redis 端口
    REDIS_DB = 0               # Redis 数据库编号
    REDIS_PASSWORD = None       # Redis 密码（如果有的话）


    #Target
    DEFAULT_TARGET_IMAGE_URL=''



