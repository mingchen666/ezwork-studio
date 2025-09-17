import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { useUserStore } from '@/stores/user'
import Qs from 'qs'


const request = axios.create({
  baseURL: '/api', //  import.meta.env.VITE_API_URL   url = base url + request url
  withCredentials: true, // send cookies when cross-domain requests
  crossDomain: true,
  timeout: 300000, // request timeout

})

// request interceptor
request.interceptors.request.use(
  config => {
    const userStore = useUserStore()

    // 使用Bearer token格式
    if (userStore.token) {
      config.headers['Authorization'] = `Bearer ${userStore.token}`
    }

    // 如果是FormData，不设置Content-Type让axios自动设置
    // 如果是普通对象，设置为JSON格式，让axios自动处理序列化
    if (!(config.data instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json'
      // 删除手动JSON.stringify，让axios自动处理
    }

    return config
  },
  error => {
    console.log(error)
    return Promise.reject(error)
  }
)


// response interceptor
request.interceptors.response.use(
  response => {
    const res = response.data
    // if (res?.code === 401) {
    //   router.push('/login')
    //   return Promise.reject(new Error('Unauthorized'))
    // }
    return res
  },
  error => {
    const { response } = error
    const userStore = useUserStore()
    if (response) {
      switch (response.status) {
        case 401:
          ElMessage.error('身份过期，请重新登录')
          userStore.logout()
          router.push('/login')
          break
        case 403:
          ElMessage.error('用户状态异常或权限不足!')
          break
        default:
          ElMessage.error('请求失败')
      }
    } else {
      ElMessage.error('网络连接异常')
    }
    return Promise.reject(error)
  }
)


export default request
