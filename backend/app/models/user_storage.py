from datetime import datetime
from app import db


class UserStorage(db.Model):
    """用户存储信息表"""
    __tablename__ = 'user_storage'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    # 存储配额（字节）
    total_storage = db.Column(db.BigInteger, default=1024 * 1024 * 1024)  # 默认1GB
    used_storage = db.Column(db.BigInteger, default=0)  # 已使用空间

    # 图片数量限制
    max_images = db.Column(db.Integer, default=100)  # 最大图片数量
    current_images = db.Column(db.Integer, default=0)  # 当前图片数量

    # 单个文件大小限制（字节）
    max_file_size = db.Column(db.Integer, default=10 * 1024 * 1024)  # 默认10MB

    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_remaining_space(self):
        """获取剩余空间"""
        return max(0, self.total_storage - self.used_storage)

    def get_usage_percentage(self):
        """获取使用率百分比"""
        if self.total_storage == 0:
            return 0
        return round((self.used_storage / self.total_storage) * 100, 2)

    def can_upload(self, file_size):
        """检查是否可以上传指定大小的文件"""
        return (
                file_size <= self.max_file_size and
                file_size <= self.get_remaining_space() and
                self.current_images < self.max_images
        )

    def add_usage(self, file_size):
        """增加使用量"""
        self.used_storage += file_size
        self.current_images += 1
        db.session.commit()

    def remove_usage(self, file_size):
        """减少使用量"""
        self.used_storage = max(0, self.used_storage - file_size)
        self.current_images = max(0, self.current_images - 1)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'total_storage': self.total_storage,
            'used_storage': self.used_storage,
            'remaining_space': self.get_remaining_space(),
            'usage_percentage': self.get_usage_percentage(),
            'max_images': self.max_images,
            'current_images': self.current_images,
            'max_file_size': self.max_file_size,
            'updated_at': self.updated_at.isoformat()
        }


# 更新存储使用量的辅助函数
def update_storage_on_image_save(user_id, image_size):
    """保存图片时更新存储使用量"""
    storage = UserStorage.query.filter_by(user_id=user_id).first()
    if storage:
        storage.add_usage(image_size)
        return True
    return False


def update_storage_on_image_delete(user_id, image_size):
    """删除图片时更新存储使用量"""
    storage = UserStorage.query.filter_by(user_id=user_id).first()
    if storage:
        storage.remove_usage(image_size)
        return True
    return False
