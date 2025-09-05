<template>
  <div class="fitness-page">
    <div class="page-header">
      <h1>健身管理</h1>
      <el-button type="primary" @click="showStatsDialog = true">
        <el-icon><DataAnalysis /></el-icon>
        数据统计
      </el-button>
    </div>
    
    <!-- 健身数据概览 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Trophy /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ fitnessStats.totalWorkouts }}</div>
              <div class="stat-label">总训练次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Timer /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ fitnessStats.totalDuration }}</div>
              <div class="stat-label">总训练时长(分钟)</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Medal /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ fitnessStats.totalAchievements }}</div>
              <div class="stat-label">获得成就</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ fitnessStats.activeUsers }}</div>
              <div class="stat-label">活跃用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 筛选和搜索 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="用户">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="训练类型">
          <el-select v-model="searchForm.workout_type" placeholder="请选择训练类型" clearable>
            <el-option label="有氧运动" value="cardio" />
            <el-option label="力量训练" value="strength" />
            <el-option label="柔韧性训练" value="flexibility" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 训练记录表格 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="workouts"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user.username" label="用户" width="120" />
        <el-table-column prop="workout_type" label="训练类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getWorkoutTypeTag(row.workout_type)">
              {{ getWorkoutTypeName(row.workout_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="时长(分钟)" width="120" />
        <el-table-column prop="calories_burned" label="消耗卡路里" width="120" />
        <el-table-column prop="notes" label="备注" min-width="200" />
        <el-table-column prop="created_at" label="训练时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleView(row)">查看</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 数据统计对话框 -->
    <el-dialog
      v-model="showStatsDialog"
      title="健身数据统计"
      width="800px"
    >
      <div class="stats-content">
        <el-row :gutter="20">
          <el-col :span="12">
            <h3>训练类型分布</h3>
            <div class="chart-container">
              <v-chart :option="workoutTypeChart" style="height: 300px;" />
            </div>
          </el-col>
          <el-col :span="12">
            <h3>每日训练时长</h3>
            <div class="chart-container">
              <v-chart :option="dailyDurationChart" style="height: 300px;" />
            </div>
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, LineChart } from 'echarts/charts'
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
  PieChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const loading = ref(false)
const showStatsDialog = ref(false)

// 健身统计数据
const fitnessStats = reactive({
  totalWorkouts: 0,
  totalDuration: 0,
  totalAchievements: 0,
  activeUsers: 0
})

// 搜索表单
const searchForm = reactive({
  username: '',
  workout_type: '',
  dateRange: [] as string[]
})

// 训练记录列表
const workouts = ref<any[]>([])

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 图表数据
const workoutTypeChart = ref({})
const dailyDurationChart = ref({})

// 获取训练类型标签
const getWorkoutTypeTag = (type: string) => {
  const tags: Record<string, string> = {
    cardio: 'success',
    strength: 'warning',
    flexibility: 'info',
    other: 'default'
  }
  return tags[type] || 'default'
}

// 获取训练类型名称
const getWorkoutTypeName = (type: string) => {
  const names: Record<string, string> = {
    cardio: '有氧运动',
    strength: '力量训练',
    flexibility: '柔韧性训练',
    other: '其他'
  }
  return names[type] || '未知'
}

// 加载健身数据
const loadFitnessData = async () => {
  loading.value = true
  try {
    // 这里应该调用API获取健身数据
    // 现在使用模拟数据
    fitnessStats.totalWorkouts = 1234
    fitnessStats.totalDuration = 5678
    fitnessStats.totalAchievements = 89
    fitnessStats.activeUsers = 156
    
    workouts.value = [
      {
        id: 1,
        user: { username: 'user1' },
        workout_type: 'cardio',
        duration: 30,
        calories_burned: 300,
        notes: '跑步训练',
        created_at: '2024-01-15 14:30:00'
      },
      {
        id: 2,
        user: { username: 'user2' },
        workout_type: 'strength',
        duration: 45,
        calories_burned: 450,
        notes: '举重训练',
        created_at: '2024-01-15 16:20:00'
      }
    ]
    pagination.total = workouts.value.length
  } catch (error) {
    ElMessage.error('加载健身数据失败')
  } finally {
    loading.value = false
  }
}

// 初始化图表
const initCharts = () => {
  // 训练类型分布图
  workoutTypeChart.value = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '训练类型',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 335, name: '有氧运动' },
          { value: 310, name: '力量训练' },
          { value: 234, name: '柔韧性训练' },
          { value: 135, name: '其他' }
        ]
      }
    ]
  }
  
  // 每日训练时长图
  dailyDurationChart.value = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: {
      type: 'value',
      name: '时长(分钟)'
    },
    series: [
      {
        name: '训练时长',
        type: 'line',
        data: [30, 45, 60, 35, 50, 40, 25],
        smooth: true
      }
    ]
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadFitnessData()
}

// 重置搜索
const handleReset = () => {
  Object.assign(searchForm, {
    username: '',
    workout_type: '',
    dateRange: []
  })
  handleSearch()
}

// 查看详情
const handleView = (workout: any) => {
  ElMessage.info(`查看训练记录: ${workout.id}`)
}

// 删除记录
const handleDelete = async (workout: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除这条训练记录吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    
    const index = workouts.value.findIndex(w => w.id === workout.id)
    if (index > -1) {
      workouts.value.splice(index, 1)
      pagination.total--
    }
    ElMessage.success('删除成功')
  } catch (error) {
    // 用户取消
  }
}

// 分页处理
const handleSizeChange = (size: number) => {
  pagination.size = size
  loadFitnessData()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadFitnessData()
}

onMounted(() => {
  loadFitnessData()
  initCharts()
})
</script>

<style scoped>
.fitness-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.stats-row {
  margin-bottom: 20px;
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

.search-card {
  margin-bottom: 20px;
}

.table-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.stats-content h3 {
  margin-bottom: 16px;
  color: #303133;
}

.chart-container {
  width: 100%;
}
</style>
