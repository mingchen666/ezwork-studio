import request from "@/utils/request";

// 登录
export function Login(data) {
  return request({
    url: "/api/auth/login",
    method: "post",
    data,
  });
}
// 注册发送验证码
export function RegisterSendCode(data) {
  return request({
    url: "/api/auth/send-code",
    method: "post",
    data,
  });
}
// 注册
export function Register(data) {
  return request({
    url: "/api/auth/register",
    method: "post",
    data,
  });
}