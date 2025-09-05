<template>
  <div class="life-tools-page">
    <div class="page-header">
      <h1>生活工具管理</h1>
    </div>
    
    <!-- 工具统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon diary">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ toolStats.diaryCount }}</div>
              <div class="stat-label">日记总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon food">
              <el-icon><Food /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ toolStats.foodCount }}</div>
              <div class="stat-label">食物推荐</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon checkin">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ toolStats.checkinCount }}</div>
              <div class="stat-label">签到记录</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon meditation">
              <el-icon><Moon /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ toolStats.meditationCount }}</div>
              <div class="stat-label">冥想记录</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 工具列表 -->
    <el-card class="tools-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="日记管理" name="diary">
          <diary-management />
        </el-tab-pane>
        <el-tab-pane label="食物推荐" name="food">
          <food-management />
        </el-tab-pane>
        <el-tab-pane label="签到管理" name="checkin">
          <checkin-management />
        </el-tab-pane>
        <el-tab-pane label="冥想管理" name="meditation">
          <meditation-management />
        </el-tab-pane>
        <el-tab-pane label="AI文案" name="ai-writing">
          <ai-writing-management />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import DiaryManagement from '@/components/life-tools/DiaryManagement.vue'
import FoodManagement from '@/components/life-tools/FoodManagement.vue'
import CheckinManagement from '@/components/life-tools/CheckinManagement.vue'
import MeditationManagement from '@/components/life-tools/MeditationManagement.vue'
import AIWritingManagement from '@/components/life-tools/AIWritingManagement.vue'

const activeTab = ref('diary')

// 工具统计数据
const toolStats = reactive({
  diaryCount: 0,
  foodCount: 0,
  checkinCount: 0,
  meditationCount: 0
})

// 切换标签页
const handleTabChange = (tab: string) => {
  console.log('切换到标签页:', tab)
}

// 加载统计数据
const loadStats = async () => {
  try {
    // 这里应该调用API获取统计数据
    toolStats.diaryCount = 1234
    toolStats.foodCount = 567
    toolStats.checkinCount = 890
    toolStats.meditationCount = 345
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.life-tools-page {
  padding: 0;
}

.page-header {
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
}

.stat-icon.diary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.food {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.checkin {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.meditation {
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

.tools-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>
