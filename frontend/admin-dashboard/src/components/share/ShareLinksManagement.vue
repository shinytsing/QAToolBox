<template>
  <div class="share-links-management">
    <div class="management-header">
      <h3>分享链接管理</h3>
    </div>
    
    <el-table
      v-loading="loading"
      :data="shareLinks"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="user.username" label="用户" width="120" />
      <el-table-column prop="short_url" label="短链接" width="200" />
      <el-table-column prop="original_url" label="原始链接" min-width="300" show-overflow-tooltip />
      <el-table-column prop="click_count" label="点击次数" width="100" />
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
const shareLinks = ref<any[]>([])

const loadShareLinks = async () => {
  loading.value = true
  try {
    // 模拟数据
    shareLinks.value = [
      {
        id: 1,
        user: { username: 'user1' },
        short_url: 'https://short.ly/abc123',
        original_url: 'https://example.com/very/long/url',
        click_count: 42,
        created_at: '2024-01-15 14:30:00'
      }
    ]
  } catch (error) {
    console.error('加载分享链接数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleView = (link: any) => {
  console.log('查看分享链接:', link)
}

const handleDelete = (link: any) => {
  console.log('删除分享链接:', link)
}

onMounted(() => {
  loadShareLinks()
})
</script>

<style scoped>
.share-links-management {
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
