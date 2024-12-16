from app_server.db import Base, db


class Blessing(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="自增主键")
    target_id = db.Column(db.Integer, db.ForeignKey('target.id', ondelete='CASCADE'), 
                         nullable=False, comment="目标ID")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), 
                       nullable=True, comment="祝福者ID,为空表示系统祝福")
    blesser_name = db.Column(db.String(50), nullable=False, comment="祝福者对用户显示的昵称")
    content = db.Column(db.Text, nullable=False, comment="祝福内容")
    is_system = db.Column(db.Boolean, default=False, comment="是否为系统祝福")

    # 建立与Target的关系
    target = db.relationship("Target", backref=db.backref('blessings', lazy='dynamic'))
    # 建立与User的关系
    user = db.relationship("User", backref=db.backref('blessings', lazy='dynamic'))

    def create(self):
        """创建祝福"""
        try:
            # 如果user_id为空,则标记为系统祝福
            if not self.user_id:
                self.is_system = True
            
            # 如果是用户祝福且没有设置祝福者名字,则使用用户昵称
            if self.user_id and not self.blesser_name:
                from app_server.models.user import User
                user = User.query.get(self.user_id)
                if user:
                    self.blesser_name = user.nickname
                
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            print(f"创建祝福失败: {str(e)}")
            db.session.rollback()
            return False

    @classmethod
    def bulk_create(cls, blessing_objects):
        """批量创建祝福记录
        
        Args:
            blessing_objects: list - Blessing对象列表
        
        Returns:
            bool - 是否创建成功
        """
        
        try:
            # 为所有没有user_id的祝福标记为系统祝福
            for blessing in blessing_objects:
                if not blessing.user_id:
                    blessing.is_system = True
                
                # 如果是用户祝福且没有设置祝福者名字,则使用用户昵称
                if blessing.user_id and not blessing.blesser_name:
                    from app_server.models.user import User
                    user = User.query.get(blessing.user_id)
                    if user:
                        blessing.blesser_name = user.nickname
            
            # 批量添加所有对象
            db.session.bulk_save_objects(blessing_objects)
            db.session.commit()
            return True
        except Exception as e:
            print(f"批量创建祝福失败: {str(e)}")
            db.session.rollback()
            return False


def get_target_blessings(target_id, blessing_type='all'):
        """获取目标的祝福
        
        Args:
            target_id: 目标ID
            blessing_type: 祝福类型,可选值:
                - 'all': 所有祝福(默认)
                - 'system': 仅系统祝福
                - 'user': 仅用户祝福
        
        Returns:
            祝福列表
        """
        query = Blessing.query.filter_by(target_id=target_id)
        
        if blessing_type == 'system':
            query = query.filter_by(is_system=True)
        elif blessing_type == 'user':
            query = query.filter_by(is_system=False)
            
        return query.order_by(Blessing.create_time.desc()).all()
