<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>仪表盘</h1>
      <p>欢迎回来，{{ authStore.user?.username }}！</p>
    </div>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon users">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalUsers }}</div>
              <div class="stat-label">总用户数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon fitness">
              <el-icon><Trophy /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.activeUsers }}</div>
              <div class="stat-label">活跃用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon tools">
              <el-icon><Tools /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalTools }}</div>
              <div class="stat-label">工具使用次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon social">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.totalShares }}</div>
              <div class="stat-label">分享次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>用户增长趋势</span>
              <el-button-group>
                <el-button size="small" :type="userChartPeriod === '7d' ? 'primary' : ''" @click="userChartPeriod = '7d'">7天</el-button>
                <el-button size="small" :type="userChartPeriod === '30d' ? 'primary' : ''" @click="userChartPeriod = '30d'">30天</el-button>
                <el-button size="small" :type="userChartPeriod === '90d' ? 'primary' : ''" @click="userChartPeriod = '90d'">90天</el-button>
              </el-button-group>
            </div>
          </template>
          <div class="chart-container">
            <v-chart :option="userGrowthChart" style="height: 300px;" />
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>工具使用分布</span>
            </div>
          </template>
          <div class="chart-container">
            <v-chart :option="toolUsageChart" style="height: 300px;" />
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 最近活动 -->
    <el-row :gutter="20" class="activity-row">
      <el-col :span="16">
        <el-card class="activity-card">
          <template #header>
            <div class="card-header">
              <span>最近活动</span>
              <el-button size="small" @click="refreshActivities">刷新</el-button>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="activity in recentActivities"
              :key="activity.id"
              :timestamp="activity.timestamp"
              :type="activity.type"
            >
              <el-card>
                <h4>{{ activity.title }}</h4>
                <p>{{ activity.description }}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="quick-actions-card">
          <template #header>
            <span>快速操作</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/users')" class="action-btn">
              <el-icon><User /></el-icon>
              用户管理
            </el-button>
            <el-button type="success" @click="$router.push('/fitness')" class="action-btn">
              <el-icon><Trophy /></el-icon>
              健身数据
            </el-button>
            <el-button type="warning" @click="$router.push('/geek-tools')" class="action-btn">
              <el-icon><Tools /></el-icon>
              工具管理
            </el-button>
            <el-button type="info" @click="$router.push('/social')" class="action-btn">
              <el-icon><ChatDotRound /></el-icon>
              社交管理
            </el-button>
            <el-button type="danger" @click="$router.push('/settings')" class="action-btn">
              <el-icon><Setting /></el-icon>
              系统设置
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

// 注册ECharts组件
use([
  CanvasRenderer,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const authStore = useAuthStore()

// 统计数据
const stats = reactive({
  totalUsers: 0,
  activeUsers: 0,
  totalTools: 0,
  totalShares: 0
})

// 图表数据
const userChartPeriod = ref('30d')
const userGrowthChart = ref({})
const toolUsageChart = ref({})

// 最近活动
const recentActivities = ref([
  {
    id: 1,
    title: '新用户注册',
    description: '用户 "张三" 刚刚注册了账号',
    timestamp: '2024-01-15 14:30',
    type: 'primary'
  },
  {
    id: 2,
    title: '工具使用',
    description: '用户 "李四" 使用了PDF转换工具',
    timestamp: '2024-01-15 14:25',
    type: 'success'
  },
  {
    id: 3,
    title: '健身数据',
    description: '用户 "王五" 完成了今日健身打卡',
    timestamp: '2024-01-15 14:20',
    type: 'warning'
  },
  {
    id: 4,
    title: '社交互动',
    description: '用户 "赵六" 在聊天室发送了消息',
    timestamp: '2024-01-15 14:15',
    type: 'info'
  }
])

// 初始化数据
onMounted(() => {
  loadStats()
  initCharts()
})

// 加载统计数据
const loadStats = async () => {
  try {
    // 这里应该调用API获取真实数据
    // 现在使用模拟数据
    stats.totalUsers = 1234
    stats.activeUsers = 567
    stats.totalTools = 8901
    stats.totalShares = 234
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

// 初始化图表
const initCharts = () => {
  // 用户增长趋势图
  userGrowthChart.value = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '新增用户',
        type: 'line',
        data: [120, 200, 150, 80, 70, 110, 130],
        smooth: true,
        itemStyle: {
          color: '#409eff'
        }
      }
    ]
  }
  
  // 工具使用分布图
  toolUsageChart.value = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '工具使用',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 335, name: 'PDF转换' },
          { value: 310, name: '网页爬虫' },
          { value: 234, name: '测试用例' },
          { value: 135, name: '代码格式化' },
          { value: 548, name: '其他工具' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
}

// 刷新活动
const refreshActivities = () => {
  // 这里应该调用API获取最新活动
  console.log('Refreshing activities...')
}
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.dashboard-header {
  margin-bottom: 24px;
}

.dashboard-header h1 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.dashboard-header p {
  margin: 0;
  color: #909399;
  font-size: 16px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: white;
}

.stat-icon.users {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.fitness {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.tools {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.social {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.charts-row {
  margin-bottom: 24px;
}

.chart-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #303133;
}

.chart-container {
  width: 100%;
}

.activity-row {
  margin-bottom: 24px;
}

.activity-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.quick-actions-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-btn {
  width: 100%;
  justify-content: flex-start;
  height: 44px;
}

.action-btn .el-icon {
  margin-right: 8px;
}
</style>
