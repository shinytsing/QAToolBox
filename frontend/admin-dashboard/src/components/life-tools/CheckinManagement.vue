<template>
  <div class="checkin-management">
    <div class="management-header">
      <h3>签到管理</h3>
    </div>
    
    <el-table
      v-loading="loading"
      :data="checkins"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user.username" label="用户" width="120" />
      <el-table-column prop="checkin_type" label="签到类型" width="120" />
      <el-table-column prop="streak_days" label="连续天数" width="120" />
      <el-table-column prop="created_at" label="签到时间" width="180" />
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
const checkins = ref<any[]>([])

const loadCheckins = async () => {
  loading.value = true
  try {
    // 模拟数据
    checkins.value = [
      {
        id: 1,
        user: { username: 'user1' },
        checkin_type: '每日签到',
        streak_days: 7,
        created_at: '2024-01-15 14:30:00'
      }
    ]
  } catch (error) {
    console.error('加载签到数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleView = (checkin: any) => {
  console.log('查看签到:', checkin)
}

const handleDelete = (checkin: any) => {
  console.log('删除签到:', checkin)
}

onMounted(() => {
  loadCheckins()
})
</script>

<style scoped>
.checkin-management {
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
