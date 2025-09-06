<template>
  <div class="dashboard-home">
    <el-row :gutter="20">
      <!-- 欢迎卡片 -->
      <el-col :span="24">
        <el-card class="welcome-card">
          <div class="welcome-content">
            <h2>欢迎使用 QAToolBox 管理后台</h2>
            <p>多平台统一管理系统 - 健身、生活、极客工具、社交娱乐</p>
            <div class="user-info">
              <el-tag type="success">当前用户: {{ authStore.user?.username }}</el-tag>
              <el-tag type="info">设备类型: {{ authStore.device?.device_type }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 系统统计 -->
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon fitness">
              <el-icon><Trophy /></el-icon>
            </div>
            <div class="stat-info">
              <h3>健身模块</h3>
              <p>训练计划、健身社区</p>
              <el-button type="primary" size="small" @click="$router.push('/fitness/workouts')">
                管理
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon life">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <h3>生活模块</h3>
              <p>日记、食物、签到</p>
              <el-button type="success" size="small" @click="$router.push('/life/diary')">
                管理
              </el-button>
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
              <h3>极客工具</h3>
              <p>PDF转换、爬虫、测试</p>
              <el-button type="warning" size="small" @click="$router.push('/tools/pdf')">
                管理
              </el-button>
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
              <h3>社交娱乐</h3>
              <p>聊天、心链、塔罗</p>
              <el-button type="danger" size="small" @click="$router.push('/social/chat')">
                管理
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 快速操作 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快速操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/admin/users')">
              <el-icon><User /></el-icon>
              用户管理
            </el-button>
            <el-button type="success" @click="$router.push('/admin/features')">
              <el-icon><Setting /></el-icon>
              功能管理
            </el-button>
            <el-button type="info" @click="$router.push('/admin/stats')">
              <el-icon><DataAnalysis /></el-icon>
              系统统计
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 系统状态 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统状态</span>
            </div>
          </template>
          <div class="system-status">
            <el-row>
              <el-col :span="12">
                <div class="status-item">
                  <el-tag type="success">后端服务</el-tag>
                  <span>运行中</span>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="status-item">
                  <el-tag type="success">数据库</el-tag>
                  <span>连接正常</span>
                </div>
              </el-col>
            </el-row>
            <el-row style="margin-top: 10px;">
              <el-col :span="12">
                <div class="status-item">
                  <el-tag type="success">API服务</el-tag>
                  <span>正常</span>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="status-item">
                  <el-tag type="success">认证系统</el-tag>
                  <span>JWT正常</span>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

<style scoped>
.dashboard-home {
  padding: 20px;
}

.welcome-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.welcome-content h2 {
  margin: 0 0 10px 0;
  font-size: 28px;
}

.welcome-content p {
  margin: 0 0 20px 0;
  font-size: 16px;
  opacity: 0.9;
}

.user-info {
  display: flex;
  gap: 10px;
}

.stat-card {
  height: 120px;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
  color: white;
}

.stat-icon.fitness {
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
}

.stat-icon.life {
  background: linear-gradient(135deg, #4ecdc4, #44a08d);
}

.stat-icon.tools {
  background: linear-gradient(135deg, #feca57, #ff9ff3);
}

.stat-icon.social {
  background: linear-gradient(135deg, #a8e6cf, #88d8c0);
}

.stat-info h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
}

.stat-info p {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 12px;
}

.card-header {
  font-weight: bold;
  font-size: 16px;
}

.quick-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.system-status {
  padding: 10px 0;
}

.status-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
</style>
