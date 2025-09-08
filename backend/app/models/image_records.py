from datetime import datetime
from app import db
from app.utils.id_generator import generate_image_id


class ImageRecord(db.Model):
    """图片记录表"""
    __tablename__ = 'image_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_id = db.Column(db.String(20), unique=True, nullable=False, default=generate_image_id)
    # 生成信息
    prompt = db.Column(db.Text, nullable=False)
    model = db.Column(db.String(100), nullable=False)
    base_url = db.Column(db.String(100))
    api_key = db.Column(db.String(100))
    # 图片信息
    image_url = db.Column(db.String(500), nullable=False)
    image_filename = db.Column(db.String(255))

    # 其他信息
    elapsed_time = db.Column(db.String(10))  # 如 "2.5s"
    model_response = db.Column(db.Text)
    # 图片元数据
    image_width = db.Column(db.Integer)
    image_height = db.Column(db.Integer)
    image_size = db.Column(db.Integer)  # 文件大小（字节）

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'prompt': self.prompt,
            'model': self.model,
            'image_url': self.image_url,
            'image_filename': self.image_filename,
            'elapsed_time': self.elapsed_time,
            'image_width': self.image_width,
            'image_height': self.image_height,
            'model_response': self.model_response,
            'image_size': self.image_size,
            'created_at': self.created_at.isoformat(),
            'timestamp': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'sortTimestamp': int(self.created_at.timestamp() * 1000)
        }

    def to_simple_dict(self):
        """简化版本，用于列表展示"""
        return {
            'image_id': self.image_id,
            'model': self.model,
            'prompt': self.prompt[:50] + '...' if len(self.prompt) > 50 else self.prompt,
            'image_url': self.image_url,
            'model_response': self.model_response,
            'elapsed_time': self.elapsed_time,
            'created_at': self.created_at.isoformat(),
            'sortTimestamp': int(self.created_at.timestamp() * 1000)
        }
