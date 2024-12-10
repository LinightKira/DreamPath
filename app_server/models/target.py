from datetime import datetime
from app_server.db import Base, db


class Target(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="自增主键")
    title = db.Column(db.String(255), comment="目标标题")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), comment="创建者id")
    desc = db.Column(db.String(255), comment="目标描述")
    deadline = db.Column(db.DateTime, comment="目标截止时间")
    priority = db.Column(db.Integer, default=0, comment="优先级: 0-低, 1-中, 2-高")
    progress = db.Column(db.Integer, default=0, comment="目标完成进度(0-100)")
    is_completed = db.Column(db.Boolean, default=False, comment="是否完成")

    # 单向一对多引用
    tasks = db.relationship("Task", order_by="Task.step")


def GetTargetById(tid):
    return Target.query.get(tid) 