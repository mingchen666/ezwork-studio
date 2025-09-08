from flask import current_app, render_template_string
from flask_mail import  Message
from datetime import datetime, timedelta
import random
import string

from app import db
from app.extensions import mail
from app.models.send_code import SendCode


class EmailService:
    """邮件发送服务类"""

    def __init__(self):
        self.mail = mail


    def generate_code(self, length=6):
        """生成验证码"""
        return ''.join(random.choices(string.digits, k=length))

    def send_verification_code(self, email, send_type, user_id=None, expires_minutes=10):
        try:
            # 生成验证码
            code = self.generate_code()

            # 设置过期时间
            expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)

            # 根据发送类型选择邮件模板和主题
            templates = {
                1: {
                    'subject': '【AI绘画程序】邮箱注册验证码',
                    'template': 'register_template'
                },
                2: {
                    'subject': '【AI绘画程序】密码重置验证码',
                    'template': 'reset_password_template'
                },
                3: {
                    'subject': '【AI绘画程序】登录验证码',
                    'template': 'login_template'
                }
            }

            if send_type not in templates:
                return {'success': False, 'message': '无效的发送类型'}

            template_info = templates[send_type]

            # 发送邮件
            success = self._send_email(
                to=email,
                subject=template_info['subject'],
                template=template_info['template'],
                code=code,
                expires_minutes=expires_minutes
            )

            if success:
                # 保存验证码记录
                send_record = SendCode(
                    user_id=user_id,
                    send_type=send_type,
                    send_to=email,
                    code=code,
                    expires_at=expires_at
                )
                db.session.add(send_record)
                db.session.commit()

                return {
                    'success': True,
                    'message': '验证码发送成功',
                    'code_id': send_record.id,
                    'expires_at': expires_at.isoformat()
                }
            else:
                return {'success': False, 'message': '邮件发送失败'}

        except Exception as e:
            current_app.logger.error(f'发送验证码邮件失败: {str(e)}')
            return {'success': False, 'message': f'发送失败: {str(e)}'}

    def verify_code(self, email, code, send_type, max_attempts=3):
        """验证验证码"""
        try:
            # 查找最近的未使用验证码
            send_record = SendCode.query.filter_by(
                send_to=email,
                send_type=send_type,
                is_used=False
            ).order_by(SendCode.created_at.desc()).first()

            if not send_record:
                return {'success': False, 'message': '验证码不存在或已使用'}

            # 使用模型方法检查是否过期
            if send_record.is_expired():
                return {'success': False, 'message': '验证码已过期'}

            # 验证码匹配
            if send_record.code == code:
                # 标记为已使用
                send_record.is_used = True
                db.session.commit()

                return {
                    'success': True,
                    'message': '验证码验证成功',
                    'user_id': send_record.user_id,
                    'code_id': send_record.id
                }
            else:
                return {'success': False, 'message': '验证码错误'}

        except Exception as e:
            current_app.logger.error(f'验证码验证失败: {str(e)}', exc_info=True)
            return {'success': False, 'message': f'验证失败: {str(e)}'}

    def check_send_frequency(self, email, send_type, interval_minutes=1):
        """
        检查发送频率限制

        Args:
            email: 邮箱
            send_type: 发送类型
            interval_minutes: 发送间隔（分钟）

        Returns:
            dict: 检查结果
        """
        try:
            # 查找最近的发送记录
            recent_send = SendCode.query.filter_by(
                send_to=email,
                send_type=send_type
            ).order_by(SendCode.created_at.desc()).first()

            if recent_send:
                time_diff = datetime.utcnow() - recent_send.created_at
                if time_diff.total_seconds() < interval_minutes * 60:
                    remaining_seconds = int(interval_minutes * 60 - time_diff.total_seconds())
                    return {
                        'can_send': False,
                        'message': f'请等待 {remaining_seconds} 秒后再试',
                        'remaining_seconds': remaining_seconds
                    }

            return {'can_send': True, 'message': '可以发送'}

        except Exception as e:
            current_app.logger.error(f'检查发送频率失败: {str(e)}')
            return {'can_send': False, 'message': '检查失败'}

    def _send_email(self, to, subject, template, **kwargs):
        """
        发送邮件的内部方法

        Args:
            to: 收件人
            subject: 主题
            template: 模板名称
            **kwargs: 模板参数

        Returns:
            bool: 发送是否成功
        """
        try:
            # 获取邮件模板
            html_content = self._get_email_template(template, **kwargs)

            # 创建邮件消息
            msg = Message(
                subject=subject,
                recipients=[to],
                html=html_content,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER')
            )

            # 发送邮件
            self.mail.send(msg)
            return True

        except Exception as e:
            current_app.logger.error(f'邮件发送失败: {str(e)}')
            return False

    def _get_email_template(self, template_name, **kwargs):
        """获取邮件模板"""
        templates = {
            'register_template': self._get_register_template(**kwargs),
            'reset_password_template': self._get_reset_password_template(**kwargs),
            'login_template': self._get_login_template(**kwargs)
        }

        return templates.get(template_name, self._get_default_template(**kwargs))

    def _get_register_template(self, code, expires_minutes=10, **kwargs):
        """注册验证码邮件模板"""
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>邮箱注册验证码</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(45deg, #0B5345, #16A085); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
                .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }
                .code { background: #fff; border: 2px solid #0B5345; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; color: #0B5345; margin: 20px 0; border-radius: 8px; }
                .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
                .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 4px; margin: 15px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎨 AI绘画程序</h1>
                    <p>欢迎注册我们的服务</p>
                </div>
                <div class="content">
                    <h2>邮箱验证码</h2>
                    <p>您好！感谢您注册AI绘画程序。</p>
                    <p>您的验证码是：</p>
                    <div class="code">{{ code }}</div>
                    <div class="warning">
                        <strong>⚠️ 重要提示：</strong>
                        <ul>
                            <li>验证码有效期为 {{ expires_minutes }} 分钟</li>
                            <li>请勿将验证码告诉他人</li>
                            <li>如非本人操作，请忽略此邮件</li>
                        </ul>
                    </div>
                    <p>完成验证后，您就可以开始使用AI绘画功能了！</p>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                    <p>© 2024 AI绘画程序. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """, code=code, expires_minutes=expires_minutes)

    def _get_reset_password_template(self, code, expires_minutes=10, **kwargs):
        """重置密码验证码邮件模板"""
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>密码重置验证码</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(45deg, #dc3545, #e74c3c); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
                .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }
                .code { background: #fff; border: 2px solid #dc3545; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; color: #dc3545; margin: 20px 0; border-radius: 8px; }
                .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
                .warning { background: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; border-radius: 4px; margin: 15px 0; color: #721c24; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔒 密码重置</h1>
                    <p>AI绘画程序</p>
                </div>
                <div class="content">
                    <h2>密码重置验证码</h2>
                    <p>您好！我们收到了您的密码重置请求。</p>
                    <p>您的验证码是：</p>
                    <div class="code">{{ code }}</div>
                    <div class="warning">
                        <strong>🚨 安全提示：</strong>
                        <ul>
                            <li>验证码有效期为 {{ expires_minutes }} 分钟</li>
                            <li>如果这不是您的操作，请立即联系我们</li>
                            <li>请勿将验证码告诉任何人</li>
                            <li>建议设置一个强密码</li>
                        </ul>
                    </div>
                    <p>使用此验证码完成密码重置后，请妥善保管您的新密码。</p>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                    <p>© 2024 AI绘画程序. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """, code=code, expires_minutes=expires_minutes)

    def _get_login_template(self, code, expires_minutes=10, **kwargs):
        """登录验证码邮件模板"""
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>登录验证码</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(45deg, #007bff, #0056b3); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }
                .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }
                .code { background: #fff; border: 2px solid #007bff; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; color: #007bff; margin: 20px 0; border-radius: 8px; }
                .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
                .info { background: #d1ecf1; border: 1px solid #bee5eb; padding: 10px; border-radius: 4px; margin: 15px 0; color: #0c5460; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 安全登录</h1>
                    <p>AI绘画程序</p>
                </div>
                <div class="content">
                    <h2>登录验证码</h2>
                    <p>您好！检测到您正在尝试登录AI绘画程序。</p>
                    <p>您的登录验证码是：</p>
                    <div class="code">{{ code }}</div>
                    <div class="info">
                        <strong>ℹ️ 登录信息：</strong>
                        <ul>
                            <li>验证码有效期为 {{ expires_minutes }} 分钟</li>
                            <li>如果这不是您的登录操作，请忽略此邮件</li>
                            <li>为了账户安全，建议定期更换密码</li>
                        </ul>
                    </div>
                    <p>输入验证码后即可完成登录，开始您的AI绘画之旅！</p>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                    <p>© 2025 AI绘画程序. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """, code=code, expires_minutes=expires_minutes)

    def _get_default_template(self, code, expires_minutes=10, **kwargs):
        """默认邮件模板"""
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>验证码</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .code { background: #f8f9fa; border: 2px solid #6c757d; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; margin: 20px 0; border-radius: 8px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>验证码</h2>
                <p>您的验证码是：</p>
                <div class="code">{{ code }}</div>
                <p>验证码有效期为 {{ expires_minutes }} 分钟，请及时使用。</p>
            </div>
        </body>
        </html>
        """, code=code, expires_minutes=expires_minutes)


# 创建全局邮件服务实例
email_service = EmailService()
