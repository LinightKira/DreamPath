from datetime import timedelta


class Config:
    TESTING_MODE = False  # 默认关闭测试模式

    # mysql
    MYSQL_HOST = '127.0.0.1'  # 127.0.0.1/localhost
    MYSQL_PORT = 3306
    MYSQL_DATA_BASE = 'Happiness'
    MYSQL_USER = 'root'  # root
    MYSQL_PWD = '1234567'  # Freedom7
    MYSQL_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PWD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATA_BASE}?charset=utf8'

    # wx_app
    APP_ID = 'wxabcdefghijk'
    SECRET = 'abcdefghijk'

    # JWT
    JWT_KEY = 'abcdefghijk'
    JWT_EXPIRE = timedelta(days=2)

