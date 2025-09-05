<template>
  <div class="home-page">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="banner-content">
        <h1>欢迎回来，{{ authStore.user?.username }}！</h1>
        <p>今天也要加油哦 💪</p>
        <div class="quick-stats">
          <div class="stat-item">
            <div class="stat-number">{{ userStats.todayWorkouts }}</div>
            <div class="stat-label">今日训练</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ userStats.toolsUsed }}</div>
            <div class="stat-label">工具使用</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ userStats.socialActivities }}</div>
            <div class="stat-label">社交活动</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 功能模块 -->
    <div class="modules-section">
      <div class="section-header">
        <h2>功能模块</h2>
        <p>选择您需要的功能</p>
      </div>
      
      <div class="modules-grid">
        <div class="module-card" @click="$router.push('/fitness')">
          <div class="module-icon fitness">
            <el-icon><Trophy /></el-icon>
          </div>
          <h3>健身管理</h3>
          <p>记录训练，追踪进度，达成目标</p>
          <div class="module-stats">
            <span>{{ userStats.fitnessRecords }} 条记录</span>
          </div>
        </div>
        
        <div class="module-card" @click="$router.push('/life')">
          <div class="module-icon life">
            <el-icon><Sunny /></el-icon>
          </div>
          <h3>生活助手</h3>
          <p>日记记录，食物推荐，冥想放松</p>
          <div class="module-stats">
            <span>{{ userStats.lifeRecords }} 条记录</span>
          </div>
        </div>
        
        <div class="module-card" @click="$router.push('/geek')">
          <div class="module-icon geek">
            <el-icon><Tools /></el-icon>
          </div>
          <h3>极客工具</h3>
          <p>PDF转换，代码格式化，数据分析</p>
          <div class="module-stats">
            <span>{{ userStats.geekTools }} 个工具</span>
          </div>
        </div>
        
        <div class="module-card" @click="$router.push('/social')">
          <div class="module-icon social">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <h3>社交娱乐</h3>
          <p>聊天交友，心链连接，塔罗占卜</p>
          <div class="module-stats">
            <span>{{ userStats.socialConnections }} 个连接</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 最近活动 -->
    <div class="recent-activities">
      <div class="section-header">
        <h2>最近活动</h2>
        <el-button type="text" @click="refreshActivities">刷新</el-button>
      </div>
      
      <div class="activities-list">
        <div 
          v-for="activity in recentActivities" 
          :key="activity.id"
          class="activity-item"
        >
          <div class="activity-icon">
            <el-icon><component :is="activity.icon" /></el-icon>
          </div>
          <div class="activity-content">
            <h4>{{ activity.title }}</h4>
            <p>{{ activity.description }}</p>
            <span class="activity-time">{{ activity.time }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 推荐内容 -->
    <div class="recommendations">
      <div class="section-header">
        <h2>推荐内容</h2>
      </div>
      
      <div class="recommendations-grid">
        <div class="recommendation-card">
          <img src="/api/placeholder/300/200" alt="推荐图片" />
          <div class="card-content">
            <h3>健身小贴士</h3>
            <p>如何正确进行有氧运动</p>
            <el-button type="primary" size="small">查看详情</el-button>
          </div>
        </div>
        
        <div class="recommendation-card">
          <img src="/api/placeholder/300/200" alt="推荐图片" />
          <div class="card-content">
            <h3>生活技巧</h3>
            <p>提高工作效率的10个方法</p>
            <el-button type="primary" size="small">查看详情</el-button>
          </div>
        </div>
        
        <div class="recommendation-card">
          <img src="/api/placeholder/300/200" alt="推荐图片" />
          <div class="card-content">
            <h3>技术分享</h3>
            <p>Vue3 最佳实践指南</p>
            <el-button type="primary" size="small">查看详情</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 用户统计数据
const userStats = reactive({
  todayWorkouts: 0,
  toolsUsed: 0,
  socialActivities: 0,
  fitnessRecords: 0,
  lifeRecords: 0,
  geekTools: 0,
  socialConnections: 0
})

// 最近活动
const recentActivities = ref([
  {
    id: 1,
    title: '完成今日训练',
    description: '进行了30分钟的有氧运动',
    time: '2小时前',
    icon: 'Trophy'
  },
  {
    id: 2,
    title: '使用PDF转换工具',
    description: '将Word文档转换为PDF格式',
    time: '4小时前',
    icon: 'Tools'
  },
  {
    id: 3,
    title: '发布新的日记',
    description: '记录今天的心情和感受',
    time: '6小时前',
    icon: 'Document'
  },
  {
    id: 4,
    title: '参与聊天室讨论',
    description: '在技术交流群中分享经验',
    time: '8小时前',
    icon: 'ChatDotRound'
  }
])

// 加载用户数据
const loadUserData = async () => {
  try {
    // 这里应该调用API获取用户数据
    // 现在使用模拟数据
    userStats.todayWorkouts = 2
    userStats.toolsUsed = 15
    userStats.socialActivities = 8
    userStats.fitnessRecords = 45
    userStats.lifeRecords = 23
    userStats.geekTools = 12
    userStats.socialConnections = 6
  } catch (error) {
    console.error('加载用户数据失败:', error)
  }
}

// 刷新活动
const refreshActivities = () => {
  console.log('刷新活动数据')
}

onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.home-page {
  padding: 0;
}

.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 60px 20px;
  text-align: center;
}

.banner-content h1 {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 16px;
}

.banner-content p {
  font-size: 18px;
  margin-bottom: 40px;
  opacity: 0.9;
}

.quick-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  max-width: 600px;
  margin: 0 auto;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.8;
}

.modules-section {
  padding: 60px 20px;
  background: white;
}

.section-header {
  text-align: center;
  margin-bottom: 40px;
}

.section-header h2 {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.section-header p {
  color: #909399;
  font-size: 16px;
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.module-card {
  background: white;
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid #f0f0f0;
}

.module-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.module-icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  font-size: 32px;
  color: white;
}

.module-icon.fitness {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.module-icon.life {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.module-icon.geek {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.module-icon.social {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.module-card h3 {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.module-card p {
  color: #606266;
  margin-bottom: 20px;
  line-height: 1.5;
}

.module-stats {
  color: #909399;
  font-size: 14px;
}

.recent-activities {
  padding: 60px 20px;
  background: #f8f9fa;
}

.activities-list {
  max-width: 800px;
  margin: 0 auto;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 12px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.activity-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #f0f9ff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  color: #409eff;
  font-size: 20px;
}

.activity-content {
  flex: 1;
}

.activity-content h4 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.activity-content p {
  color: #606266;
  margin-bottom: 8px;
}

.activity-time {
  color: #909399;
  font-size: 12px;
}

.recommendations {
  padding: 60px 20px;
  background: white;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.recommendation-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease;
}

.recommendation-card:hover {
  transform: translateY(-2px);
}

.recommendation-card img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.card-content {
  padding: 20px;
}

.card-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.card-content p {
  color: #606266;
  margin-bottom: 16px;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .welcome-banner {
    padding: 40px 16px;
  }
  
  .banner-content h1 {
    font-size: 28px;
  }
  
  .quick-stats {
    gap: 20px;
  }
  
  .stat-number {
    font-size: 24px;
  }
  
  .modules-section,
  .recent-activities,
  .recommendations {
    padding: 40px 16px;
  }
  
  .modules-grid {
    grid-template-columns: 1fr;
  }
}
</style>
