from app.apis.auth import SendCodeResource, RegisterResource, LoginResource, ResetPasswordResource, \
    UserInfoResource
from app.apis.image import ImageSaveResource, ImageListResource, ImageDetailResource, \
    ImageUpdateResource, ImageDeleteResource, ImageUrlToBase64Resource


def register_routes(api):
    # 注册路由
    api.add_resource(SendCodeResource, '/api/auth/send-code')
    api.add_resource(RegisterResource, '/api/auth/register')
    api.add_resource(LoginResource, '/api/auth/login')
    api.add_resource(ResetPasswordResource, '/api/auth/reset-pwd')
    api.add_resource(UserInfoResource, '/api/user/info')
    # 图片相关接口 - 增删查改
    api.add_resource(ImageSaveResource, '/api/images/add')                    # POST - 增
    api.add_resource(ImageListResource, '/api/images/list')                    # GET - 查（列表）
    api.add_resource(ImageDetailResource, '/api/images/<string:image_id>') # GET - 查（详情）
    api.add_resource(ImageUpdateResource, '/api/images/<string:image_id>') # PUT - 改
    api.add_resource(ImageDeleteResource, '/api/images/<string:image_id>') # DELETE - 删
    api.add_resource(ImageUrlToBase64Resource, '/api/images/url-to-base64')    # POST - URL转Base64
