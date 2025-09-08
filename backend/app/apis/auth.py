from flask import request, current_app
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import re

from app import db, APIResponse
from app.models.send_code import SendCode
from app.models.user import User
from app.models.user_storage import UserStorage
from app.utils.email_service import email_service


class SendCodeResource(Resource):
    def post(self):
        data = request.get_json()

        email = data.get('email', '').strip()
        send_type = data.get('send_type', 1)

        if not email:
            return APIResponse.error('邮箱不能为空')

        # 邮箱格式验证
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return APIResponse.error('邮箱格式不正确')

        # 检查发送频率
        frequency_check = email_service.check_send_frequency(email, send_type, 1)
        if not frequency_check['can_send']:
            return APIResponse.error(frequency_check['message'])

        # 根据发送类型处理
        user_id = None
        if send_type == 1:  # 注册
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return APIResponse.error('该邮箱已注册')
        elif send_type in [2, 3]:  # 重置密码或登录
            user = User.query.filter_by(email=email).first()
            if not user:
                return APIResponse.error('该邮箱未注册')
            user_id = user.id

        # 发送验证码 - 修复参数传递
        result = email_service.send_verification_code(
            email=email,
            send_type=send_type,
            user_id=user_id
        )

        # 修复返回值处理
        if result['success']:
            return APIResponse.success(message=result['message'])
        else:
            return APIResponse.error(result['message'])


class RegisterResource(Resource):
    def post(self):
        data = request.get_json()

        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        username = data.get('username', '').strip()
        code = data.get('code', '').strip()

        if not all([email, password, code]):
            return APIResponse.error('邮箱、密码和验证码不能为空')

        # 邮箱格式验证
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return APIResponse.error('邮箱格式不正确')

        # 密码强度验证
        if len(password) < 6:
            return APIResponse.error('密码长度不能少于6位')

        # 用户名验证
        if username and len(username) < 2:
            return APIResponse.error('用户名长度不能少于2位')

        # 检查邮箱是否已存在
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return APIResponse.error('该邮箱已注册')

        # 验证验证码 - 修复验证逻辑
        send_record = SendCode.query.filter_by(
            send_to=email,
            send_type=1,  # 注册类型
            code=code,
            is_used=False  # 添加未使用条件
        ).order_by(SendCode.created_at.desc()).first()

        if not send_record:
            return APIResponse.error('验证码不存在或已使用')

        # 使用模型方法检查是否过期
        if send_record.is_expired():
            return APIResponse.error('验证码已过期')

        try:
            # 创建用户
            user = User(
                email=email,
                username=username or email
            )
            user.set_password(password)

            db.session.add(user)
            db.session.flush()

            # 创建用户存储信息
            user_storage = UserStorage(user_id=user.id)
            db.session.add(user_storage)

            # 标记验证码为已使用，而不是删除
            send_record.is_used = True

            db.session.commit()

            return APIResponse.success(
                message='注册成功'
            )

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'注册失败: {str(e)}', exc_info=True)
            return APIResponse.error('注册失败，请稍后重试')


class LoginResource(Resource):
    """用户登录接口"""

    def post(self):
        """用户登录"""
        data = request.get_json()

        # 参数验证
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        login_type = data.get('login_type', 'password')  # password 或 code
        code = data.get('code', '').strip()

        if not email:
            return APIResponse.error('邮箱不能为空')

        # 邮箱格式验证
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return APIResponse.error('邮箱格式不正确')

        # 查找用户
        user = User.query.filter_by(email=email).first()
        if not user:
            return APIResponse.error('用户不存在')

        if not user.is_active:
            return APIResponse.error('账户已被禁用')

        # 根据登录类型验证
        if login_type == 'password':
            # 密码登录
            if not password:
                return APIResponse.error('密码不能为空')

            if not user.check_password(password):
                return APIResponse.error('密码错误')

        elif login_type == 'code':
            # 验证码登录
            if not code:
                return APIResponse.error('验证码不能为空')

            # 验证验证码
            send_record = SendCode.query.filter_by(
                send_to=email,
                send_type=3,  # 登录类型
                code=code
            ).order_by(SendCode.created_at.desc()).first()

            if not send_record:
                return APIResponse.error('验证码不存在或已失效')

            # 检查验证码是否过期
            if datetime.utcnow() > send_record.created_at + timedelta(minutes=10):
                return APIResponse.error('验证码已过期')

            # 删除已使用的验证码
            db.session.delete(send_record)
            db.session.commit()

        else:
            return APIResponse.error('登录类型无效')

        # 生成访问令牌
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(days=20)
        )

        return APIResponse.success(
            data={
                'user': user.to_dict(),
                'access_token': access_token
            },
            message='登录成功'
        )


class ResetPasswordResource(Resource):
    """重置密码接口"""

    def post(self):
        """重置密码"""
        data = request.get_json()

        # 参数验证
        email = data.get('email', '').strip()
        code = data.get('code', '').strip()
        new_password = data.get('new_password', '').strip()

        if not all([email, code, new_password]):
            return APIResponse.error('邮箱、验证码和新密码不能为空')

        # 密码强度验证
        if len(new_password) < 6:
            return APIResponse.error('密码长度不能少于6位')

        # 查找用户
        user = User.query.filter_by(email=email).first()
        if not user:
            return APIResponse.error('用户不存在')

        # 验证验证码
        send_record = SendCode.query.filter_by(
            send_to=email,
            send_type=2,  # 重置密码类型
            code=code
        ).order_by(SendCode.created_at.desc()).first()

        if not send_record:
            return APIResponse.error('验证码不存在或已失效')

        # 检查验证码是否过期
        if datetime.utcnow() > send_record.created_at + timedelta(minutes=10):
            return APIResponse.error('验证码已过期')

        try:
            # 更新密码
            user.set_password(new_password)

            # 删除已使用的验证码
            db.session.delete(send_record)

            db.session.commit()

            return APIResponse.success(message='密码重置成功')

        except Exception as e:
            db.session.rollback()
            return APIResponse.error('密码重置失败，请稍后重试', code=500)


class UserInfoResource(Resource):
    """用户信息接口"""

    @jwt_required()
    def get(self):
        """获取当前用户信息"""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return APIResponse.error('用户不存在', code=404)

        # 获取存储信息
        storage = UserStorage.query.filter_by(user_id=user_id).first()

        return APIResponse.success(
            data={
                'user': user.to_dict(),
                'storage': storage.to_dict() if storage else None
            }
        )

    @jwt_required()
    def put(self):
        """更新用户信息"""
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return APIResponse.error('用户不存在', code=404)

        data = request.get_json()
        username = data.get('username', '').strip()

        if username:
            if len(username) < 2:
                return APIResponse.error('用户名长度不能少于2位')
            user.username = username

        try:
            db.session.commit()
            return APIResponse.success(
                data={'user': user.to_dict()},
                message='用户信息更新成功'
            )
        except Exception as e:
            db.session.rollback()
            return APIResponse.error('更新失败，请稍后重试', code=500)
