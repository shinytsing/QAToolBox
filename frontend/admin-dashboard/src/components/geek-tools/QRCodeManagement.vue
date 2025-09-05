<template>
  <div class="qrcode-management">
    <div class="management-header">
      <h3>二维码生成管理</h3>
    </div>
    
    <el-table
      v-loading="loading"
      :data="qrcodes"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user.username" label="用户" width="120" />
      <el-table-column prop="content" label="内容" min-width="200" show-overflow-tooltip />
      <el-table-column prop="size" label="尺寸" width="100" />
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
const qrcodes = ref<any[]>([])

const loadQRCodes = async () => {
  loading.value = true
  try {
    // 模拟数据
    qrcodes.value = [
      {
        id: 1,
        user: { username: 'user1' },
        content: 'https://example.com',
        size: '200x200',
        created_at: '2024-01-15 14:30:00'
      }
    ]
  } catch (error) {
    console.error('加载二维码数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleView = (qrcode: any) => {
  console.log('查看二维码:', qrcode)
}

const handleDelete = (qrcode: any) => {
  console.log('删除二维码:', qrcode)
}

onMounted(() => {
  loadQRCodes()
})
</script>

<style scoped>
.qrcode-management {
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
