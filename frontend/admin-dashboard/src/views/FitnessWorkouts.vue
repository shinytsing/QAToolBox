<template>
  <div class="fitness-workouts">
    <div class="page-header">
      <h2>训练计划管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新增训练计划
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="计划名称">
          <el-input v-model="searchForm.name" placeholder="请输入计划名称" clearable />
        </el-form-item>
        <el-form-item label="难度等级">
          <el-select v-model="searchForm.difficulty" placeholder="选择难度" clearable>
            <el-option label="初级" value="beginner" />
            <el-option label="中级" value="intermediate" />
            <el-option label="高级" value="advanced" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="选择状态" clearable>
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
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
      <el-table :data="workouts" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="计划名称" min-width="150" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="difficulty" label="难度" width="100">
          <template #default="{ row }">
            <el-tag :type="getDifficultyType(row.difficulty)">
              {{ getDifficultyText(row.difficulty) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="时长(分钟)" width="120" />
        <el-table-column prop="calories" label="消耗卡路里" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="success" @click="handleView(row)">
              <el-icon><View /></el-icon>
              查看
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
      :title="editingWorkout ? '编辑训练计划' : '新增训练计划'"
      width="600px"
    >
      <el-form :model="workoutForm" :rules="workoutRules" ref="workoutFormRef" label-width="100px">
        <el-form-item label="计划名称" prop="name">
          <el-input v-model="workoutForm.name" placeholder="请输入计划名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="workoutForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入计划描述"
          />
        </el-form-item>
        <el-form-item label="难度等级" prop="difficulty">
          <el-select v-model="workoutForm.difficulty" placeholder="选择难度">
            <el-option label="初级" value="beginner" />
            <el-option label="中级" value="intermediate" />
            <el-option label="高级" value="advanced" />
          </el-select>
        </el-form-item>
        <el-form-item label="时长(分钟)" prop="duration">
          <el-input-number v-model="workoutForm.duration" :min="1" :max="300" />
        </el-form-item>
        <el-form-item label="消耗卡路里" prop="calories">
          <el-input-number v-model="workoutForm.calories" :min="0" :max="2000" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="workoutForm.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">
          {{ saving ? '保存中...' : '保存' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const editingWorkout = ref(null)
const workoutFormRef = ref<FormInstance>()

// 搜索表单
const searchForm = reactive({
  name: '',
  difficulty: '',
  status: ''
})

// 分页数据
const pagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

// 训练计划表单
const workoutForm = reactive({
  name: '',
  description: '',
  difficulty: 'beginner',
  duration: 30,
  calories: 200,
  status: 'active'
})

// 表单验证规则
const workoutRules: FormRules = {
  name: [
    { required: true, message: '请输入计划名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入计划描述', trigger: 'blur' }
  ],
  difficulty: [
    { required: true, message: '请选择难度等级', trigger: 'change' }
  ],
  duration: [
    { required: true, message: '请输入时长', trigger: 'blur' }
  ],
  calories: [
    { required: true, message: '请输入消耗卡路里', trigger: 'blur' }
  ]
}

// 模拟数据
const workouts = ref([
  {
    id: 1,
    name: 'HIIT高强度训练',
    description: '高强度间歇训练，快速燃脂',
    difficulty: 'advanced',
    duration: 30,
    calories: 400,
    status: 'active',
    created_at: '2025-09-06 10:00:00'
  },
  {
    id: 2,
    name: '瑜伽基础课程',
    description: '适合初学者的瑜伽基础动作',
    difficulty: 'beginner',
    duration: 45,
    calories: 150,
    status: 'active',
    created_at: '2025-09-06 09:30:00'
  },
  {
    id: 3,
    name: '力量训练计划',
    description: '全身肌肉力量训练',
    difficulty: 'intermediate',
    duration: 60,
    calories: 350,
    status: 'inactive',
    created_at: '2025-09-06 08:15:00'
  }
])

// 方法
const getDifficultyType = (difficulty: string) => {
  const typeMap = {
    beginner: 'success',
    intermediate: 'warning',
    advanced: 'danger'
  }
  return typeMap[difficulty] || 'info'
}

const getDifficultyText = (difficulty: string) => {
  const textMap = {
    beginner: '初级',
    intermediate: '中级',
    advanced: '高级'
  }
  return textMap[difficulty] || '未知'
}

const handleSearch = () => {
  // 实现搜索逻辑
  ElMessage.info('搜索功能开发中...')
}

const handleReset = () => {
  Object.assign(searchForm, {
    name: '',
    difficulty: '',
    status: ''
  })
  handleSearch()
}

const handleEdit = (row: any) => {
  editingWorkout.value = row
  Object.assign(workoutForm, row)
  showCreateDialog.value = true
}

const handleView = (row: any) => {
  ElMessage.info(`查看训练计划: ${row.name}`)
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除训练计划"${row.name}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    // 实现删除逻辑
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

const handleSave = async () => {
  if (!workoutFormRef.value) return
  
  try {
    const valid = await workoutFormRef.value.validate()
    if (!valid) return
    
    saving.value = true
    // 实现保存逻辑
    await new Promise(resolve => setTimeout(resolve, 1000)) // 模拟API调用
    ElMessage.success(editingWorkout.value ? '更新成功' : '创建成功')
    showCreateDialog.value = false
    resetForm()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  Object.assign(workoutForm, {
    name: '',
    description: '',
    difficulty: 'beginner',
    duration: 30,
    calories: 200,
    status: 'active'
  })
  editingWorkout.value = null
}

const handleSizeChange = (size: number) => {
  pagination.size = size
  // 重新加载数据
}

const handleCurrentChange = (current: number) => {
  pagination.current = current
  // 重新加载数据
}

onMounted(() => {
  // 初始化数据
  pagination.total = workouts.value.length
})
</script>

<style scoped>
.fitness-workouts {
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
</style>