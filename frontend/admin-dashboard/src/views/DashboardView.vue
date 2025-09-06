<template>
  <div class="dashboard">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="250px" class="sidebar">
        <div class="logo">
          <h2>QAToolBox</h2>
          <p>管理后台</p>
        </div>
        
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          router
        >
          <el-menu-item index="/dashboard">
            <el-icon><House /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          
          <el-sub-menu index="fitness">
            <template #title>
              <el-icon><Trophy /></el-icon>
              <span>健身模块</span>
            </template>
            <el-menu-item index="/fitness/workouts">训练计划</el-menu-item>
            <el-menu-item index="/fitness/posts">健身社区</el-menu-item>
            <el-menu-item index="/fitness/profile">用户档案</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="life">
            <template #title>
              <el-icon><Calendar /></el-icon>
              <span>生活模块</span>
            </template>
            <el-menu-item index="/life/diary">日记管理</el-menu-item>
            <el-menu-item index="/life/food">食物随机</el-menu-item>
            <el-menu-item index="/life/checkin">签到管理</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="tools">
            <template #title>
              <el-icon><Tools /></el-icon>
              <span>极客工具</span>
            </template>
            <el-menu-item index="/tools/pdf">PDF转换</el-menu-item>
            <el-menu-item index="/tools/crawler">网页爬虫</el-menu-item>
            <el-menu-item index="/tools/testcase">测试用例</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="social">
            <template #title>
              <el-icon><ChatDotRound /></el-icon>
              <span>社交娱乐</span>
            </template>
            <el-menu-item index="/social/chat">聊天室</el-menu-item>
            <el-menu-item index="/social/heart-link">心链</el-menu-item>
            <el-menu-item index="/social/tarot">塔罗占卜</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="admin">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>系统管理</span>
            </template>
            <el-menu-item index="/admin/users">用户管理</el-menu-item>
            <el-menu-item index="/admin/features">功能管理</el-menu-item>
            <el-menu-item index="/admin/stats">系统统计</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-container>
        <!-- 顶部导航 -->
        <el-header class="header">
          <div class="header-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item>QAToolBox</el-breadcrumb-item>
              <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-icon><User /></el-icon>
                {{ authStore.user?.username }}
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                  <el-dropdown-item command="settings">系统设置</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <!-- 内容区域 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)

const currentPageTitle = computed(() => {
  const titleMap: Record<string, string> = {
    '/dashboard': '仪表盘',
    '/fitness/workouts': '训练计划',
    '/fitness/posts': '健身社区',
    '/fitness/profile': '用户档案',
    '/life/diary': '日记管理',
    '/life/food': '食物随机',
    '/life/checkin': '签到管理',
    '/tools/pdf': 'PDF转换',
    '/tools/crawler': '网页爬虫',
    '/tools/testcase': '测试用例',
    '/social/chat': '聊天室',
    '/social/heart-link': '心链',
    '/social/tarot': '塔罗占卜',
    '/admin/users': '用户管理',
    '/admin/features': '功能管理',
    '/admin/stats': '系统统计'
  }
  return titleMap[route.path] || '未知页面'
})

const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人资料功能开发中...')
      break
    case 'settings':
      ElMessage.info('系统设置功能开发中...')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        await authStore.logout()
        ElMessage.success('已退出登录')
        router.push('/login')
      } catch {
        // 用户取消
      }
      break
  }
}
</script>

<style scoped>
.dashboard {
  height: 100vh;
}

.sidebar {
  background: #304156;
  color: white;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #434a50;
}

.logo h2 {
  margin: 0 0 5px 0;
  color: #fff;
  font-size: 20px;
}

.logo p {
  margin: 0;
  color: #b3b3b3;
  font-size: 12px;
}

.sidebar-menu {
  border: none;
  background: #304156;
}

.sidebar-menu .el-menu-item,
.sidebar-menu .el-sub-menu__title {
  color: #b3b3b3;
}

.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-sub-menu__title:hover {
  background: #263445;
  color: #fff;
}

.sidebar-menu .el-menu-item.is-active {
  background: #409eff;
  color: #fff;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background: #f5f5f5;
}

.main-content {
  background: #f5f5f5;
  padding: 20px;
}
</style>
