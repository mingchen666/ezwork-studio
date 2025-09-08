from datetime import datetime
from app import db


class SendCode(db.Model):
    """ 验证码发送记录表 """
    __tablename__ = 'send_code'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    is_used = db.Column(db.Boolean, default=False)

    send_type = db.Column(db.Integer, nullable=False)               # 发送类型（1=邮件改密）[^4]
    send_to = db.Column(db.String(100), nullable=False)             # 接收地址（邮箱/手机）
    code = db.Column(db.String(6), nullable=False)                  # 验证码（6位）
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)# 创建时间
    expires_at = db.Column(db.DateTime, nullable=False)  # 移除 onupdate
    def is_expired(self):
        """检查是否过期"""
        return datetime.utcnow() > self.expires_at

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'send_type': self.send_type,
            'send_to': self.send_to,
            'is_used': self.is_used,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }




