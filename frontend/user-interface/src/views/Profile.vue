<template>
  <div class="profile-page">
    <div class="profile-header">
      <div class="profile-avatar">
        <el-avatar :size="120" :src="userProfile.avatar">
          {{ userProfile.username?.charAt(0).toUpperCase() }}
        </el-avatar>
        <el-button type="primary" @click="showEditDialog = true" class="edit-btn">
          <el-icon><Edit /></el-icon>
          编辑资料
        </el-button>
      </div>
      
      <div class="profile-info">
        <h1>{{ userProfile.username }}</h1>
        <p>{{ userProfile.email }}</p>
        <div class="profile-stats">
          <div class="stat-item">
            <div class="stat-number">{{ userProfile.totalWorkouts }}</div>
            <div class="stat-label">训练次数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ userProfile.totalTools }}</div>
            <div class="stat-label">工具使用</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ userProfile.totalSocial }}</div>
            <div class="stat-label">社交活动</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ userProfile.totalDays }}</div>
            <div class="stat-label">使用天数</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 个人数据 -->
    <div class="profile-content">
      <el-row :gutter="20">
        <el-col :span="16">
          <!-- 最近活动 -->
          <div class="section-card">
            <h2>最近活动</h2>
            <div class="activity-timeline">
              <div 
                v-for="activity in recentActivities" 
                :key="activity.id"
                class="timeline-item"
              >
                <div class="timeline-icon">
                  <el-icon><component :is="activity.icon" /></el-icon>
                </div>
                <div class="timeline-content">
                  <h4>{{ activity.title }}</h4>
                  <p>{{ activity.description }}</p>
                  <span class="timeline-time">{{ activity.time }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 成就徽章 -->
          <div class="section-card">
            <h2>成就徽章</h2>
            <div class="badges-grid">
              <div 
                v-for="badge in badges" 
                :key="badge.id"
                class="badge-item"
                :class="{ 'earned': badge.earned }"
              >
                <div class="badge-icon">
                  <el-icon><component :is="badge.icon" /></el-icon>
                </div>
                <h4>{{ badge.name }}</h4>
                <p>{{ badge.description }}</p>
              </div>
            </div>
          </div>
        </el-col>
        
        <el-col :span="8">
          <!-- 个人设置 -->
          <div class="section-card">
            <h2>个人设置</h2>
            <div class="settings-list">
              <div class="setting-item" @click="showPasswordDialog = true">
                <el-icon><Lock /></el-icon>
                <span>修改密码</span>
                <el-icon><ArrowRight /></el-icon>
              </div>
              <div class="setting-item" @click="showNotificationDialog = true">
                <el-icon><Bell /></el-icon>
                <span>通知设置</span>
                <el-icon><ArrowRight /></el-icon>
              </div>
              <div class="setting-item" @click="showPrivacyDialog = true">
                <el-icon><View /></el-icon>
                <span>隐私设置</span>
                <el-icon><ArrowRight /></el-icon>
              </div>
              <div class="setting-item" @click="showThemeDialog = true">
                <el-icon><Sunny /></el-icon>
                <span>主题设置</span>
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </div>
          
          <!-- 数据统计 -->
          <div class="section-card">
            <h2>数据统计</h2>
            <div class="stats-chart">
              <div class="chart-item">
                <h4>本周训练</h4>
                <div class="chart-bar">
                  <div class="bar" style="width: 60%"></div>
                </div>
                <span>6/10 次</span>
              </div>
              <div class="chart-item">
                <h4>工具使用</h4>
                <div class="chart-bar">
                  <div class="bar" style="width: 80%"></div>
                </div>
                <span>8/10 次</span>
              </div>
              <div class="chart-item">
                <h4>社交互动</h4>
                <div class="chart-bar">
                  <div class="bar" style="width: 40%"></div>
                </div>
                <span>4/10 次</span>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
    
    <!-- 编辑资料对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑个人资料"
      width="500px"
    >
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="editForm.firstName" />
        </el-form-item>
        <el-form-item label="头像">
          <el-upload
            class="avatar-uploader"
            action="#"
            :show-file-list="false"
            :on-change="handleAvatarChange"
          >
            <img v-if="editForm.avatar" :src="editForm.avatar" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="showPasswordDialog"
      title="修改密码"
      width="400px"
    >
      <el-form :model="passwordForm" label-width="80px">
        <el-form-item label="当前密码">
          <el-input v-model="passwordForm.currentPassword" type="password" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="changePassword">修改</el-button>
      </template>
    </el-dialog>
    
    <!-- 通知设置对话框 -->
    <el-dialog
      v-model="showNotificationDialog"
      title="通知设置"
      width="400px"
    >
      <el-form :model="notificationForm" label-width="120px">
        <el-form-item label="邮件通知">
          <el-switch v-model="notificationForm.email" />
        </el-form-item>
        <el-form-item label="推送通知">
          <el-switch v-model="notificationForm.push" />
        </el-form-item>
        <el-form-item label="系统通知">
          <el-switch v-model="notificationForm.system" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showNotificationDialog = false">取消</el-button>
        <el-button type="primary" @click="saveNotification">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 隐私设置对话框 -->
    <el-dialog
      v-model="showPrivacyDialog"
      title="隐私设置"
      width="400px"
    >
      <el-form :model="privacyForm" label-width="120px">
        <el-form-item label="公开资料">
          <el-switch v-model="privacyForm.publicProfile" />
        </el-form-item>
        <el-form-item label="显示活动">
          <el-switch v-model="privacyForm.showActivity" />
        </el-form-item>
        <el-form-item label="允许搜索">
          <el-switch v-model="privacyForm.allowSearch" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showPrivacyDialog = false">取消</el-button>
        <el-button type="primary" @click="savePrivacy">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 主题设置对话框 -->
    <el-dialog
      v-model="showThemeDialog"
      title="主题设置"
      width="400px"
    >
      <el-form :model="themeForm" label-width="80px">
        <el-form-item label="主题模式">
          <el-radio-group v-model="themeForm.mode">
            <el-radio label="light">浅色模式</el-radio>
            <el-radio label="dark">深色模式</el-radio>
            <el-radio label="auto">跟随系统</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="主题色彩">
          <el-color-picker v-model="themeForm.color" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showThemeDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTheme">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()

// 对话框状态
const showEditDialog = ref(false)
const showPasswordDialog = ref(false)
const showNotificationDialog = ref(false)
const showPrivacyDialog = ref(false)
const showThemeDialog = ref(false)

// 用户资料
const userProfile = reactive({
  username: '',
  email: '',
  avatar: '',
  totalWorkouts: 0,
  totalTools: 0,
  totalSocial: 0,
  totalDays: 0
})

// 编辑表单
const editForm = reactive({
  username: '',
  email: '',
  firstName: '',
  avatar: ''
})

// 密码表单
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 通知设置
const notificationForm = reactive({
  email: true,
  push: true,
  system: true
})

// 隐私设置
const privacyForm = reactive({
  publicProfile: true,
  showActivity: true,
  allowSearch: true
})

// 主题设置
const themeForm = reactive({
  mode: 'light',
  color: '#409eff'
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
    title: '参与聊天室讨论',
    description: '在技术交流群中分享经验',
    time: '6小时前',
    icon: 'ChatDotRound'
  }
])

// 成就徽章
const badges = ref([
  {
    id: 1,
    name: '健身达人',
    description: '连续训练7天',
    icon: 'Trophy',
    earned: true
  },
  {
    id: 2,
    name: '工具专家',
    description: '使用10种工具',
    icon: 'Tools',
    earned: true
  },
  {
    id: 3,
    name: '社交之星',
    description: '参与50次社交活动',
    icon: 'ChatDotRound',
    earned: false
  },
  {
    id: 4,
    name: '生活记录者',
    description: '写100篇日记',
    icon: 'Document',
    earned: false
  }
])

// 加载用户资料
const loadUserProfile = async () => {
  try {
    // 这里应该调用API获取用户资料
    Object.assign(userProfile, {
      username: authStore.user?.username || '用户',
      email: authStore.user?.email || 'user@example.com',
      avatar: authStore.user?.avatar || '',
      totalWorkouts: 25,
      totalTools: 15,
      totalSocial: 8,
      totalDays: 30
    })
    
    // 初始化编辑表单
    Object.assign(editForm, {
      username: userProfile.username,
      email: userProfile.email,
      firstName: userProfile.username,
      avatar: userProfile.avatar
    })
  } catch (error) {
    console.error('加载用户资料失败:', error)
  }
}

// 头像上传
const handleAvatarChange = (file: any) => {
  editForm.avatar = URL.createObjectURL(file.raw)
}

// 保存资料
const saveProfile = () => {
  Object.assign(userProfile, editForm)
  ElMessage.success('资料保存成功')
  showEditDialog.value = false
}

// 修改密码
const changePassword = () => {
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.error('两次输入密码不一致')
    return
  }
  ElMessage.success('密码修改成功')
  showPasswordDialog.value = false
}

// 保存通知设置
const saveNotification = () => {
  ElMessage.success('通知设置保存成功')
  showNotificationDialog.value = false
}

// 保存隐私设置
const savePrivacy = () => {
  ElMessage.success('隐私设置保存成功')
  showPrivacyDialog.value = false
}

// 保存主题设置
const saveTheme = () => {
  ElMessage.success('主题设置保存成功')
  showThemeDialog.value = false
}

onMounted(() => {
  loadUserProfile()
})
</script>

<style scoped>
.profile-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.profile-header {
  background: white;
  border-radius: 16px;
  padding: 40px;
  margin-bottom: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 40px;
}

.profile-avatar {
  text-align: center;
}

.edit-btn {
  margin-top: 16px;
}

.profile-info {
  flex: 1;
}

.profile-info h1 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 32px;
  font-weight: 600;
}

.profile-info p {
  margin: 0 0 24px 0;
  color: #909399;
  font-size: 16px;
}

.profile-stats {
  display: flex;
  gap: 40px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 28px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 4px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.profile-content {
  display: grid;
  gap: 20px;
}

.section-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.section-card h2 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.activity-timeline {
  display: grid;
  gap: 16px;
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.timeline-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e3f2fd;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2196f3;
  font-size: 18px;
  flex-shrink: 0;
}

.timeline-content {
  flex: 1;
}

.timeline-content h4 {
  margin: 0 0 4px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.timeline-content p {
  margin: 0 0 8px 0;
  color: #606266;
  line-height: 1.5;
}

.timeline-time {
  color: #909399;
  font-size: 12px;
}

.badges-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.badge-item {
  text-align: center;
  padding: 20px;
  border: 2px solid #e6e6e6;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.badge-item.earned {
  border-color: #409eff;
  background: #f0f9ff;
}

.badge-item.earned .badge-icon {
  color: #409eff;
}

.badge-icon {
  font-size: 32px;
  color: #c0c4cc;
  margin-bottom: 12px;
}

.badge-item h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.badge-item p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.settings-list {
  display: grid;
  gap: 12px;
}

.setting-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.setting-item:hover {
  background: #e3f2fd;
}

.setting-item .el-icon:first-child {
  margin-right: 12px;
  color: #409eff;
}

.setting-item span {
  flex: 1;
  color: #303133;
  font-weight: 500;
}

.setting-item .el-icon:last-child {
  color: #c0c4cc;
}

.stats-chart {
  display: grid;
  gap: 20px;
}

.chart-item h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.chart-bar {
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  margin-bottom: 8px;
  overflow: hidden;
}

.bar {
  height: 100%;
  background: linear-gradient(90deg, #409eff, #67c23a);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.chart-item span {
  color: #909399;
  font-size: 12px;
}

.avatar-uploader {
  text-align: center;
}

.avatar-uploader .avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  line-height: 100px;
  text-align: center;
  border: 1px dashed #d9d9d9;
  border-radius: 50%;
}

@media (max-width: 768px) {
  .profile-page {
    padding: 16px;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
    padding: 24px;
  }
  
  .profile-stats {
    gap: 20px;
  }
  
  .badges-grid {
    grid-template-columns: 1fr;
  }
}
</style>
