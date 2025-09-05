<template>
  <div class="travel-management">
    <div class="management-header">
      <h3>旅游攻略管理</h3>
    </div>
    
    <el-table
      v-loading="loading"
      :data="travels"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user.username" label="用户" width="120" />
      <el-table-column prop="destination" label="目的地" width="150" />
      <el-table-column prop="duration" label="行程天数" width="100" />
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
const travels = ref<any[]>([])

const loadTravels = async () => {
  loading.value = true
  try {
    // 模拟数据
    travels.value = [
      {
        id: 1,
        user: { username: 'user1' },
        destination: '北京',
        duration: 3,
        created_at: '2024-01-15 14:30:00'
      }
    ]
  } catch (error) {
    console.error('加载旅游攻略数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleView = (travel: any) => {
  console.log('查看旅游攻略:', travel)
}

const handleDelete = (travel: any) => {
  console.log('删除旅游攻略:', travel)
}

onMounted(() => {
  loadTravels()
})
</script>

<style scoped>
.travel-management {
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
