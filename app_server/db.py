from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Base(db.Model):
    __abstract__ = True

    status = db.Column(db.Integer, default=1, comment="状态")  # 0删除 1正常
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    @classmethod
    def to_model(cls, **kwargs):
        value = Base()
        columns = [c.name for c in cls.__table__.columns]  # 获取模型定义的所有列属性的名字
        for k, v in kwargs.items():  # 遍历传入kwargs的键值
            if k in columns:  # 如果键包含在列名中，则为该对象赋加对应的属性值
                setattr(value, k, v)
        return value

    # 模型到字典转化
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def save(self):
        """保存对象到数据库"""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def update(self, **kwargs):
        """更新对象属性并保存到数据库
        
        Args:
            **kwargs: 需要更新的字段和值的键值对
            
        Raises:
            Exception: 数据库操作异常时抛出
        """
        try:
            # 获取当前模型的所有列名
            columns = [c.name for c in self.__table__.columns]
            
            # 只更新存在的字段
            for key, value in kwargs.items():
                if key in columns:
                    setattr(self, key, value)
            
            # 自动更新update_time
            self.update_time = datetime.now()
            
            # 保存到数据库
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

