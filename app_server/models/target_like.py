from datetime import datetime
from app_server.db import Base, db


class TargetLike(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="自增主键")
    target_id = db.Column(db.Integer, db.ForeignKey('target.id', ondelete='CASCADE'), 
                         nullable=False, comment="目标ID")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), 
                       nullable=False, comment="用户ID")
    created_at = db.Column(db.DateTime, default=datetime.now, comment="点赞时间")

    # 建立唯一索引，确保同一用户不能重复点赞同一目标
    __table_args__ = (
        db.UniqueConstraint('target_id', 'user_id', name='uk_target_user'),
    )

    # 建立与Target的关系
    target = db.relationship("Target", backref=db.backref('likes', lazy='dynamic'))
    # 建立与User的关系
    user = db.relationship("User", backref=db.backref('target_likes', lazy='dynamic'))


def create_target_like(target_id, user_id):
    """创建点赞记录"""
    try:
        like = TargetLike(target_id=target_id, user_id=user_id)
        db.session.add(like)
        # 更新目标的点赞计数
        target = like.target
        target.likes_count += 1
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False

def delete_target_like(target_id, user_id):
    """删除点赞记录"""
    try:
        like = TargetLike.query.filter_by(target_id=target_id, user_id=user_id).first()
        if like:
            db.session.delete(like)
            # 更新目标的点赞计数
            target = like.target
            target.likes_count = max(0, target.likes_count - 1)
            db.session.commit()
            return True
        return False
    except Exception:
        db.session.rollback()
        return False