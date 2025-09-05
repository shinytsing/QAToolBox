<template>
  <div class="buddy-events-management">
    <div class="management-header">
      <h3>搭子活动管理</h3>
    </div>
    
    <el-table
      v-loading="loading"
      :data="buddyEvents"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user.username" label="创建者" width="120" />
      <el-table-column prop="title" label="活动标题" min-width="200" />
      <el-table-column prop="event_type" label="活动类型" width="120" />
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
const buddyEvents = ref<any[]>([])

const getStatusTag = (status: string) => {
  const tags: Record<string, string> = {
    active: 'success',
    inactive: 'info',
    pending: 'warning',
    cancelled: 'danger'
  }
  return tags[status] || 'default'
}

const getStatusName = (status: string) => {
  const names: Record<string, string> = {
    active: '进行中',
    inactive: '已结束',
    pending: '等待中',
    cancelled: '已取消'
  }
  return names[status] || '未知'
}

const loadBuddyEvents = async () => {
  loading.value = true
  try {
    // 模拟数据
    buddyEvents.value = [
      {
        id: 1,
        user: { username: 'user1' },
        title: '周末爬山活动',
        event_type: '户外运动',
        status: 'active',
        created_at: '2024-01-15 14:30:00'
      }
    ]
  } catch (error) {
    console.error('加载搭子活动数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleView = (buddyEvent: any) => {
  console.log('查看搭子活动:', buddyEvent)
}

const handleDelete = (buddyEvent: any) => {
  console.log('删除搭子活动:', buddyEvent)
}

onMounted(() => {
  loadBuddyEvents()
})
</script>

<style scoped>
.buddy-events-management {
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
