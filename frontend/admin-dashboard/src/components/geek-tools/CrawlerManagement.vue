<template>
  <div class="crawler-management">
    <div class="management-header">
      <h3>网页爬虫管理</h3>
    </div>
    
    <el-table
      v-loading="loading"
      :data="crawlers"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user.username" label="用户" width="120" />
      <el-table-column prop="url" label="目标URL" min-width="200" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusTag(row.status)">
            {{ getStatusName(row.status) }}
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const loading = ref(false)
const crawlers = ref<any[]>([])

const getStatusTag = (status: string) => {
  const tags: Record<string, string> = {
    pending: 'warning',
    running: 'primary',
    completed: 'success',
    failed: 'danger'
  }
  return tags[status] || 'default'
}

const getStatusName = (status: string) => {
  const names: Record<string, string> = {
    pending: '等待中',
    running: '运行中',
    completed: '已完成',
    failed: '失败'
  }
  return names[status] || '未知'
}

const loadCrawlers = async () => {
  loading.value = true
  try {
    // 模拟数据
    crawlers.value = [
      {
        id: 1,
        user: { username: 'user1' },
        url: 'https://example.com',
        status: 'completed',
        created_at: '2024-01-15 14:30:00'
      }
    ]
  } catch (error) {
    console.error('加载爬虫数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleView = (crawler: any) => {
  console.log('查看爬虫:', crawler)
}

const handleDelete = (crawler: any) => {
  console.log('删除爬虫:', crawler)
}

onMounted(() => {
  loadCrawlers()
})
</script>

<style scoped>
.crawler-management {
  padding: 0;
}

.management-header {
  margin-bottom: 20px;
}

.management-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}
</style>
