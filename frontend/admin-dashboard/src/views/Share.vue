<template>
  <div class="share-page">
    <div class="page-header">
      <h1>分享管理</h1>
    </div>
    
    <!-- 分享统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon share">
              <el-icon><Share /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ shareStats.totalShares }}</div>
              <div class="stat-label">总分享数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon links">
              <el-icon><Link /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ shareStats.activeLinks }}</div>
              <div class="stat-label">活跃链接</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon pwa">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ shareStats.pwaInstalls }}</div>
              <div class="stat-label">PWA安装</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon widgets">
              <el-icon><Grid /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ shareStats.widgetUses }}</div>
              <div class="stat-label">组件使用</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 分享管理 -->
    <el-card class="share-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="分享记录" name="records">
          <share-records-management />
        </el-tab-pane>
        <el-tab-pane label="分享链接" name="links">
          <share-links-management />
        </el-tab-pane>
        <el-tab-pane label="PWA管理" name="pwa">
          <pwa-management />
        </el-tab-pane>
        <el-tab-pane label="分享组件" name="widgets">
          <share-widgets-management />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import ShareRecordsManagement from '@/components/share/ShareRecordsManagement.vue'
import ShareLinksManagement from '@/components/share/ShareLinksManagement.vue'
import PWAManagement from '@/components/share/PWAManagement.vue'
import ShareWidgetsManagement from '@/components/share/ShareWidgetsManagement.vue'

const activeTab = ref('records')

// 分享统计数据
const shareStats = reactive({
  totalShares: 0,
  activeLinks: 0,
  pwaInstalls: 0,
  widgetUses: 0
})

// 切换标签页
const handleTabChange = (tab: string) => {
  console.log('切换到标签页:', tab)
}

// 加载统计数据
const loadStats = async () => {
  try {
    // 这里应该调用API获取统计数据
    shareStats.totalShares = 1234
    shareStats.activeLinks = 567
    shareStats.pwaInstalls = 89
    shareStats.widgetUses = 345
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.share-page {
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

.stat-icon.share {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.links {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.pwa {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.widgets {
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

.share-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>
