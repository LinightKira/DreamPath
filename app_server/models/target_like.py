from app_server.db import Base, db
from app_server.models.target import Target
from app_server.models.user import User


class TargetLike(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="自增主键")
    target_id = db.Column(db.Integer, db.ForeignKey('target.id', ondelete='CASCADE'), 
                         nullable=False, comment="愿望ID")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), 
                       nullable=False, comment="用户ID")

    # 建立唯一索引，确保同一用户不能重复祝福同一愿望
    __table_args__ = (
        db.UniqueConstraint('target_id', 'user_id', name='uk_target_user'),
    )

    # 建立与Target的关系
    target = db.relationship("Target", backref=db.backref('likes', lazy='dynamic'))
    # 建立与User的关系
    user = db.relationship("User", backref=db.backref('target_likes', lazy='dynamic'))


def create_target_like(target_id, user_id):
    """创建祝福记录"""
    try:
        # 首先检查愿望是否存在
        target = Target.query.get(target_id)
        if not target:
            print(f"愿望不存在: target_id={target_id}")
            return False
            
        # 检查用户是否存在
        user = User.query.get(user_id)
        if not user:
            print(f"用户不存在: user_id={user_id}")
            return False
            
        # 检查是否已经点过赞
        existing_like = TargetLike.query.filter_by(
            target_id=target_id, 
            user_id=user_id
        ).first()
        if existing_like:
            print(f"用户已经点过赞: user_id={user_id}, target_id={target_id}")
            return False

        # 创建新的祝福记录
        like = TargetLike(target_id=target_id, user_id=user_id)
        db.session.add(like)
        target.likes_count += 1
        db.session.commit()
        return True
        
    except Exception as e:
        print(f"祝福失败: {str(e)}")
        db.session.rollback()
        return False

def delete_target_like(target_id, user_id):
    """删除祝福记录"""
    try:
        like = TargetLike.query.filter_by(target_id=target_id, user_id=user_id).first()
        if like:
            db.session.delete(like)
            # 更新愿望的祝福计数
            target = like.target
            target.likes_count = max(0, target.likes_count - 1)
            db.session.commit()
            return True
        return False
    except Exception:
        db.session.rollback()
        return False