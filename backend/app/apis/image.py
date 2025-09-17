from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
import base64
import requests
from datetime import datetime
from io import BytesIO
from PIL import Image

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
        validation_result = self._validate_base64_image(image_data)
        if not validation_result['valid']:
            current_app.logger.error(f"图片数据验证失败: {validation_result['message']}")
            return APIResponse.error(f"数据中未找到图片: {validation_result['message']}")

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

    def _validate_base64_image(self, image_data):
        """详细验证base64图片数据并返回验证结果"""
        try:
            current_app.logger.info(f"开始验证图片数据，数据长度: {len(image_data) if image_data else 0}")
            
            if not image_data:
                return {'valid': False, 'message': '图片数据为空'}
            
            if not isinstance(image_data, str):
                return {'valid': False, 'message': '图片数据必须是字符串格式'}
            
            # 检查是否包含data URL前缀
            if image_data.startswith('data:image'):
                current_app.logger.info("检测到data URL格式")
                if ',' not in image_data:
                    return {'valid': False, 'message': 'data URL格式错误，缺少逗号分隔符'}
                
                # 提取base64部分
                try:
                    header, base64_part = image_data.split(',', 1)
                    current_app.logger.info(f"data URL头部: {header}")
                except ValueError:
                    return {'valid': False, 'message': 'data URL格式错误，无法分割'}
            else:
                base64_part = image_data
                current_app.logger.info("检测到纯base64格式")
            
            # 验证base64编码
            try:
                decoded = base64.b64decode(base64_part)
                current_app.logger.info(f"base64解码成功，数据大小: {len(decoded)} bytes")
            except Exception as e:
                return {'valid': False, 'message': f'base64解码失败: {str(e)}'}
            
            # 检查解码后的数据大小
            if len(decoded) < 100:
                return {'valid': False, 'message': f'解码后数据太小: {len(decoded)} bytes'}
            
            # 检查是否为图片格式（简单的魔数检查）
            if not self._check_image_format(decoded):
                return {'valid': False, 'message': '数据不是有效的图片格式'}
            
            current_app.logger.info("图片数据验证成功")
            return {'valid': True, 'message': '图片数据验证成功'}
            
        except Exception as e:
            current_app.logger.error(f"图片数据验证异常: {str(e)}")
            return {'valid': False, 'message': f'验证过程异常: {str(e)}'}
    
    def _check_image_format(self, data):
        """检查数据是否为常见图片格式"""
        if len(data) < 8:
            return False
        
        # 检查常见图片格式的魔数
        magic_numbers = [
            b'\xFF\xD8\xFF',  # JPEG
            b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A',  # PNG
            b'\x47\x49\x46\x38',  # GIF
            b'\x42\x4D',  # BMP
            b'\x52\x49\x46\x46'  # WEBP (部分)
        ]
        
        for magic in magic_numbers:
            if data.startswith(magic):
                return True
        
        return False

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


class ImageUrlToBase64Resource(Resource):
    """图片URL转Base64接口 - 用于"修改此图"功能"""

    @jwt_required()
    def post(self):
        """将图片URL转换为base64格式"""
        user_id = get_jwt_identity()
        data = request.get_json()

        # 参数验证
        if not data or 'image_url' not in data:
            return APIResponse.error('缺少必需参数: image_url')

        image_url = data.get('image_url', '').strip()
        if not image_url:
            return APIResponse.error('图片URL不能为空')

        # 验证URL格式
        if not image_url.startswith(('http://', 'https://')):
            return APIResponse.error('图片URL格式无效')

        try:
            current_app.logger.info(f"用户 {user_id} 开始转换图片URL: {image_url}")

            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/*,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }

            # 下载图片
            response = requests.get(image_url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()

            # 检查Content-Type
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                return APIResponse.error('URL指向的不是有效的图片文件')

            # 检查文件大小
            content_length = response.headers.get('Content-Length')
            if content_length:
                file_size = int(content_length)
                # 限制图片大小为10MB
                if file_size > 10 * 1024 * 1024:
                    return APIResponse.error('图片文件过大，最大支持10MB')

            # 读取图片数据
            image_data = response.content
            
            # 检查实际大小
            if len(image_data) > 10 * 1024 * 1024:
                return APIResponse.error('图片文件过大，最大支持10MB')

            if len(image_data) < 100:
                return APIResponse.error('图片数据过小，可能不是有效的图片文件')

            # 使用PIL验证图片格式并获取信息
            try:
                image_io = BytesIO(image_data)
                pil_image = Image.open(image_io)
                pil_image.verify()  # 验证图片完整性
                
                # 重新打开获取信息（verify后需要重新打开）
                image_io.seek(0)
                pil_image = Image.open(image_io)
                
                width, height = pil_image.size
                format_name = pil_image.format.lower() if pil_image.format else 'unknown'
                
                current_app.logger.info(f"图片信息: {width}x{height}, 格式: {format_name}, 大小: {len(image_data)} bytes")
                
            except Exception as img_error:
                current_app.logger.error(f"图片验证失败: {str(img_error)}")
                return APIResponse.error('图片文件格式无效或已损坏')

            # 转换为base64
            base64_data = base64.b64encode(image_data).decode('utf-8')
            
            # 确定MIME类型
            mime_type = content_type if content_type.startswith('image/') else 'image/png'
            
            # 构建完整的data URL
            data_url = f"data:{mime_type};base64,{base64_data}"

            current_app.logger.info(f"图片转换成功，用户: {user_id}")

            return APIResponse.success(
                data={
                    'base64': base64_data,  # 纯base64数据
                    'dataUrl': data_url,    # 完整的data URL
                    'mimeType': mime_type,  # MIME类型
                    'width': width,         # 图片宽度
                    'height': height,       # 图片高度
                    'size': len(image_data),# 文件大小
                    'format': format_name   # 图片格式
                },
                message='图片转换成功'
            )

        except requests.RequestException as e:
            current_app.logger.error(f"下载图片失败: {str(e)}")
            if "timeout" in str(e).lower():
                return APIResponse.error('下载图片超时，请重试')
            elif "404" in str(e):
                return APIResponse.error('图片不存在或已被删除')
            elif "403" in str(e):
                return APIResponse.error('没有权限访问该图片')
            else:
                return APIResponse.error('下载图片失败，请检查URL是否正确')
        
        except Exception as e:
            current_app.logger.error(f"图片转换失败: {str(e)}")
            return APIResponse.error('图片转换失败，请重试', code=500)
