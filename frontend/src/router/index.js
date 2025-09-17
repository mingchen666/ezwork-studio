// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
const routes = [
  {
    path: '',
    redirect: '/home',
    name: 'AppLayout',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      {
        path: '/home',
        name: 'GeminiDraw',
        component: () => import('@/views/gemini-draw/index.vue'),
        meta: {
          title: 'Ezwork Studio',
          requiresAuth: true
        }
      },
      {
        path: '/test',
        name: 'test',
        component: () => import('@/views/test.vue'),
        meta: {
          title: 'Ezwork Studio',
          requiresAuth: true
        }
      }
    ]

  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/index.vue'),
    meta: {
      title: '登录注册',
      requiresAuth: false
    }
  },
  // 404
  {
    path: '/404',
    name: '404',
    component: () => import('@/views/404/index.vue'),
    meta: {
      title: '404'
    }
  },
  // 匹配其他路由
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})


router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - AI绘图助手`
  } else {
    document.title = 'AI绘图客户端'
  }
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && userStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})



export default router
