<template>
  <div class="settings-page">
    <div class="page-header">
      <h1>系统设置</h1>
    </div>
    
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="settings-card">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="基本设置" name="basic">
              <basic-settings />
            </el-tab-pane>
            <el-tab-pane label="功能管理" name="features">
              <feature-settings />
            </el-tab-pane>
            <el-tab-pane label="通知设置" name="notifications">
              <notification-settings />
            </el-tab-pane>
            <el-tab-pane label="安全设置" name="security">
              <security-settings />
            </el-tab-pane>
            <el-tab-pane label="API设置" name="api">
              <api-settings />
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="info-card">
          <template #header>
            <span>系统信息</span>
          </template>
          <div class="system-info">
            <div class="info-item">
              <span class="label">系统版本:</span>
              <span class="value">v1.0.0</span>
            </div>
            <div class="info-item">
              <span class="label">运行时间:</span>
              <span class="value">15天 8小时</span>
            </div>
            <div class="info-item">
              <span class="label">数据库状态:</span>
              <el-tag type="success">正常</el-tag>
            </div>
            <div class="info-item">
              <span class="label">Redis状态:</span>
              <el-tag type="success">正常</el-tag>
            </div>
            <div class="info-item">
              <span class="label">Celery状态:</span>
              <el-tag type="success">正常</el-tag>
            </div>
          </div>
        </el-card>
        
        <el-card class="quick-actions-card">
          <template #header>
            <span>快速操作</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="handleBackup" class="action-btn">
              <el-icon><Download /></el-icon>
              备份数据
            </el-button>
            <el-button type="warning" @click="handleClearCache" class="action-btn">
              <el-icon><Delete /></el-icon>
              清理缓存
            </el-button>
            <el-button type="info" @click="handleRestart" class="action-btn">
              <el-icon><Refresh /></el-icon>
              重启服务
            </el-button>
            <el-button type="danger" @click="handleShutdown" class="action-btn">
              <el-icon><SwitchButton /></el-icon>
              关闭系统
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import BasicSettings from '@/components/settings/BasicSettings.vue'
import FeatureSettings from '@/components/settings/FeatureSettings.vue'
import NotificationSettings from '@/components/settings/NotificationSettings.vue'
import SecuritySettings from '@/components/settings/SecuritySettings.vue'
import APISettings from '@/components/settings/APISettings.vue'

const activeTab = ref('basic')

// 备份数据
const handleBackup = async () => {
  try {
    await ElMessageBox.confirm('确定要备份系统数据吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.success('备份任务已启动')
  } catch (error) {
    // 用户取消
  }
}

// 清理缓存
const handleClearCache = async () => {
  try {
    await ElMessageBox.confirm('确定要清理系统缓存吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.success('缓存清理完成')
  } catch (error) {
    // 用户取消
  }
}

// 重启服务
const handleRestart = async () => {
  try {
    await ElMessageBox.confirm('确定要重启系统服务吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'error'
    })
    ElMessage.success('服务重启中...')
  } catch (error) {
    // 用户取消
  }
}

// 关闭系统
const handleShutdown = async () => {
  try {
    await ElMessageBox.confirm('确定要关闭系统吗？此操作将停止所有服务！', '危险操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'error'
    })
    ElMessage.success('系统关闭中...')
  } catch (error) {
    // 用户取消
  }
}
</script>

<style scoped>
.settings-page {
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

.settings-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.info-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.quick-actions-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.system-info {
  padding: 0;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  color: #606266;
  font-size: 14px;
}

.value {
  color: #303133;
  font-size: 14px;
  font-weight: 500;
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
