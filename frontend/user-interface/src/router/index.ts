import { createRouter, createWebHistory } from 'vue-router'
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
    component: () => import('@/layouts/UserLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: { title: '首页' }
      },
      {
        path: '/fitness',
        name: 'Fitness',
        component: () => import('@/views/Fitness.vue'),
        meta: { title: '健身' }
      },
      {
        path: '/life',
        name: 'Life',
        component: () => import('@/views/Life.vue'),
        meta: { title: '生活' }
      },
      {
        path: '/geek',
        name: 'Geek',
        component: () => import('@/views/Geek.vue'),
        meta: { title: '极客' }
      },
      {
        path: '/social',
        name: 'Social',
        component: () => import('@/views/Social.vue'),
        meta: { title: '社交' }
      },
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人中心' }
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
  
  // 检查是否有token，避免循环依赖
  const token = localStorage.getItem('token')
  const isAuthenticated = !!token
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router
