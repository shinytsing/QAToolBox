<template>
  <div class="life-page">
    <div class="page-header">
      <h1>生活助手</h1>
      <p>让生活更简单，让每一天都充满意义</p>
    </div>
    
    <!-- 生活工具 -->
    <div class="tools-section">
      <div class="tools-grid">
        <div class="tool-card" @click="showDiaryDialog = true">
          <div class="tool-icon diary">
            <el-icon><Document /></el-icon>
          </div>
          <h3>生活日记</h3>
          <p>记录生活中的美好瞬间</p>
        </div>
        
        <div class="tool-card" @click="showFoodDialog = true">
          <div class="tool-icon food">
            <el-icon><Food /></el-icon>
          </div>
          <h3>食物推荐</h3>
          <p>根据心情推荐美食</p>
        </div>
        
        <div class="tool-card" @click="showCheckinDialog = true">
          <div class="tool-icon checkin">
            <el-icon><Calendar /></el-icon>
          </div>
          <h3>每日签到</h3>
          <p>保持好习惯，记录成长</p>
        </div>
        
        <div class="tool-card" @click="showMeditationDialog = true">
          <div class="tool-icon meditation">
            <el-icon><Moon /></el-icon>
          </div>
          <h3>冥想放松</h3>
          <p>静心冥想，释放压力</p>
        </div>
        
        <div class="tool-card" @click="showAIWritingDialog = true">
          <div class="tool-icon ai">
            <el-icon><MagicStick /></el-icon>
          </div>
          <h3>AI文案</h3>
          <p>智能生成创意文案</p>
        </div>
      </div>
    </div>
    
    <!-- 最近记录 -->
    <div class="recent-section">
      <h2>最近记录</h2>
      <div class="recent-list">
        <div 
          v-for="record in recentRecords" 
          :key="record.id"
          class="record-item"
        >
          <div class="record-icon">
            <el-icon><component :is="record.icon" /></el-icon>
          </div>
          <div class="record-content">
            <h4>{{ record.title }}</h4>
            <p>{{ record.description }}</p>
            <span class="record-time">{{ record.time }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 日记对话框 -->
    <el-dialog
      v-model="showDiaryDialog"
      title="写日记"
      width="600px"
    >
      <el-form :model="diaryForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="diaryForm.title" placeholder="请输入日记标题" />
        </el-form-item>
        <el-form-item label="心情">
          <el-select v-model="diaryForm.mood" placeholder="选择心情">
            <el-option label="开心" value="happy" />
            <el-option label="平静" value="calm" />
            <el-option label="兴奋" value="excited" />
            <el-option label="难过" value="sad" />
            <el-option label="愤怒" value="angry" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容">
          <el-input 
            v-model="diaryForm.content" 
            type="textarea" 
            :rows="6"
            placeholder="记录今天的心情和感受..."
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showDiaryDialog = false">取消</el-button>
        <el-button type="primary" @click="saveDiary">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 食物推荐对话框 -->
    <el-dialog
      v-model="showFoodDialog"
      title="食物推荐"
      width="500px"
    >
      <div class="food-recommendation">
        <h3>今日推荐</h3>
        <div class="food-item">
          <img src="https://via.placeholder.com/200x150/4A90E2/FFFFFF?text=推荐食物" alt="推荐食物" />
          <div class="food-info">
            <h4>健康沙拉</h4>
            <p>新鲜蔬菜搭配，营养均衡</p>
            <el-button type="primary" size="small">查看详情</el-button>
          </div>
        </div>
      </div>
    </el-dialog>
    
    <!-- 签到对话框 -->
    <el-dialog
      v-model="showCheckinDialog"
      title="每日签到"
      width="400px"
    >
      <div class="checkin-content">
        <div class="checkin-stats">
          <div class="stat-item">
            <div class="stat-number">{{ checkinStats.streakDays }}</div>
            <div class="stat-label">连续签到</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ checkinStats.totalDays }}</div>
            <div class="stat-label">总签到天数</div>
          </div>
        </div>
        <el-button type="primary" @click="doCheckin" :disabled="checkinStats.todayChecked">
          {{ checkinStats.todayChecked ? '今日已签到' : '立即签到' }}
        </el-button>
      </div>
    </el-dialog>
    
    <!-- 冥想对话框 -->
    <el-dialog
      v-model="showMeditationDialog"
      title="冥想放松"
      width="500px"
    >
      <div class="meditation-content">
        <h3>选择冥想类型</h3>
        <div class="meditation-types">
          <div class="meditation-type" @click="startMeditation('breathing')">
            <el-icon><WindPower /></el-icon>
            <span>呼吸冥想</span>
          </div>
          <div class="meditation-type" @click="startMeditation('body')">
            <el-icon><Sunny /></el-icon>
            <span>身体扫描</span>
          </div>
          <div class="meditation-type" @click="startMeditation('mindfulness')">
            <el-icon><Moon /></el-icon>
            <span>正念冥想</span>
          </div>
        </div>
      </div>
    </el-dialog>
    
    <!-- AI文案对话框 -->
    <el-dialog
      v-model="showAIWritingDialog"
      title="AI文案生成"
      width="600px"
    >
      <el-form :model="aiForm" label-width="80px">
        <el-form-item label="文案类型">
          <el-select v-model="aiForm.type" placeholder="选择文案类型">
            <el-option label="朋友圈文案" value="moments" />
            <el-option label="工作汇报" value="report" />
            <el-option label="节日祝福" value="greeting" />
            <el-option label="创意写作" value="creative" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="aiForm.keywords" placeholder="输入关键词" />
        </el-form-item>
        <el-form-item label="生成内容">
          <el-input 
            v-model="aiForm.content" 
            type="textarea" 
            :rows="4"
            placeholder="AI生成的文案将显示在这里..."
            readonly
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAIWritingDialog = false">关闭</el-button>
        <el-button type="primary" @click="generateAI">生成文案</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 对话框状态
const showDiaryDialog = ref(false)
const showFoodDialog = ref(false)
const showCheckinDialog = ref(false)
const showMeditationDialog = ref(false)
const showAIWritingDialog = ref(false)

// 日记表单
const diaryForm = reactive({
  title: '',
  mood: '',
  content: ''
})

// 签到统计
const checkinStats = reactive({
  streakDays: 7,
  totalDays: 45,
  todayChecked: false
})

// AI表单
const aiForm = reactive({
  type: '',
  keywords: '',
  content: ''
})

// 最近记录
const recentRecords = ref([
  {
    id: 1,
    title: '今日日记',
    description: '今天天气很好，心情也很不错',
    time: '2小时前',
    icon: 'Document'
  },
  {
    id: 2,
    title: '每日签到',
    description: '连续签到第7天',
    time: '4小时前',
    icon: 'Calendar'
  },
  {
    id: 3,
    title: '冥想练习',
    description: '完成了15分钟的正念冥想',
    time: '6小时前',
    icon: 'Moon'
  }
])

// 保存日记
const saveDiary = () => {
  if (!diaryForm.title || !diaryForm.content) {
    ElMessage.warning('请填写标题和内容')
    return
  }
  
  // 这里应该调用API保存日记
  ElMessage.success('日记保存成功')
  showDiaryDialog.value = false
  
  // 重置表单
  Object.assign(diaryForm, {
    title: '',
    mood: '',
    content: ''
  })
}

// 签到
const doCheckin = () => {
  checkinStats.streakDays++
  checkinStats.totalDays++
  checkinStats.todayChecked = true
  ElMessage.success('签到成功！')
}

// 开始冥想
const startMeditation = (type: string) => {
  ElMessage.info(`开始${type}冥想`)
  showMeditationDialog.value = false
}

// 生成AI文案
const generateAI = () => {
  if (!aiForm.type || !aiForm.keywords) {
    ElMessage.warning('请选择文案类型并输入关键词')
    return
  }
  
  // 这里应该调用AI API生成文案
  aiForm.content = `基于"${aiForm.keywords}"生成的${aiForm.type}文案：这是一段由AI生成的创意文案，可以根据您的需求进行个性化定制。`
  ElMessage.success('文案生成成功')
}

onMounted(() => {
  // 初始化数据
})
</script>

<style scoped>
.life-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 32px;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: #909399;
  font-size: 16px;
}

.tools-section {
  margin-bottom: 40px;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.tool-card {
  background: white;
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid #f0f0f0;
}

.tool-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.tool-icon {
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

.tool-icon.diary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.tool-icon.food {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.tool-icon.checkin {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.tool-icon.meditation {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.tool-icon.ai {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.tool-card h3 {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.tool-card p {
  color: #606266;
  margin: 0;
  line-height: 1.5;
}

.recent-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.recent-section h2 {
  margin: 0 0 24px 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.recent-list {
  display: grid;
  gap: 16px;
}

.record-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
}

.record-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #e3f2fd;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  color: #2196f3;
  font-size: 20px;
}

.record-content {
  flex: 1;
}

.record-content h4 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.record-content p {
  color: #606266;
  margin-bottom: 8px;
}

.record-time {
  color: #909399;
  font-size: 12px;
}

.food-recommendation h3 {
  margin-bottom: 16px;
  color: #303133;
}

.food-item {
  display: flex;
  gap: 16px;
  align-items: center;
}

.food-item img {
  width: 120px;
  height: 90px;
  border-radius: 8px;
  object-fit: cover;
}

.food-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.food-info p {
  margin: 0 0 12px 0;
  color: #606266;
}

.checkin-content {
  text-align: center;
}

.checkin-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 24px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 4px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.meditation-content h3 {
  margin-bottom: 16px;
  color: #303133;
}

.meditation-types {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.meditation-type {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.meditation-type:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.meditation-type .el-icon {
  font-size: 24px;
  color: #409eff;
  margin-bottom: 8px;
}

.meditation-type span {
  color: #303133;
  font-size: 14px;
}

@media (max-width: 768px) {
  .life-page {
    padding: 16px;
  }
  
  .tools-grid {
    grid-template-columns: 1fr;
  }
  
  .tool-card {
    padding: 24px 16px;
  }
  
  .meditation-types {
    grid-template-columns: 1fr;
  }
  
  .checkin-stats {
    gap: 20px;
  }
}
</style>
