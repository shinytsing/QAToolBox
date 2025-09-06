<template>
  <div class="fitness-posts">
    <div class="page-header">
      <h2>健身社区管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        发布新内容
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="内容标题">
          <el-input v-model="searchForm.title" placeholder="请输入标题" clearable />
        </el-form-item>
        <el-form-item label="作者">
          <el-input v-model="searchForm.author" placeholder="请输入作者" clearable />
        </el-form-item>
        <el-form-item label="内容类型">
          <el-select v-model="searchForm.type" placeholder="选择类型" clearable>
            <el-option label="训练分享" value="workout" />
            <el-option label="饮食建议" value="diet" />
            <el-option label="经验心得" value="experience" />
            <el-option label="问题求助" value="question" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="选择状态" clearable>
            <el-option label="已发布" value="published" />
            <el-option label="草稿" value="draft" />
            <el-option label="已删除" value="deleted" />
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
      <el-table :data="posts" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="author" label="作者" width="120" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.type)">
              {{ getTypeText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="likes" label="点赞数" width="100" />
        <el-table-column prop="comments" label="评论数" width="100" />
        <el-table-column prop="views" label="浏览数" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="发布时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleView(row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button 
              size="small" 
              :type="row.status === 'published' ? 'warning' : 'success'"
              @click="handleToggleStatus(row)"
            >
              <el-icon><Switch /></el-icon>
              {{ row.status === 'published' ? '下架' : '发布' }}
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
      :title="editingPost ? '编辑内容' : '发布新内容'"
      width="800px"
    >
      <el-form :model="postForm" :rules="postRules" ref="postFormRef" label-width="100px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="postForm.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="内容类型" prop="type">
          <el-select v-model="postForm.type" placeholder="选择类型">
            <el-option label="训练分享" value="workout" />
            <el-option label="饮食建议" value="diet" />
            <el-option label="经验心得" value="experience" />
            <el-option label="问题求助" value="question" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="postForm.content"
            type="textarea"
            :rows="8"
            placeholder="请输入内容"
          />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="postForm.tags" placeholder="请输入标签，用逗号分隔" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="postForm.status">
            <el-radio label="draft">草稿</el-radio>
            <el-radio label="published">发布</el-radio>
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

    <!-- 查看详情对话框 -->
    <el-dialog v-model="showViewDialog" title="内容详情" width="800px">
      <div v-if="viewingPost" class="post-detail">
        <h3>{{ viewingPost.title }}</h3>
        <div class="post-meta">
          <el-tag :type="getTypeColor(viewingPost.type)">{{ getTypeText(viewingPost.type) }}</el-tag>
          <span>作者: {{ viewingPost.author }}</span>
          <span>发布时间: {{ viewingPost.created_at }}</span>
        </div>
        <div class="post-stats">
          <el-tag type="info">点赞: {{ viewingPost.likes }}</el-tag>
          <el-tag type="info">评论: {{ viewingPost.comments }}</el-tag>
          <el-tag type="info">浏览: {{ viewingPost.views }}</el-tag>
        </div>
        <div class="post-content">
          {{ viewingPost.content }}
        </div>
      </div>
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
const showViewDialog = ref(false)
const editingPost = ref(null)
const viewingPost = ref(null)
const postFormRef = ref<FormInstance>()

// 搜索表单
const searchForm = reactive({
  title: '',
  author: '',
  type: '',
  status: ''
})

// 分页数据
const pagination = reactive({
  current: 1,
  size: 10,
  total: 0
})

// 内容表单
const postForm = reactive({
  title: '',
  type: 'workout',
  content: '',
  tags: '',
  status: 'draft'
})

// 表单验证规则
const postRules: FormRules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择内容类型', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入内容', trigger: 'blur' }
  ]
}

// 模拟数据
const posts = ref([
  {
    id: 1,
    title: '我的HIIT训练心得分享',
    author: '健身达人',
    type: 'workout',
    content: '经过3个月的HIIT训练，我的体脂率从25%降到了18%，体重减少了8kg...',
    likes: 156,
    comments: 23,
    views: 1200,
    status: 'published',
    created_at: '2025-09-06 10:00:00'
  },
  {
    id: 2,
    title: '减脂期饮食搭配建议',
    author: '营养师小王',
    type: 'diet',
    content: '减脂期的饮食搭配非常重要，需要控制热量摄入的同时保证营养均衡...',
    likes: 89,
    comments: 15,
    views: 800,
    status: 'published',
    created_at: '2025-09-06 09:30:00'
  },
  {
    id: 3,
    title: '新手如何开始力量训练？',
    author: '健身教练',
    type: 'question',
    content: '作为健身新手，想要开始力量训练但不知道从何开始，求指导...',
    likes: 45,
    comments: 8,
    views: 300,
    status: 'draft',
    created_at: '2025-09-06 08:15:00'
  }
])

// 方法
const getTypeColor = (type: string) => {
  const colorMap = {
    workout: 'success',
    diet: 'warning',
    experience: 'info',
    question: 'danger'
  }
  return colorMap[type] || 'info'
}

const getTypeText = (type: string) => {
  const textMap = {
    workout: '训练分享',
    diet: '饮食建议',
    experience: '经验心得',
    question: '问题求助'
  }
  return textMap[type] || '未知'
}

const getStatusColor = (status: string) => {
  const colorMap = {
    published: 'success',
    draft: 'warning',
    deleted: 'danger'
  }
  return colorMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const textMap = {
    published: '已发布',
    draft: '草稿',
    deleted: '已删除'
  }
  return textMap[status] || '未知'
}

const handleSearch = () => {
  ElMessage.info('搜索功能开发中...')
}

const handleReset = () => {
  Object.assign(searchForm, {
    title: '',
    author: '',
    type: '',
    status: ''
  })
  handleSearch()
}

const handleView = (row: any) => {
  viewingPost.value = row
  showViewDialog.value = true
}

const handleEdit = (row: any) => {
  editingPost.value = row
  Object.assign(postForm, {
    title: row.title,
    type: row.type,
    content: row.content,
    tags: row.tags || '',
    status: row.status
  })
  showCreateDialog.value = true
}

const handleToggleStatus = async (row: any) => {
  const newStatus = row.status === 'published' ? 'draft' : 'published'
  const action = newStatus === 'published' ? '发布' : '下架'
  
  try {
    await ElMessageBox.confirm(`确定要${action}这条内容吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    row.status = newStatus
    ElMessage.success(`${action}成功`)
  } catch {
    // 用户取消
  }
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除这条内容吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    row.status = 'deleted'
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

const handleSave = async () => {
  if (!postFormRef.value) return
  
  try {
    const valid = await postFormRef.value.validate()
    if (!valid) return
    
    saving.value = true
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success(editingPost.value ? '更新成功' : '发布成功')
    showCreateDialog.value = false
    resetForm()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  Object.assign(postForm, {
    title: '',
    type: 'workout',
    content: '',
    tags: '',
    status: 'draft'
  })
  editingPost.value = null
}

const handleSizeChange = (size: number) => {
  pagination.size = size
}

const handleCurrentChange = (current: number) => {
  pagination.current = current
}

onMounted(() => {
  pagination.total = posts.value.length
})
</script>

<style scoped>
.fitness-posts {
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

.post-detail h3 {
  margin-bottom: 15px;
  color: #333;
}

.post-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
  color: #666;
  font-size: 14px;
}

.post-stats {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.post-content {
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
}
</style>
