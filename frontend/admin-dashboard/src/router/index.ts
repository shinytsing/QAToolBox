import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 配置NProgress
NProgress.configure({ showSpinner: false })

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: '/users',
        name: 'Users',
        component: () => import('@/views/Users.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: '/fitness',
        name: 'Fitness',
        component: () => import('@/views/Fitness.vue'),
        meta: { title: '健身管理' }
      },
      {
        path: '/life-tools',
        name: 'LifeTools',
        component: () => import('@/views/LifeTools.vue'),
        meta: { title: '生活工具' }
      },
      {
        path: '/geek-tools',
        name: 'GeekTools',
        component: () => import('@/views/GeekTools.vue'),
        meta: { title: '极客工具' }
      },
      {
        path: '/social',
        name: 'Social',
        component: () => import('@/views/Social.vue'),
        meta: { title: '社交娱乐' }
      },
      {
        path: '/share',
        name: 'Share',
        component: () => import('@/views/Share.vue'),
        meta: { title: '分享管理' }
      },
      {
        path: '/settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '系统设置' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  NProgress.start()
  
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router
