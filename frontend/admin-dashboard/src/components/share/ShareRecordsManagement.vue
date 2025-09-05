<template>
  <div class="share-records-management">
    <div class="management-header">
      <h3>分享记录管理</h3>
    </div>
    
    <el-table
      v-loading="loading"
      :data="shareRecords"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user.username" label="用户" width="120" />
      <el-table-column prop="content_type" label="内容类型" width="120" />
      <el-table-column prop="content_id" label="内容ID" width="100" />
      <el-table-column prop="platform" label="分享平台" width="120" />
      <el-table-column prop="created_at" label="分享时间" width="180" />
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
const shareRecords = ref<any[]>([])

const loadShareRecords = async () => {
  loading.value = true
  try {
    // 模拟数据
    shareRecords.value = [
      {
        id: 1,
        user: { username: 'user1' },
        content_type: 'PDF转换',
        content_id: 123,
        platform: '微信',
        created_at: '2024-01-15 14:30:00'
      }
    ]
  } catch (error) {
    console.error('加载分享记录数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleView = (record: any) => {
  console.log('查看分享记录:', record)
}

const handleDelete = (record: any) => {
  console.log('删除分享记录:', record)
}

onMounted(() => {
  loadShareRecords()
})
</script>

<style scoped>
.share-records-management {
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
