<template>
  <div class="fitness-profile">
    <div class="page-header">
      <h2>用户档案管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新增档案
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="searchForm.gender" placeholder="选择性别" clearable>
            <el-option label="男" value="male" />
            <el-option label="女" value="female" />
          </el-select>
        </el-form-item>
        <el-form-item label="健身目标">
          <el-select v-model="searchForm.goal" placeholder="选择目标" clearable>
            <el-option label="减脂" value="weight_loss" />
            <el-option label="增肌" value="muscle_gain" />
            <el-option label="塑形" value="body_shaping" />
            <el-option label="健康" value="health" />
          </el-select>
        </el-form-item>
        <el-form-item label="等级">
          <el-select v-model="searchForm.level" placeholder="选择等级" clearable>
            <el-option label="新手" value="beginner" />
            <el-option label="中级" value="intermediate" />
            <el-option label="高级" value="advanced" />
            <el-option label="专业" value="expert" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <el-table :data="profiles" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="nickname" label="昵称" width="120" />
        <el-table-column prop="gender" label="性别" width="80">
          <template #default="{ row }">
            <el-tag :type="row.gender === 'male' ? 'primary' : 'danger'">
              {{ row.gender === 'male' ? '男' : '女' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="80" />
        <el-table-column prop="height" label="身高(cm)" width="100" />
        <el-table-column prop="weight" label="体重(kg)" width="100" />
        <el-table-column prop="bmi" label="BMI" width="80">
          <template #default="{ row }">
            <el-tag :type="getBMIType(row.bmi)">
              {{ row.bmi }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="goal" label="健身目标" width="120">
          <template #default="{ row }">
            <el-tag :type="getGoalColor(row.goal)">
              {{ getGoalText(row.goal) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelColor(row.level)">
              {{ getLevelText(row.level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleView(row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.current"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingProfile ? '编辑档案' : '新增档案'"
      width="600px"
    >
      <el-form :model="profileForm" :rules="profileRules" ref="profileFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="profileForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="profileForm.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="profileForm.gender">
            <el-radio label="male">男</el-radio>
            <el-radio label="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="年龄" prop="age">
          <el-input-number v-model="profileForm.age" :min="1" :max="120" />
        </el-form-item>
        <el-form-item label="身高(cm)" prop="height">
          <el-input-number v-model="profileForm.height" :min="100" :max="250" />
        </el-form-item>
        <el-form-item label="体重(kg)" prop="weight">
          <el-input-number v-model="profileForm.weight" :min="20" :max="200" />
        </el-form-item>
        <el-form-item label="健身目标" prop="goal">
          <el-select v-model="profileForm.goal" placeholder="选择目标">
            <el-option label="减脂" value="weight_loss" />
            <el-option label="增肌" value="muscle_gain" />
            <el-option label="塑形" value="body_shaping" />
            <el-option label="健康" value="health" />
          </el-select>
        </el-form-item>
        <el-form-item label="等级" prop="level">
          <el-select v-model="profileForm.level" placeholder="选择等级">
            <el-option label="新手" value="beginner" />
            <el-option label="中级" value="intermediate" />
            <el-option label="高级" value="advanced" />
            <el-option label="专业" value="expert" />
          </el-select>
        </el-form-item>
        <el-form-item label="个人简介">
          <el-input
            v-model="profileForm.bio"
            type="textarea"
            :rows="3"
            placeholder="请输入个人简介"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">
          {{ saving ? '保存中...' : '保存' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog v-model="showViewDialog" title="档案详情" width="600px">
      <div v-if="viewingProfile" class="profile-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户名">{{ viewingProfile.username }}</el-descriptions-item>
          <el-descriptions-item label="昵称">{{ viewingProfile.nickname }}</el-descriptions-item>
          <el-descriptions-item label="性别">
            <el-tag :type="viewingProfile.gender === 'male' ? 'primary' : 'danger'">
              {{ viewingProfile.gender === 'male' ? '男' : '女' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="年龄">{{ viewingProfile.age }}岁</el-descriptions-item>
          <el-descriptions-item label="身高">{{ viewingProfile.height }}cm</el-descriptions-item>
          <el-descriptions-item label="体重">{{ viewingProfile.weight }}kg</el-descriptions-item>
          <el-descriptions-item label="BMI">
            <el-tag :type="getBMIType(viewingProfile.bmi)">{{ viewingProfile.bmi }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="健身目标">
            <el-tag :type="getGoalColor(viewingProfile.goal)">
              {{ getGoalText(viewingProfile.goal) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="等级">
            <el-tag :type="getLevelColor(viewingProfile.level)">
              {{ getLevelText(viewingProfile.level) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="注册时间" :span="2">{{ viewingProfile.created_at }}</el-descriptions-item>
          <el-descriptions-item label="个人简介" :span="2">{{ viewingProfile.bio || '暂无' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const showViewDialog = ref(false)
const editingProfile = ref(null)
const viewingProfile = ref(null)
const profileFormRef = ref<FormInstance>()

// 搜索表单
const searchForm = reactive({
  username: '',
  gender: '',
  goal: '',
  level: ''
})

// 分页数据
const pagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

// 档案表单
const profileForm = reactive({
  username: '',
  nickname: '',
  gender: 'male',
  age: 25,
  height: 170,
  weight: 65,
  goal: 'health',
  level: 'beginner',
  bio: ''
})

// 表单验证规则
const profileRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  age: [
    { required: true, message: '请输入年龄', trigger: 'blur' }
  ],
  height: [
    { required: true, message: '请输入身高', trigger: 'blur' }
  ],
  weight: [
    { required: true, message: '请输入体重', trigger: 'blur' }
  ],
  goal: [
    { required: true, message: '请选择健身目标', trigger: 'change' }
  ],
  level: [
    { required: true, message: '请选择等级', trigger: 'change' }
  ]
}

// 模拟数据
const profiles = ref([
  {
    id: 1,
    username: 'fitness_lover',
    nickname: '健身爱好者',
    gender: 'male',
    age: 28,
    height: 175,
    weight: 70,
    bmi: 22.9,
    goal: 'muscle_gain',
    level: 'intermediate',
    bio: '热爱健身，追求健康生活',
    created_at: '2025-09-01 10:00:00'
  },
  {
    id: 2,
    username: 'yoga_girl',
    nickname: '瑜伽女孩',
    gender: 'female',
    age: 25,
    height: 165,
    weight: 55,
    bmi: 20.2,
    goal: 'body_shaping',
    level: 'advanced',
    bio: '瑜伽教练，专注身心平衡',
    created_at: '2025-09-02 14:30:00'
  },
  {
    id: 3,
    username: 'newbie_fit',
    nickname: '健身新手',
    gender: 'male',
    age: 22,
    height: 180,
    weight: 80,
    bmi: 24.7,
    goal: 'weight_loss',
    level: 'beginner',
    bio: '刚开始健身，希望减脂塑形',
    created_at: '2025-09-03 09:15:00'
  }
])

// 计算BMI
const calculateBMI = (height: number, weight: number) => {
  const heightInM = height / 100
  return (weight / (heightInM * heightInM)).toFixed(1)
}

// 方法
const getBMIType = (bmi: number) => {
  if (bmi < 18.5) return 'info'
  if (bmi < 24) return 'success'
  if (bmi < 28) return 'warning'
  return 'danger'
}

const getGoalColor = (goal: string) => {
  const colorMap = {
    weight_loss: 'success',
    muscle_gain: 'primary',
    body_shaping: 'warning',
    health: 'info'
  }
  return colorMap[goal] || 'info'
}

const getGoalText = (goal: string) => {
  const textMap = {
    weight_loss: '减脂',
    muscle_gain: '增肌',
    body_shaping: '塑形',
    health: '健康'
  }
  return textMap[goal] || '未知'
}

const getLevelColor = (level: string) => {
  const colorMap = {
    beginner: 'info',
    intermediate: 'success',
    advanced: 'warning',
    expert: 'danger'
  }
  return colorMap[level] || 'info'
}

const getLevelText = (level: string) => {
  const textMap = {
    beginner: '新手',
    intermediate: '中级',
    advanced: '高级',
    expert: '专业'
  }
  return textMap[level] || '未知'
}

const handleSearch = () => {
  ElMessage.info('搜索功能开发中...')
}

const handleReset = () => {
  Object.assign(searchForm, {
    username: '',
    gender: '',
    goal: '',
    level: ''
  })
  handleSearch()
}

const handleView = (row: any) => {
  viewingProfile.value = row
  showViewDialog.value = true
}

const handleEdit = (row: any) => {
  editingProfile.value = row
  Object.assign(profileForm, {
    username: row.username,
    nickname: row.nickname,
    gender: row.gender,
    age: row.age,
    height: row.height,
    weight: row.weight,
    goal: row.goal,
    level: row.level,
    bio: row.bio || ''
  })
  showCreateDialog.value = true
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户"${row.username}"的档案吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

const handleSave = async () => {
  if (!profileFormRef.value) return
  
  try {
    const valid = await profileFormRef.value.validate()
    if (!valid) return
    
    saving.value = true
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success(editingProfile.value ? '更新成功' : '创建成功')
    showCreateDialog.value = false
    resetForm()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  Object.assign(profileForm, {
    username: '',
    nickname: '',
    gender: 'male',
    age: 25,
    height: 170,
    weight: 65,
    goal: 'health',
    level: 'beginner',
    bio: ''
  })
  editingProfile.value = null
}

const handleSizeChange = (size: number) => {
  pagination.size = size
}

const handleCurrentChange = (current: number) => {
  pagination.current = current
}

onMounted(() => {
  pagination.total = profiles.value.length
})
</script>

<style scoped>
.fitness-profile {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.profile-detail {
  padding: 20px 0;
}
</style>
