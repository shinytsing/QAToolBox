<template>
  <div class="diary-management">
    <div class="management-header">
      <h3>日记管理</h3>
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        添加日记
      </el-button>
    </div>
    
    <!-- 搜索筛选 -->
    <el-form :model="searchForm" inline class="search-form">
      <el-form-item label="用户">
        <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
      </el-form-item>
      <el-form-item label="日期">
        <el-date-picker
          v-model="searchForm.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
    
    <!-- 日记列表 -->
    <el-table
      v-loading="loading"
      :data="diaries"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user.username" label="用户" width="120" />
      <el-table-column prop="title" label="标题" min-width="200" />
      <el-table-column prop="content" label="内容" min-width="300" show-overflow-tooltip />
      <el-table-column prop="mood" label="心情" width="100">
        <template #default="{ row }">
          <el-tag :type="getMoodTag(row.mood)">
            {{ getMoodName(row.mood) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleView(row)">查看</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const showAddDialog = ref(false)

// 搜索表单
const searchForm = reactive({
  username: '',
  dateRange: [] as string[]
})

// 日记列表
const diaries = ref<any[]>([])

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 获取心情标签
const getMoodTag = (mood: string) => {
  const tags: Record<string, string> = {
    happy: 'success',
    sad: 'info',
    angry: 'danger',
    calm: 'warning',
    excited: 'primary'
  }
  return tags[mood] || 'default'
}

// 获取心情名称
const getMoodName = (mood: string) => {
  const names: Record<string, string> = {
    happy: '开心',
    sad: '难过',
    angry: '愤怒',
    calm: '平静',
    excited: '兴奋'
  }
  return names[mood] || '未知'
}

// 加载日记列表
const loadDiaries = async () => {
  loading.value = true
  try {
    // 这里应该调用API获取日记列表
    // 现在使用模拟数据
    diaries.value = [
      {
        id: 1,
        user: { username: 'user1' },
        title: '今天很开心',
        content: '今天天气很好，心情也很不错...',
        mood: 'happy',
        created_at: '2024-01-15 14:30:00'
      },
      {
        id: 2,
        user: { username: 'user2' },
        title: '工作压力大',
        content: '最近工作压力很大，需要调整心态...',
        mood: 'sad',
        created_at: '2024-01-15 16:20:00'
      }
    ]
    pagination.total = diaries.value.length
  } catch (error) {
    ElMessage.error('加载日记列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadDiaries()
}

// 重置搜索
const handleReset = () => {
  Object.assign(searchForm, {
    username: '',
    dateRange: []
  })
  handleSearch()
}

// 查看详情
const handleView = (diary: any) => {
  ElMessage.info(`查看日记: ${diary.title}`)
}

// 删除日记
const handleDelete = async (diary: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除日记 "${diary.title}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    
    const index = diaries.value.findIndex(d => d.id === diary.id)
    if (index > -1) {
      diaries.value.splice(index, 1)
      pagination.total--
    }
    ElMessage.success('删除成功')
  } catch (error) {
    // 用户取消
  }
}

// 分页处理
const handleSizeChange = (size: number) => {
  pagination.size = size
  loadDiaries()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadDiaries()
}

onMounted(() => {
  loadDiaries()
})
</script>

<style scoped>
.diary-management {
  padding: 0;
}

.management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.management-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.search-form {
  margin-bottom: 20px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
