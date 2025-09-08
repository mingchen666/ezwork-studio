import alibabacloud_oss_v2 as oss
import base64
import uuid
import os
from datetime import datetime
from PIL import Image
from io import BytesIO
import tempfile
import logging


class OSSService:
    """阿里云OSS存储服务类 - 独立版本"""

    def __init__(self):
        self.client = None
        self.bucket_name = None
        self.region = None
        self.endpoint = None
        self._initialized = True
        self._init_client()

    def _init_client(self):
        """初始化OSS客户端"""
        try:
            # 从环境变量获取OSS参数
            access_key_id = os.getenv('OSS_ACCESS_KEY_ID')
            access_key_secret = os.getenv('OSS_ACCESS_KEY_SECRET')
            self.region = os.getenv('OSS_REGION', 'cn-hangzhou')
            self.bucket_name = os.getenv('OSS_BUCKET_NAME')
            self.endpoint = os.getenv('OSS_ENDPOINT')  # 可选

            if not all([access_key_id, access_key_secret, self.region, self.bucket_name]):
                missing_vars = []
                if not access_key_id:
                    missing_vars.append('OSS_ACCESS_KEY_ID')
                if not access_key_secret:
                    missing_vars.append('OSS_ACCESS_KEY_SECRET')
                if not self.region:
                    missing_vars.append('OSS_REGION')
                if not self.bucket_name:
                    missing_vars.append('OSS_BUCKET_NAME')

                error_msg = f"缺少OSS环境变量配置: {', '.join(missing_vars)}"
                print(f"OSS初始化失败: {error_msg}")
                logging.error(error_msg)
                return  # 不抛出异常，允许应用继续运行

            # 设置环境变量供SDK使用
            os.environ['OSS_ACCESS_KEY_ID'] = access_key_id
            os.environ['OSS_ACCESS_KEY_SECRET'] = access_key_secret

            # 创建凭证提供者
            credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()

            # 加载默认配置
            cfg = oss.config.load_default()
            cfg.credentials_provider = credentials_provider
            cfg.region = self.region

            # 如果提供了自定义endpoint，则使用自定义endpoint
            if self.endpoint:
                cfg.endpoint = self.endpoint

            # 创建OSS客户端
            self.client = oss.Client(cfg)

            logging.info("OSS服务初始化成功")

        except Exception as e:
            error_msg = f"OSS服务初始化失败: {str(e)}"
            print(error_msg)
            logging.error(error_msg)
            # 不抛出异常，允许应用继续运行

    def is_available(self):
        """检查OSS服务是否可用"""
        return self._initialized and self.client is not None

    def upload_base64_image(self, base64_data, user_id, folder='ai-images'):
        """
        上传base64图片到OSS

        Args:
            base64_data: base64编码的图片数据
            user_id: 用户ID
            folder: 存储文件夹

        Returns:
            dict: 上传结果
        """
        if not self.is_available():
            return {
                'success': False,
                'message': 'OSS服务不可用，请检查配置'
            }

        try:
            print(f"开始上传图片，用户ID: {user_id}")

            # 解码base64数据
            if base64_data.startswith('data:image'):
                # 移除data:image/...;base64,前缀
                base64_data = base64_data.split(',')[1]

            image_bytes = base64.b64decode(base64_data)
            print(f"图片解码成功，大小: {len(image_bytes)} bytes")

            # 生成文件名
            filename = self._generate_filename(user_id, folder)
            print(f"生成文件名: {filename}")

            # 获取图片信息
            image_info = self._get_image_info(image_bytes)
            print(f"图片信息: {image_info}")

            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(image_bytes)
                temp_file_path = temp_file.name

            print(f"创建临时文件: {temp_file_path}")

            try:
                # 上传到OSS
                request = oss.PutObjectRequest(
                    bucket=self.bucket_name,
                    key=filename
                )

                print(f"开始上传到OSS，bucket: {self.bucket_name}, key: {filename}")
                result = self.client.put_object_from_file(request, temp_file_path)
                print(f"OSS上传完成，状态码: {result.status_code}")

                if result.status_code == 200:
                    # 构建访问URL
                    file_url = self._get_file_url(filename)
                    print(f"上传成功，文件URL: {file_url}")

                    return {
                        'success': True,
                        'url': file_url,
                        'filename': filename,
                        'size': len(image_bytes),
                        'width': image_info.get('width'),
                        'height': image_info.get('height'),
                        'format': image_info.get('format'),
                        'etag': result.etag,
                        'request_id': result.request_id,
                        'message': '上传成功'
                    }
                else:
                    return {
                        'success': False,
                        'message': f'上传失败，状态码: {result.status_code}'
                    }
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    print(f"清理临时文件: {temp_file_path}")

        except Exception as e:
            error_msg = f"上传图片失败: {str(e)}"
            print(error_msg)
            logging.error(error_msg)
            return {
                'success': False,
                'message': error_msg
            }

    def delete_file(self, filename):
        """
        删除OSS文件

        Args:
            filename: 文件名（OSS中的key）

        Returns:
            dict: 删除结果
        """
        if not self.is_available():
            return {
                'success': False,
                'message': 'OSS服务不可用，请检查配置'
            }

        try:
            request = oss.DeleteObjectRequest(
                bucket=self.bucket_name,
                key=filename
            )

            result = self.client.delete_object(request)

            if result.status_code == 204:
                return {
                    'success': True,
                    'request_id': result.request_id,
                    'version_id': result.version_id,
                    'delete_marker': result.delete_marker,
                    'message': '删除成功'
                }
            else:
                return {
                    'success': False,
                    'message': f'删除失败，状态码: {result.status_code}'
                }

        except Exception as e:
            error_msg = f"删除文件失败: {str(e)}"
            logging.error(error_msg)
            return {
                'success': False,
                'message': error_msg
            }

    def file_exists(self, filename):
        """
        检查文件是否存在

        Args:
            filename: 文件名

        Returns:
            bool: 文件是否存在
        """
        if not self.is_available():
            return False

        try:
            request = oss.HeadObjectRequest(
                bucket=self.bucket_name,
                key=filename
            )

            result = self.client.head_object(request)
            return result.status_code == 200

        except Exception as e:
            logging.error(f"检查文件存在性失败: {str(e)}")
            return False

    def _generate_filename(self, user_id, folder, original_filename=None):
        """生成唯一文件名"""
        # 生成时间戳路径
        now = datetime.now()
        date_path = now.strftime('%Y/%m/%d')

        # 生成唯一ID
        unique_id = str(uuid.uuid4())

        if original_filename:
            # 保留原始文件扩展名
            _, ext = os.path.splitext(original_filename)
            filename = f"{unique_id}{ext}"
        else:
            # 默认为PNG格式
            filename = f"{unique_id}.png"

        # 构建完整路径: folder/user_id/date/filename
        full_path = f"{folder}/user_{user_id}/{date_path}/{filename}"

        return full_path

    def _get_file_url(self, filename):
        """获取文件访问URL"""
        # 获取并验证自定义域名
        custom_domain = os.getenv('OSS_CUSTOM_DOMAIN', '').strip()

        # 如果自定义域名有效且不为空
        if custom_domain and custom_domain.lower() not in ['null', 'none', 'undefined']:
            # 移除可能的协议前缀
            if custom_domain.startswith(('http://', 'https://')):
                custom_domain = custom_domain.split('://', 1)[1]

            print(f"使用自定义域名: {custom_domain}")
            return f"https://{custom_domain}/{filename}"

        # 使用OSS默认域名
        if self.endpoint:
            # 如果配置了自定义endpoint
            endpoint = self.endpoint
            if endpoint.startswith(('http://', 'https://')):
                endpoint = endpoint.split('://', 1)[1]

            print(f"使用自定义endpoint: {endpoint}")
            return f"https://{self.bucket_name}.{endpoint}/{filename}"
        else:
            # 使用默认的区域endpoint
            default_url = f"https://{self.bucket_name}.oss-{self.region}.aliyuncs.com/{filename}"
            print(f"使用默认OSS域名: {default_url}")
            return default_url

    def _get_image_info(self, image_bytes):
        """获取图片信息"""
        try:
            with Image.open(BytesIO(image_bytes)) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode
                }
        except Exception as e:
            logging.warning(f"获取图片信息失败: {str(e)}")
            return {}


# 创建全局实例 - 自动初始化
oss_service = OSSService()
