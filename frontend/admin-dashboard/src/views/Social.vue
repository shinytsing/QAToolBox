<template>
  <div class="social-page">
    <div class="page-header">
      <h1>社交娱乐管理</h1>
    </div>
    
    <!-- 社交统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon chat">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ socialStats.chatCount }}</div>
              <div class="stat-label">聊天消息</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon heart">
              <el-icon><Heart /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ socialStats.heartLinkCount }}</div>
              <div class="stat-label">心链连接</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon tarot">
              <el-icon><MagicStick /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ socialStats.tarotCount }}</div>
              <div class="stat-label">塔罗占卜</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon story">
              <el-icon><Reading /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ socialStats.storyCount }}</div>
              <div class="stat-label">故事生成</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 社交功能管理 -->
    <el-card class="social-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="聊天管理" name="chat">
          <chat-management />
        </el-tab-pane>
        <el-tab-pane label="心链管理" name="heart-link">
          <heart-link-management />
        </el-tab-pane>
        <el-tab-pane label="搭子活动" name="buddy-events">
          <buddy-events-management />
        </el-tab-pane>
        <el-tab-pane label="塔罗占卜" name="tarot">
          <tarot-management />
        </el-tab-pane>
        <el-tab-pane label="故事生成" name="story">
          <story-management />
        </el-tab-pane>
        <el-tab-pane label="旅游攻略" name="travel">
          <travel-management />
        </el-tab-pane>
        <el-tab-pane label="命运分析" name="fortune">
          <fortune-management />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import ChatManagement from '@/components/social/ChatManagement.vue'
import HeartLinkManagement from '@/components/social/HeartLinkManagement.vue'
import BuddyEventsManagement from '@/components/social/BuddyEventsManagement.vue'
import TarotManagement from '@/components/social/TarotManagement.vue'
import StoryManagement from '@/components/social/StoryManagement.vue'
import TravelManagement from '@/components/social/TravelManagement.vue'
import FortuneManagement from '@/components/social/FortuneManagement.vue'

const activeTab = ref('chat')

// 社交统计数据
const socialStats = reactive({
  chatCount: 0,
  heartLinkCount: 0,
  tarotCount: 0,
  storyCount: 0
})

// 切换标签页
const handleTabChange = (tab: string) => {
  console.log('切换到标签页:', tab)
}

// 加载统计数据
const loadStats = async () => {
  try {
    // 这里应该调用API获取统计数据
    socialStats.chatCount = 5678
    socialStats.heartLinkCount = 1234
    socialStats.tarotCount = 890
    socialStats.storyCount = 456
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.social-page {
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

.stat-icon.chat {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.heart {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.tarot {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.story {
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

.social-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>
