from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from .config import get_config
from .extensions import init_extensions, db, api
from .utils.api_response import APIResponse


def create_app(config_class=None):
    load_dotenv()
    app = Flask(__name__)

    from .routes import register_routes
    # 加载配置
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # 初始化扩展（此时不注册路由）
    init_extensions(app)
    register_routes(api)

    # from .utils.email_service import email_service
    # # 初始化邮件服务
    # email_service.init_app(app)
    @app.errorhandler(404)
    def handle_404(e):
        return APIResponse.not_found()

    from jwt.exceptions import ExpiredSignatureError

    @app.errorhandler(ExpiredSignatureError)
    def handle_expired_token_error(e):
        return jsonify({"message": "身份验证信息已过期，请重新登录"}), 401

    @app.errorhandler(500)
    def handle_500(e):
        return APIResponse.error(message='服务器错误', code=500)

    # 初始化数据库
    with app.app_context():
        db.create_all()

    # 开发环境路由打印
    # if app.debug:
    #     with app.app_context():
    #         print("\n=== 已注册路由 ===")
    #         for rule in app.url_map.iter_rules():
    #             methods = ','.join(rule.methods)
    #             print(f"{rule.endpoint}: {methods} -> {rule}")
    #         print("===================\n")

    return app
