from datetime import datetime
from app_server.db import Base, db


class Target(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="自增主键")
    title = db.Column(db.String(255), comment="目标标题")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), comment="创建者id")
    desc = db.Column(db.String(255), comment="目标描述")
    deadline = db.Column(db.DateTime, comment="目标截止时间")
    progress = db.Column(db.Integer, default=0, comment="目标完成进度(0-100)")
    is_completed = db.Column(db.Boolean, default=False, comment="是否完成")
    complete_time = db.Column(db.DateTime, nullable=True, comment="目标完成时间")
    c_type = db.Column(db.String(50), nullable=False, default='normal', comment="目标类型")
    parent_id = db.Column(db.Integer, db.ForeignKey('target.id'), nullable=True, comment="父级目标ID")
    likes_count = db.Column(db.BigInteger, default=0, comment="点赞数")

    # # 修改关系定义，使用字符串方式引用
    # tasks = db.relationship(
    #     "Task",
    #     order_by="Task.step",
    #     backref=db.backref("target", lazy="joined"),
    #     lazy="select"
    # )
    # children = db.relationship(
    #     "Target",
    #     backref=db.backref('parent', remote_side=[id]),
    #     cascade="all, delete-orphan",
    #     lazy="select"
    # )


def GetTargetById(tid):
    return Target.query.get(tid) 