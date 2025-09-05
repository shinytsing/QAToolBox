<template>
  <div class="heart-link-management">
    <div class="management-header">
      <h3>心链管理</h3>
    </div>
    
    <el-table
      v-loading="loading"
      :data="heartLinks"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user1.username" label="用户1" width="120" />
      <el-table-column prop="user2.username" label="用户2" width="120" />
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
const heartLinks = ref<any[]>([])

const getStatusTag = (status: string) => {
  const tags: Record<string, string> = {
    active: 'success',
    inactive: 'info',
    pending: 'warning'
  }
  return tags[status] || 'default'
}

const getStatusName = (status: string) => {
  const names: Record<string, string> = {
    active: '活跃',
    inactive: '非活跃',
    pending: '等待中'
  }
  return names[status] || '未知'
}

const loadHeartLinks = async () => {
  loading.value = true
  try {
    // 模拟数据
    heartLinks.value = [
      {
        id: 1,
        user1: { username: 'user1' },
        user2: { username: 'user2' },
        status: 'active',
        created_at: '2024-01-15 14:30:00'
      }
    ]
  } catch (error) {
    console.error('加载心链数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleView = (heartLink: any) => {
  console.log('查看心链:', heartLink)
}

const handleDelete = (heartLink: any) => {
  console.log('删除心链:', heartLink)
}

onMounted(() => {
  loadHeartLinks()
})
</script>

<style scoped>
.heart-link-management {
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
