import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'DashboardHome',
          component: () => import('@/views/DashboardHome.vue')
        },
        {
          path: 'fitness/workouts',
          name: 'FitnessWorkouts',
          component: () => import('@/views/FitnessWorkouts.vue')
        },
        {
          path: 'fitness/posts',
          name: 'FitnessPosts',
          component: () => import('@/views/FitnessPosts.vue')
        },
        {
          path: 'fitness/profile',
          name: 'FitnessProfile',
          component: () => import('@/views/FitnessProfile.vue')
        },
        {
          path: 'life/diary',
          name: 'LifeDiary',
          component: () => import('@/views/LifeDiary.vue')
        },
        {
          path: 'life/food',
          name: 'LifeFood',
          component: () => import('@/views/LifeFood.vue')
        },
        {
          path: 'life/checkin',
          name: 'LifeCheckin',
          component: () => import('@/views/LifeCheckin.vue')
        },
        {
          path: 'tools/pdf',
          name: 'ToolsPdf',
          component: () => import('@/views/ToolsPdf.vue')
        },
        {
          path: 'tools/crawler',
          name: 'ToolsCrawler',
          component: () => import('@/views/ToolsCrawler.vue')
        },
        {
          path: 'tools/testcase',
          name: 'ToolsTestcase',
          component: () => import('@/views/ToolsTestcase.vue')
        },
        {
          path: 'social/chat',
          name: 'SocialChat',
          component: () => import('@/views/SocialChat.vue')
        },
        {
          path: 'social/heart-link',
          name: 'SocialHeartLink',
          component: () => import('@/views/SocialHeartLink.vue')
        },
        {
          path: 'social/tarot',
          name: 'SocialTarot',
          component: () => import('@/views/SocialTarot.vue')
        },
        {
          path: 'admin/users',
          name: 'AdminUsers',
          component: () => import('@/views/AdminUsers.vue')
        },
        {
          path: 'admin/features',
          name: 'AdminFeatures',
          component: () => import('@/views/AdminFeatures.vue')
        },
        {
          path: 'admin/stats',
          name: 'AdminStats',
          component: () => import('@/views/AdminStats.vue')
        }
      ]
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 初始化认证状态
  authStore.initAuth()
  
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next('/login')
  } else if (to.path === '/login' && authStore.isLoggedIn) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router