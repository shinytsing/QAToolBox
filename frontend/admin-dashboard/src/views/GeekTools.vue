<template>
  <div class="geek-tools-page">
    <div class="page-header">
      <h1>极客工具管理</h1>
    </div>
    
    <!-- 工具统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon pdf">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ toolStats.pdfCount }}</div>
              <div class="stat-label">PDF转换</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon crawler">
              <el-icon><Link /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ toolStats.crawlerCount }}</div>
              <div class="stat-label">爬虫任务</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon testcase">
              <el-icon><DocumentChecked /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ toolStats.testcaseCount }}</div>
              <div class="stat-label">测试用例</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon qrcode">
              <el-icon><Grid /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ toolStats.qrcodeCount }}</div>
              <div class="stat-label">二维码生成</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 工具列表 -->
    <el-card class="tools-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="PDF转换" name="pdf">
          <pdf-management />
        </el-tab-pane>
        <el-tab-pane label="网页爬虫" name="crawler">
          <crawler-management />
        </el-tab-pane>
        <el-tab-pane label="测试用例" name="testcase">
          <testcase-management />
        </el-tab-pane>
        <el-tab-pane label="代码格式化" name="formatter">
          <formatter-management />
        </el-tab-pane>
        <el-tab-pane label="二维码生成" name="qrcode">
          <qrcode-management />
        </el-tab-pane>
        <el-tab-pane label="哈希生成" name="hash">
          <hash-management />
        </el-tab-pane>
        <el-tab-pane label="Base64编码" name="base64">
          <base64-management />
        </el-tab-pane>
        <el-tab-pane label="数据分析" name="analysis">
          <analysis-management />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import PDFManagement from '@/components/geek-tools/PDFManagement.vue'
import CrawlerManagement from '@/components/geek-tools/CrawlerManagement.vue'
import TestcaseManagement from '@/components/geek-tools/TestcaseManagement.vue'
import FormatterManagement from '@/components/geek-tools/FormatterManagement.vue'
import QRCodeManagement from '@/components/geek-tools/QRCodeManagement.vue'
import HashManagement from '@/components/geek-tools/HashManagement.vue'
import Base64Management from '@/components/geek-tools/Base64Management.vue'
import AnalysisManagement from '@/components/geek-tools/AnalysisManagement.vue'

const activeTab = ref('pdf')

// 工具统计数据
const toolStats = reactive({
  pdfCount: 0,
  crawlerCount: 0,
  testcaseCount: 0,
  qrcodeCount: 0
})

// 切换标签页
const handleTabChange = (tab: string) => {
  console.log('切换到标签页:', tab)
}

// 加载统计数据
const loadStats = async () => {
  try {
    // 这里应该调用API获取统计数据
    toolStats.pdfCount = 1234
    toolStats.crawlerCount = 567
    toolStats.testcaseCount = 890
    toolStats.qrcodeCount = 345
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.geek-tools-page {
  padding: 0;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: white;
}

.stat-icon.pdf {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.crawler {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.testcase {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.qrcode {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.tools-card {
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>
