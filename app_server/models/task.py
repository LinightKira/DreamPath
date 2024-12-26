from app_server.db import Base, db


class Task(Base):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="自增主键")
    title = db.Column(db.String(255), comment="任务标题")
    desc = db.Column(db.Text, comment="任务描述")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), comment="创建者id")
    target_id = db.Column(db.Integer, db.ForeignKey('target.id'), comment="所属目标id")
    
    # 任务顺序和进度相关
    step = db.Column(db.Integer, comment="任务步骤顺序")
    deadline = db.Column(db.DateTime, comment="任务截止时间")
    is_completed = db.Column(db.Boolean, default=False, comment="是否完成")
    completion_time = db.Column(db.DateTime, comment="完成时间")
    
    # 任务解锁相关
    is_locked = db.Column(db.Boolean, default=True, comment="是否锁定")
    unlock_condition = db.Column(db.String(255), comment="解锁条件描述")
    dependent_tasks = db.Column(db.String(255), comment="依赖的前置任务ID列表,逗号分隔")
    

    def check_unlock_condition(self):
        """检查任务是否可以解锁"""
        if not self.dependent_tasks:
            return True
            
        dependent_ids = [int(x) for x in self.dependent_tasks.split(',')]
        for task_id in dependent_ids:
            task = Task.query.get(task_id)
            if not task or not task.is_completed:
                return False
        return True

def GetTaskById(tid):
    return Task.query.get(tid) 