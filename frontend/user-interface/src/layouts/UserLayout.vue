<template>
  <div class="user-layout">
    <!-- 顶部导航 -->
    <el-header class="header">
      <div class="header-content">
        <div class="logo">
          <img src="/logo.png" alt="QAToolBox" />
          <span class="logo-text">QAToolBox</span>
        </div>
        
        <div class="nav-menu">
          <el-menu
            :default-active="$route.path"
            mode="horizontal"
            router
            class="nav-menu-list"
          >
            <el-menu-item index="/">
              <el-icon><HomeFilled /></el-icon>
              <span>首页</span>
            </el-menu-item>
            <el-menu-item index="/fitness">
              <el-icon><Trophy /></el-icon>
              <span>健身</span>
            </el-menu-item>
            <el-menu-item index="/life">
              <el-icon><Sunny /></el-icon>
              <span>生活</span>
            </el-menu-item>
            <el-menu-item index="/geek">
              <el-icon><Tools /></el-icon>
              <span>极客</span>
            </el-menu-item>
            <el-menu-item index="/social">
              <el-icon><ChatDotRound /></el-icon>
              <span>社交</span>
            </el-menu-item>
          </el-menu>
        </div>
        
        <div class="user-actions">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :src="authStore.user?.avatar" :size="32">
                {{ authStore.user?.username?.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="username">{{ authStore.user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="settings">设置</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>

    <!-- 主内容区 -->
    <el-main class="main-content">
      <router-view />
    </el-main>

    <!-- 底部导航 (移动端) -->
    <el-footer class="mobile-nav" v-show="isMobile">
      <div class="mobile-nav-content">
        <div 
          v-for="item in mobileNavItems" 
          :key="item.path"
          class="mobile-nav-item"
          :class="{ active: $route.path === item.path }"
          @click="$router.push(item.path)"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.name }}</span>
        </div>
      </div>
    </el-footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const isMobile = ref(false)

const mobileNavItems = [
  { path: '/', name: '首页', icon: 'HomeFilled' },
  { path: '/fitness', name: '健身', icon: 'Trophy' },
  { path: '/life', name: '生活', icon: 'Sunny' },
  { path: '/geek', name: '极客', icon: 'Tools' },
  { path: '/social', name: '社交', icon: 'ChatDotRound' }
]

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      // 跳转到设置页面
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await authStore.logout()
        router.push('/login')
        ElMessage.success('已退出登录')
      } catch (error) {
        // 用户取消
      }
      break
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.user-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 20px;
  font-weight: bold;
}

.logo img {
  height: 32px;
  margin-right: 8px;
}

.nav-menu {
  flex: 1;
  display: flex;
  justify-content: center;
}

.nav-menu-list {
  background: transparent;
  border: none;
}

.nav-menu-list .el-menu-item {
  color: white;
  border-bottom: 2px solid transparent;
}

.nav-menu-list .el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-menu-list .el-menu-item.is-active {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border-bottom-color: white;
}

.user-actions {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 20px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.username {
  margin: 0 8px;
  font-size: 14px;
}

.main-content {
  flex: 1;
  background-color: #f5f5f5;
  padding: 0;
  overflow-y: auto;
}

.mobile-nav {
  background: white;
  border-top: 1px solid #e6e6e6;
  padding: 0;
  height: 60px;
}

.mobile-nav-content {
  display: flex;
  height: 100%;
}

.mobile-nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: color 0.3s;
  color: #909399;
}

.mobile-nav-item.active {
  color: #409eff;
}

.mobile-nav-item .el-icon {
  font-size: 20px;
  margin-bottom: 4px;
}

.mobile-nav-item span {
  font-size: 12px;
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
  }
  
  .nav-menu {
    display: none;
  }
  
  .logo-text {
    display: none;
  }
}
</style>
