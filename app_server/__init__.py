from http import HTTPStatus

from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS

from app_server.db import db
from app_server.routes.user import user_bp
from app_server.routes.wechat import wechat_bp
from app_server.routes.target import target_bp
from app_server.routes.blessing import blessing_bp

from config import Config
from flask_jwt_extended import JWTManager

app = Flask(__name__)
CORS(app, supports_credentials=True)
# 数据库的变量
app.config['SQLALCHEMY_DATABASE_URI'] = Config.MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # 设置sqlalchemy自动更新跟踪数据库

# JWT部分
app.config['JWT_SECRET_KEY'] = Config.JWT_KEY
# 配置JWT过期时间
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.JWT_EXPIRE

# 注册JWT
jwt = JWTManager(app)

# 注册路由
app.register_blueprint(user_bp)
app.register_blueprint(wechat_bp)
app.register_blueprint(target_bp)
app.register_blueprint(blessing_bp)


# 连接数据库
with app.app_context():
    # 初始化数据库
    db.init_app(app)
    # db.drop_all() #删除所有的表
    # db.create_all()  # 创建所有的表

migrate = Migrate(app, db)


@app.route('/')
def index():
    return {
        "code": HTTPStatus.OK,
        "msg": "success",
        "datas": {
        }
    }

