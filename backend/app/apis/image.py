from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
import base64
from datetime import datetime

from app import db, APIResponse
from app.models.image_records import ImageRecord
from app.models.user_storage import UserStorage, update_storage_on_image_save, \
    update_storage_on_image_delete
from app.utils.oss_service import oss_service


class ImageSaveResource(Resource):
    """图片保存接口 - 前端绘图成功后调用"""

    @jwt_required()
    def post(self):
        """保存AI生成的图片"""
        user_id = get_jwt_identity()
        data = request.get_json()

        # 参数验证
        required_fields = ['image_data', 'prompt', 'model']
        for field in required_fields:
            if field not in data:
                return APIResponse.error(f'缺少必需参数: {field}')

        image_data = data.get('image_data')
        prompt = data.get('prompt', '').strip()
        model = data.get('model', '').strip()
        elapsed_time = data.get('elapsed_time', '')
        base_url = data.get('base_url', '')
        api_key = data.get('api_key', '')

        # 参数长度验证
        if len(prompt) > 2000:
            return APIResponse.error('提示词长度不能超过2000字符')

        if len(model) > 100:
            return APIResponse.error('模型名称长度不能超过100字符')

        # 验证base64格式
        if not self._is_valid_base64_image(image_data):
            return APIResponse.error('无效的图片数据格式')

        # 检查用户存储空间
        storage = UserStorage.query.filter_by(user_id=user_id).first()
        if not storage:
            return APIResponse.error('用户存储信息不存在')

        # 估算图片大小
        try:
            base64_part = image_data.split(',')[1] if ',' in image_data else image_data
            estimated_size = len(base64.b64decode(base64_part))
        except Exception:
            return APIResponse.error('图片数据解析失败')

        # 检查存储限制
        if not storage.can_upload(estimated_size):
            return APIResponse.error('存储空间不足或图片数量已达上限')

        try:
            # 上传到OSS
            current_app.logger.info(f"用户 {user_id} 开始上传图片，预估大小: {estimated_size} bytes")

            upload_result = oss_service.upload_base64_image(
                base64_data=image_data,
                user_id=user_id,
                folder='ai-images'
            )

            if not upload_result['success']:
                current_app.logger.error(f"OSS上传失败: {upload_result['message']}")
                return APIResponse.error(f"图片上传失败: {upload_result['message']}")

            # 保存图片记录到数据库
            image_record = ImageRecord(
                user_id=user_id,
                prompt=prompt,
                model=model,
                base_url=base_url,
                api_key=api_key,
                image_url=upload_result['url'],
                image_filename=upload_result['filename'],
                elapsed_time=elapsed_time,
                model_response=data.get('model_response', ''),
                image_width=upload_result.get('width'),
                image_height=upload_result.get('height'),
                image_size=upload_result['size']
            )

            db.session.add(image_record)
            db.session.flush()  # 获取生成的image_id

            # 更新存储使用量
            update_storage_on_image_save(user_id, upload_result['size'])

            db.session.commit()

            current_app.logger.info(f"图片保存成功: {image_record.image_id}")

            return APIResponse.success(
                data={
                    'image': image_record.to_simple_dict(),
                    'storage': storage.to_dict()
                },
                message='图片保存成功'
            )

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"保存图片记录失败: {str(e)}")
            return APIResponse.error('保存失败，请稍后重试', code=500)

    def _is_valid_base64_image(self, data):
        """验证是否为有效的base64图片数据"""
        try:
            if data.startswith('data:image'):
                if ',' in data:
                    data = data.split(',')[1]
                else:
                    return False

            decoded = base64.b64decode(data)
            return len(decoded) > 100  # 至少100字节

        except Exception:
            return False


class ImageListResource(Resource):
    """用户图片列表接口 - 最多返回20条"""

    @jwt_required()
    def get(self):
        """获取用户的图片列表（最多20条）"""
        user_id = get_jwt_identity()

        # 查询参数
        simple = request.args.get('simple', 'false').lower() == 'true'

        try:
            # 查询最新的20条图片记录（排除软删除）
            images = ImageRecord.query.filter_by(user_id=user_id).filter(
                ImageRecord.deleted_at.is_(None)
            ).order_by(ImageRecord.created_at.desc()).limit(20).all()

            # 根据simple参数决定返回数据格式
            if simple:
                image_list = [image.to_simple_dict() for image in images]
            else:
                image_list = [image.to_dict() for image in images]

            return APIResponse.success(
                data={
                    'images': image_list,
                    'total': len(image_list)
                }
            )

        except Exception as e:
            current_app.logger.error(f"获取图片列表失败: {str(e)}")
            return APIResponse.error('获取失败，请稍后重试', code=500)


class ImageDetailResource(Resource):
    """图片详情接口"""

    @jwt_required()
    def get(self, image_id):
        """根据业务ID获取图片详情"""
        user_id = get_jwt_identity()

        try:
            image_record = ImageRecord.query.filter_by(
                image_id=image_id,
                user_id=user_id
            ).filter(ImageRecord.deleted_at.is_(None)).first()

            if not image_record:
                return APIResponse.not_found('图片不存在')

            return APIResponse.success(data={'image': image_record.to_dict()})

        except Exception as e:
            current_app.logger.error(f"获取图片详情失败: {str(e)}")
            return APIResponse.error('获取失败，请稍后重试', code=500)


class ImageUpdateResource(Resource):
    """图片更新接口"""

    @jwt_required()
    def put(self, image_id):
        """更新图片信息（主要是prompt）"""
        user_id = get_jwt_identity()
        data = request.get_json()

        try:
            image_record = ImageRecord.query.filter_by(
                image_id=image_id,
                user_id=user_id
            ).filter(ImageRecord.deleted_at.is_(None)).first()

            if not image_record:
                return APIResponse.not_found('图片不存在')

            # 更新允许修改的字段
            if 'prompt' in data:
                prompt = data['prompt'].strip()
                if len(prompt) > 2000:
                    return APIResponse.error('提示词长度不能超过2000字符')
                image_record.prompt = prompt

            image_record.updated_at = datetime.utcnow()
            db.session.commit()

            return APIResponse.success(
                data={'image': image_record.to_dict()},
                message='图片信息更新成功'
            )

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"更新图片失败: {str(e)}")
            return APIResponse.error('更新失败，请稍后重试', code=500)


class ImageDeleteResource(Resource):
    """图片删除接口 - 软删除"""

    @jwt_required()
    def delete(self, image_id):
        """根据业务ID软删除图片"""
        user_id = get_jwt_identity()

        try:
            # 查找图片记录
            image_record = ImageRecord.query.filter_by(
                image_id=image_id,
                user_id=user_id
            ).filter(ImageRecord.deleted_at.is_(None)).first()

            if not image_record:
                return APIResponse.not_found('图片不存在')

            # 软删除（标记删除时间）
            image_record.deleted_at = datetime.utcnow()

            # 更新存储使用量
            update_storage_on_image_delete(user_id, image_record.image_size or 0)

            db.session.commit()

            # 异步删除OSS文件（可选，避免影响响应速度）
            if image_record.image_filename:
                try:
                    delete_result = oss_service.delete_file(image_record.image_filename)
                    if not delete_result['success']:
                        current_app.logger.warning(f"OSS删除失败: {delete_result['message']}")
                except Exception as oss_error:
                    current_app.logger.warning(f"OSS删除异常: {str(oss_error)}")

            current_app.logger.info(f"图片软删除成功: {image_id}")

            return APIResponse.success(message='图片删除成功')

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"删除图片失败: {str(e)}")
            return APIResponse.error('删除失败，请稍后重试', code=500)
