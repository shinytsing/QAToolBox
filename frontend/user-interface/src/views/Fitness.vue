<template>
  <div class="fitness-page">
    <div class="page-header">
      <h1>健身管理</h1>
      <el-button type="primary" @click="showAddWorkout = true">
        <el-icon><Plus /></el-icon>
        添加训练
      </el-button>
    </div>
    
    <!-- 健身统计 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon">
              <el-icon><Trophy /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ fitnessStats.totalWorkouts }}</div>
              <div class="stat-label">总训练次数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon">
              <el-icon><Timer /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ fitnessStats.totalDuration }}</div>
              <div class="stat-label">总训练时长(分钟)</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon">
              <el-icon><Medal /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ fitnessStats.achievements }}</div>
              <div class="stat-label">获得成就</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ fitnessStats.streakDays }}</div>
              <div class="stat-label">连续天数</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
    
    <!-- 训练记录 -->
    <div class="workouts-section">
      <div class="section-header">
        <h2>训练记录</h2>
        <el-button type="text" @click="refreshWorkouts">刷新</el-button>
      </div>
      
      <div class="workouts-list">
        <div 
          v-for="workout in workouts" 
          :key="workout.id"
          class="workout-card"
        >
          <div class="workout-header">
            <div class="workout-type">
              <el-icon><component :is="getWorkoutIcon(workout.type)" /></el-icon>
              <span>{{ getWorkoutTypeName(workout.type) }}</span>
            </div>
            <div class="workout-date">{{ workout.date }}</div>
          </div>
          
          <div class="workout-content">
            <div class="workout-duration">
              <span class="duration-label">时长</span>
              <span class="duration-value">{{ workout.duration }} 分钟</span>
            </div>
            <div class="workout-calories">
              <span class="calories-label">消耗</span>
              <span class="calories-value">{{ workout.calories }} 卡路里</span>
            </div>
          </div>
          
          <div class="workout-notes" v-if="workout.notes">
            <p>{{ workout.notes }}</p>
          </div>
          
          <div class="workout-actions">
            <el-button size="small" @click="editWorkout(workout)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteWorkout(workout)">删除</el-button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加训练对话框 -->
    <el-dialog
      v-model="showAddWorkout"
      title="添加训练记录"
      width="500px"
    >
      <el-form :model="workoutForm" label-width="80px">
        <el-form-item label="训练类型">
          <el-select v-model="workoutForm.type" placeholder="请选择训练类型">
            <el-option label="有氧运动" value="cardio" />
            <el-option label="力量训练" value="strength" />
            <el-option label="柔韧性训练" value="flexibility" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="训练时长">
          <el-input-number v-model="workoutForm.duration" :min="1" :max="300" />
        </el-form-item>
        <el-form-item label="消耗卡路里">
          <el-input-number v-model="workoutForm.calories" :min="0" :max="2000" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="workoutForm.notes" type="textarea" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddWorkout = false">取消</el-button>
        <el-button type="primary" @click="addWorkout">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const showAddWorkout = ref(false)

// 健身统计数据
const fitnessStats = reactive({
  totalWorkouts: 0,
  totalDuration: 0,
  achievements: 0,
  streakDays: 0
})

// 训练记录
const workouts = ref([
  {
    id: 1,
    type: 'cardio',
    duration: 30,
    calories: 300,
    notes: '跑步训练',
    date: '2024-01-15'
  },
  {
    id: 2,
    type: 'strength',
    duration: 45,
    calories: 450,
    notes: '举重训练',
    date: '2024-01-14'
  }
])

// 训练表单
const workoutForm = reactive({
  type: '',
  duration: 30,
  calories: 0,
  notes: ''
})

// 获取训练图标
const getWorkoutIcon = (type: string) => {
  const icons: Record<string, string> = {
    cardio: 'Running',
    strength: 'Medal',
    flexibility: 'Sunny',
    other: 'Tools'
  }
  return icons[type] || 'Tools'
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
  try {
    // 这里应该调用API获取健身数据
    fitnessStats.totalWorkouts = 25
    fitnessStats.totalDuration = 1200
    fitnessStats.achievements = 8
    fitnessStats.streakDays = 7
  } catch (error) {
    console.error('加载健身数据失败:', error)
  }
}

// 刷新训练记录
const refreshWorkouts = () => {
  console.log('刷新训练记录')
}

// 编辑训练
const editWorkout = (workout: any) => {
  console.log('编辑训练:', workout)
}

// 删除训练
const deleteWorkout = async (workout: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这条训练记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const index = workouts.value.findIndex(w => w.id === workout.id)
    if (index > -1) {
      workouts.value.splice(index, 1)
    }
    ElMessage.success('删除成功')
  } catch (error) {
    // 用户取消
  }
}

// 添加训练
const addWorkout = () => {
  const newWorkout = {
    id: Date.now(),
    ...workoutForm,
    date: new Date().toISOString().split('T')[0]
  }
  workouts.value.unshift(newWorkout)
  showAddWorkout.value = false
  ElMessage.success('添加成功')
  
  // 重置表单
  Object.assign(workoutForm, {
    type: '',
    duration: 30,
    calories: 0,
    notes: ''
  })
}

onMounted(() => {
  loadFitnessData()
})
</script>

<style scoped>
.fitness-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.stats-section {
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  color: white;
  font-size: 24px;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.workouts-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.workouts-list {
  display: grid;
  gap: 16px;
}

.workout-card {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
}

.workout-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.workout-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.workout-type {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #303133;
}

.workout-type .el-icon {
  margin-right: 8px;
  color: #409eff;
}

.workout-date {
  color: #909399;
  font-size: 14px;
}

.workout-content {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
}

.workout-duration,
.workout-calories {
  display: flex;
  flex-direction: column;
}

.duration-label,
.calories-label {
  color: #909399;
  font-size: 12px;
  margin-bottom: 4px;
}

.duration-value,
.calories-value {
  color: #303133;
  font-weight: 600;
}

.workout-notes {
  margin-bottom: 16px;
}

.workout-notes p {
  color: #606266;
  margin: 0;
  font-size: 14px;
}

.workout-actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 768px) {
  .fitness-page {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-icon {
    width: 48px;
    height: 48px;
    font-size: 20px;
  }
  
  .stat-number {
    font-size: 24px;
  }
  
  .workout-content {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
