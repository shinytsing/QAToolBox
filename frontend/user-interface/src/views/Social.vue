<template>
  <div class="social-page">
    <div class="page-header">
      <h1>社交娱乐</h1>
      <p>连接世界，分享快乐</p>
    </div>
    
    <!-- 社交功能 -->
    <div class="features-section">
      <div class="features-grid">
        <div class="feature-card" @click="showChatDialog = true">
          <div class="feature-icon chat">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <h3>聊天室</h3>
          <p>与志同道合的朋友交流</p>
        </div>
        
        <div class="feature-card" @click="showHeartLinkDialog = true">
          <div class="feature-icon heart">
            <el-icon><Heart /></el-icon>
          </div>
          <h3>心链连接</h3>
          <p>寻找心灵契合的伙伴</p>
        </div>
        
        <div class="feature-card" @click="showBuddyDialog = true">
          <div class="feature-icon buddy">
            <el-icon><UserFilled /></el-icon>
          </div>
          <h3>搭子活动</h3>
          <p>组织或参与有趣的活动</p>
        </div>
        
        <div class="feature-card" @click="showTarotDialog = true">
          <div class="feature-icon tarot">
            <el-icon><MagicStick /></el-icon>
          </div>
          <h3>塔罗占卜</h3>
          <p>探索未知，指引方向</p>
        </div>
        
        <div class="feature-card" @click="showStoryDialog = true">
          <div class="feature-icon story">
            <el-icon><Reading /></el-icon>
          </div>
          <h3>故事生成</h3>
          <p>AI创作精彩故事</p>
        </div>
        
        <div class="feature-card" @click="showTravelDialog = true">
          <div class="feature-icon travel">
            <el-icon><Location /></el-icon>
          </div>
          <h3>旅游攻略</h3>
          <p>分享旅行经验和攻略</p>
        </div>
        
        <div class="feature-card" @click="showFortuneDialog = true">
          <div class="feature-icon fortune">
            <el-icon><Star /></el-icon>
          </div>
          <h3>命运分析</h3>
          <p>了解自己的命运走向</p>
        </div>
      </div>
    </div>
    
    <!-- 最近活动 -->
    <div class="activities-section">
      <h2>最近活动</h2>
      <div class="activities-list">
        <div 
          v-for="activity in recentActivities" 
          :key="activity.id"
          class="activity-item"
        >
          <div class="activity-avatar">
            <el-avatar :src="activity.avatar" :size="40">
              {{ activity.username.charAt(0) }}
            </el-avatar>
          </div>
          <div class="activity-content">
            <div class="activity-header">
              <span class="username">{{ activity.username }}</span>
              <span class="activity-time">{{ activity.time }}</span>
            </div>
            <p class="activity-text">{{ activity.content }}</p>
            <div class="activity-actions">
              <el-button size="small" type="text">
                <el-icon><ChatDotRound /></el-icon>
                {{ activity.comments }}
              </el-button>
              <el-button size="small" type="text">
                <el-icon><Heart /></el-icon>
                {{ activity.likes }}
              </el-button>
              <el-button size="small" type="text">
                <el-icon><Share /></el-icon>
                分享
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 聊天室对话框 -->
    <el-dialog
      v-model="showChatDialog"
      title="聊天室"
      width="800px"
    >
      <div class="chat-container">
        <div class="chat-messages">
          <div 
            v-for="message in chatMessages" 
            :key="message.id"
            class="message-item"
            :class="{ 'own-message': message.isOwn }"
          >
            <div class="message-avatar">
              <el-avatar :src="message.avatar" :size="32">
                {{ message.username.charAt(0) }}
              </el-avatar>
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="message-username">{{ message.username }}</span>
                <span class="message-time">{{ message.time }}</span>
              </div>
              <div class="message-text">{{ message.text }}</div>
            </div>
          </div>
        </div>
        <div class="chat-input">
          <el-input
            v-model="newMessage"
            placeholder="输入消息..."
            @keyup.enter="sendMessage"
          >
            <template #append>
              <el-button @click="sendMessage">发送</el-button>
            </template>
          </el-input>
        </div>
      </div>
    </el-dialog>
    
    <!-- 心链连接对话框 -->
    <el-dialog
      v-model="showHeartLinkDialog"
      title="心链连接"
      width="600px"
    >
      <div class="heart-link-content">
        <h3>寻找心灵契合的伙伴</h3>
        <p>通过兴趣爱好、性格特点等匹配志同道合的朋友</p>
        <el-form :model="heartLinkForm" label-width="80px">
          <el-form-item label="兴趣爱好">
            <el-checkbox-group v-model="heartLinkForm.interests">
              <el-checkbox label="运动">运动</el-checkbox>
              <el-checkbox label="音乐">音乐</el-checkbox>
              <el-checkbox label="电影">电影</el-checkbox>
              <el-checkbox label="读书">读书</el-checkbox>
              <el-checkbox label="旅行">旅行</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
          <el-form-item label="性格特点">
            <el-checkbox-group v-model="heartLinkForm.personality">
              <el-checkbox label="开朗">开朗</el-checkbox>
              <el-checkbox label="内向">内向</el-checkbox>
              <el-checkbox label="幽默">幽默</el-checkbox>
              <el-checkbox label="安静">安静</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>
        <el-button type="primary" @click="findHeartLink">开始匹配</el-button>
      </div>
    </el-dialog>
    
    <!-- 搭子活动对话框 -->
    <el-dialog
      v-model="showBuddyDialog"
      title="搭子活动"
      width="600px"
    >
      <div class="buddy-content">
        <h3>组织或参与活动</h3>
        <div class="activity-tabs">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="我的活动" name="my">
              <div class="my-activities">
                <el-button type="primary" @click="createActivity">创建活动</el-button>
                <div class="activity-list">
                  <div 
                    v-for="activity in myActivities" 
                    :key="activity.id"
                    class="activity-card"
                  >
                    <h4>{{ activity.title }}</h4>
                    <p>{{ activity.description }}</p>
                    <div class="activity-meta">
                      <span>{{ activity.date }}</span>
                      <span>{{ activity.participants }} 人参与</span>
                    </div>
                  </div>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="推荐活动" name="recommended">
              <div class="recommended-activities">
                <div 
                  v-for="activity in recommendedActivities" 
                  :key="activity.id"
                  class="activity-card"
                >
                  <h4>{{ activity.title }}</h4>
                  <p>{{ activity.description }}</p>
                  <div class="activity-meta">
                    <span>{{ activity.date }}</span>
                    <span>{{ activity.participants }} 人参与</span>
                  </div>
                  <el-button size="small" @click="joinActivity(activity)">参与</el-button>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </el-dialog>
    
    <!-- 塔罗占卜对话框 -->
    <el-dialog
      v-model="showTarotDialog"
      title="塔罗占卜"
      width="500px"
    >
      <div class="tarot-content">
        <h3>探索未知，指引方向</h3>
        <el-form :model="tarotForm" label-width="80px">
          <el-form-item label="占卜问题">
            <el-input 
              v-model="tarotForm.question" 
              placeholder="请输入您的问题..."
            />
          </el-form-item>
          <el-form-item label="占卜类型">
            <el-select v-model="tarotForm.type" placeholder="选择占卜类型">
              <el-option label="爱情运势" value="love" />
              <el-option label="事业运势" value="career" />
              <el-option label="财运" value="wealth" />
              <el-option label="健康运势" value="health" />
            </el-select>
          </el-form-item>
        </el-form>
        <div class="tarot-result" v-if="tarotResult">
          <h4>占卜结果</h4>
          <p>{{ tarotResult }}</p>
        </div>
        <el-button type="primary" @click="startTarot">开始占卜</el-button>
      </div>
    </el-dialog>
    
    <!-- 其他对话框 -->
    <el-dialog
      v-model="showStoryDialog"
      title="故事生成"
      width="600px"
    >
      <div class="story-content">
        <h3>AI创作精彩故事</h3>
        <el-form :model="storyForm" label-width="80px">
          <el-form-item label="故事主题">
            <el-input v-model="storyForm.theme" placeholder="请输入故事主题..." />
          </el-form-item>
          <el-form-item label="故事类型">
            <el-select v-model="storyForm.type" placeholder="选择故事类型">
              <el-option label="科幻" value="sci-fi" />
              <el-option label="奇幻" value="fantasy" />
              <el-option label="悬疑" value="mystery" />
              <el-option label="爱情" value="romance" />
            </el-select>
          </el-form-item>
        </el-form>
        <div class="story-result" v-if="storyResult">
          <h4>生成的故事</h4>
          <p>{{ storyResult }}</p>
        </div>
        <el-button type="primary" @click="generateStory">生成故事</el-button>
      </div>
    </el-dialog>
    
    <el-dialog
      v-model="showTravelDialog"
      title="旅游攻略"
      width="600px"
    >
      <div class="travel-content">
        <h3>分享旅行经验和攻略</h3>
        <el-form :model="travelForm" label-width="80px">
          <el-form-item label="目的地">
            <el-input v-model="travelForm.destination" placeholder="请输入目的地..." />
          </el-form-item>
          <el-form-item label="旅行天数">
            <el-input-number v-model="travelForm.days" :min="1" :max="30" />
          </el-form-item>
        </el-form>
        <div class="travel-result" v-if="travelResult">
          <h4>旅游攻略</h4>
          <p>{{ travelResult }}</p>
        </div>
        <el-button type="primary" @click="generateTravel">生成攻略</el-button>
      </div>
    </el-dialog>
    
    <el-dialog
      v-model="showFortuneDialog"
      title="命运分析"
      width="500px"
    >
      <div class="fortune-content">
        <h3>了解自己的命运走向</h3>
        <el-form :model="fortuneForm" label-width="80px">
          <el-form-item label="出生日期">
            <el-date-picker v-model="fortuneForm.birthDate" type="date" />
          </el-form-item>
          <el-form-item label="分析类型">
            <el-select v-model="fortuneForm.type" placeholder="选择分析类型">
              <el-option label="星座分析" value="zodiac" />
              <el-option label="八字分析" value="bazi" />
              <el-option label="塔罗分析" value="tarot" />
            </el-select>
          </el-form-item>
        </el-form>
        <div class="fortune-result" v-if="fortuneResult">
          <h4>命运分析结果</h4>
          <p>{{ fortuneResult }}</p>
        </div>
        <el-button type="primary" @click="analyzeFortune">开始分析</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 对话框状态
const showChatDialog = ref(false)
const showHeartLinkDialog = ref(false)
const showBuddyDialog = ref(false)
const showTarotDialog = ref(false)
const showStoryDialog = ref(false)
const showTravelDialog = ref(false)
const showFortuneDialog = ref(false)

// 活动标签页
const activeTab = ref('my')

// 聊天相关
const newMessage = ref('')
const chatMessages = ref([
  {
    id: 1,
    username: '张三',
    avatar: '',
    text: '大家好！',
    time: '14:30',
    isOwn: false
  },
  {
    id: 2,
    username: '李四',
    avatar: '',
    text: '欢迎新朋友！',
    time: '14:32',
    isOwn: false
  }
])

// 表单数据
const heartLinkForm = reactive({
  interests: [],
  personality: []
})

const tarotForm = reactive({
  question: '',
  type: ''
})

const storyForm = reactive({
  theme: '',
  type: ''
})

const travelForm = reactive({
  destination: '',
  days: 3
})

const fortuneForm = reactive({
  birthDate: '',
  type: ''
})

// 结果数据
const tarotResult = ref('')
const storyResult = ref('')
const travelResult = ref('')
const fortuneResult = ref('')

// 活动数据
const myActivities = ref([
  {
    id: 1,
    title: '周末爬山活动',
    description: '一起去爬香山，欣赏秋景',
    date: '2024-01-20',
    participants: 5
  }
])

const recommendedActivities = ref([
  {
    id: 1,
    title: '摄影爱好者聚会',
    description: '分享摄影技巧，交流作品',
    date: '2024-01-22',
    participants: 12
  },
  {
    id: 2,
    title: '读书分享会',
    description: '分享最近读的好书',
    date: '2024-01-25',
    participants: 8
  }
])

// 最近活动
const recentActivities = ref([
  {
    id: 1,
    username: '小明',
    avatar: '',
    content: '今天天气真好，适合出去走走',
    time: '2小时前',
    comments: 5,
    likes: 12
  },
  {
    id: 2,
    username: '小红',
    avatar: '',
    content: '推荐一本好书《百年孤独》',
    time: '4小时前',
    comments: 8,
    likes: 20
  }
])

// 发送消息
const sendMessage = () => {
  if (!newMessage.value.trim()) return
  
  const message = {
    id: Date.now(),
    username: '我',
    avatar: '',
    text: newMessage.value,
    time: new Date().toLocaleTimeString().slice(0, 5),
    isOwn: true
  }
  
  chatMessages.value.push(message)
  newMessage.value = ''
}

// 寻找心链
const findHeartLink = () => {
  if (heartLinkForm.interests.length === 0) {
    ElMessage.warning('请选择兴趣爱好')
    return
  }
  ElMessage.success('正在为您匹配心链伙伴...')
  showHeartLinkDialog.value = false
}

// 创建活动
const createActivity = () => {
  ElMessage.info('创建活动功能开发中...')
}

// 参与活动
const joinActivity = (activity: any) => {
  ElMessage.success(`已参与活动: ${activity.title}`)
}

// 开始占卜
const startTarot = () => {
  if (!tarotForm.question || !tarotForm.type) {
    ElMessage.warning('请填写问题并选择占卜类型')
    return
  }
  tarotResult.value = `根据您的问题"${tarotForm.question}"，${tarotForm.type}运势显示：您将迎来新的机遇，保持积极的心态，勇敢面对挑战。`
  ElMessage.success('占卜完成')
}

// 生成故事
const generateStory = () => {
  if (!storyForm.theme || !storyForm.type) {
    ElMessage.warning('请填写主题并选择故事类型')
    return
  }
  storyResult.value = `基于主题"${storyForm.theme}"的${storyForm.type}故事：在一个遥远的星球上，主人公踏上了寻找真相的旅程...`
  ElMessage.success('故事生成完成')
}

// 生成旅游攻略
const generateTravel = () => {
  if (!travelForm.destination) {
    ElMessage.warning('请输入目的地')
    return
  }
  travelResult.value = `${travelForm.destination}${travelForm.days}日游攻略：第一天游览主要景点，第二天体验当地文化，第三天购物休闲...`
  ElMessage.success('旅游攻略生成完成')
}

// 分析命运
const analyzeFortune = () => {
  if (!fortuneForm.birthDate || !fortuneForm.type) {
    ElMessage.warning('请选择出生日期和分析类型')
    return
  }
  fortuneResult.value = `根据您的出生日期和${fortuneForm.type}分析，您的性格特点包括：乐观开朗、富有创造力、善于交际...`
  ElMessage.success('命运分析完成')
}

onMounted(() => {
  // 初始化数据
})
</script>

<style scoped>
.social-page {
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

.features-section {
  margin-bottom: 40px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.feature-card {
  background: white;
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid #f0f0f0;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.feature-icon {
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

.feature-icon.chat {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.feature-icon.heart {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.feature-icon.buddy {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.feature-icon.tarot {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.feature-icon.story {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.feature-icon.travel {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.feature-icon.fortune {
  background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
}

.feature-card h3 {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.feature-card p {
  color: #606266;
  margin: 0;
  line-height: 1.5;
}

.activities-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.activities-section h2 {
  margin: 0 0 24px 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.activities-list {
  display: grid;
  gap: 16px;
}

.activity-item {
  display: flex;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
}

.activity-avatar {
  margin-right: 16px;
}

.activity-content {
  flex: 1;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.username {
  font-weight: 600;
  color: #303133;
}

.activity-time {
  color: #909399;
  font-size: 12px;
}

.activity-text {
  color: #606266;
  margin-bottom: 12px;
  line-height: 1.5;
}

.activity-actions {
  display: flex;
  gap: 16px;
}

.chat-container {
  height: 400px;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 16px;
}

.message-item {
  display: flex;
  margin-bottom: 16px;
}

.message-item.own-message {
  flex-direction: row-reverse;
}

.message-avatar {
  margin: 0 12px;
}

.message-content {
  max-width: 70%;
}

.message-header {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

.message-username {
  font-weight: 600;
  color: #303133;
  margin-right: 8px;
}

.message-time {
  color: #909399;
  font-size: 12px;
}

.message-text {
  background: white;
  padding: 8px 12px;
  border-radius: 8px;
  color: #303133;
}

.own-message .message-text {
  background: #409eff;
  color: white;
}

.chat-input {
  display: flex;
}

.heart-link-content,
.buddy-content,
.tarot-content,
.story-content,
.travel-content,
.fortune-content {
  text-align: center;
}

.heart-link-content h3,
.buddy-content h3,
.tarot-content h3,
.story-content h3,
.travel-content h3,
.fortune-content h3 {
  margin-bottom: 16px;
  color: #303133;
}

.activity-list {
  margin-top: 16px;
}

.activity-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  text-align: left;
}

.activity-card h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.activity-card p {
  margin: 0 0 8px 0;
  color: #606266;
}

.activity-meta {
  display: flex;
  justify-content: space-between;
  color: #909399;
  font-size: 12px;
}

.tarot-result,
.story-result,
.travel-result,
.fortune-result {
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
  text-align: left;
}

.tarot-result h4,
.story-result h4,
.travel-result h4,
.fortune-result h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.tarot-result p,
.story-result p,
.travel-result p,
.fortune-result p {
  margin: 0;
  color: #606266;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .social-page {
    padding: 16px;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .feature-card {
    padding: 24px 16px;
  }
  
  .message-content {
    max-width: 85%;
  }
}
</style>
