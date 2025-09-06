<template>
  <div class="geek-page">
    <div class="page-header">
      <h1>极客工具</h1>
      <p>提升效率，让技术更简单</p>
    </div>
    
    <!-- 工具分类 -->
    <div class="tools-section">
      <div class="tools-grid">
        <div class="tool-card" @click="showPDFDialog = true">
          <div class="tool-icon pdf">
            <el-icon><Document /></el-icon>
          </div>
          <h3>PDF转换</h3>
          <p>支持多种格式互转</p>
        </div>
        
        <div class="tool-card" @click="showCrawlerDialog = true">
          <div class="tool-icon crawler">
            <el-icon><Link /></el-icon>
          </div>
          <h3>网页爬虫</h3>
          <p>快速抓取网页数据</p>
        </div>
        
        <div class="tool-card" @click="showTestcaseDialog = true">
          <div class="tool-icon testcase">
            <el-icon><DocumentChecked /></el-icon>
          </div>
          <h3>测试用例生成</h3>
          <p>自动生成测试用例</p>
        </div>
        
        <div class="tool-card" @click="showFormatterDialog = true">
          <div class="tool-icon formatter">
            <el-icon><Tools /></el-icon>
          </div>
          <h3>代码格式化</h3>
          <p>美化代码格式</p>
        </div>
        
        <div class="tool-card" @click="showQRCodeDialog = true">
          <div class="tool-icon qrcode">
            <el-icon><Grid /></el-icon>
          </div>
          <h3>二维码生成</h3>
          <p>快速生成二维码</p>
        </div>
        
        <div class="tool-card" @click="showHashDialog = true">
          <div class="tool-icon hash">
            <el-icon><Lock /></el-icon>
          </div>
          <h3>哈希生成</h3>
          <p>多种哈希算法</p>
        </div>
        
        <div class="tool-card" @click="showBase64Dialog = true">
          <div class="tool-icon base64">
            <el-icon><Key /></el-icon>
          </div>
          <h3>Base64编码</h3>
          <p>编码解码工具</p>
        </div>
        
        <div class="tool-card" @click="showAnalysisDialog = true">
          <div class="tool-icon analysis">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <h3>数据分析</h3>
          <p>数据可视化分析</p>
        </div>
      </div>
    </div>
    
    <!-- 最近使用 -->
    <div class="recent-section">
      <h2>最近使用</h2>
      <div class="recent-list">
        <div 
          v-for="tool in recentTools" 
          :key="tool.id"
          class="tool-item"
        >
          <div class="tool-icon-small">
            <el-icon><component :is="tool.icon" /></el-icon>
          </div>
          <div class="tool-info">
            <h4>{{ tool.name }}</h4>
            <p>{{ tool.description }}</p>
            <span class="tool-time">{{ tool.time }}</span>
          </div>
          <el-button size="small" @click="useTool(tool)">使用</el-button>
        </div>
      </div>
    </div>
    
    <!-- PDF转换对话框 -->
    <el-dialog
      v-model="showPDFDialog"
      title="PDF转换工具"
      width="600px"
    >
      <el-form :model="pdfForm" label-width="80px">
        <el-form-item label="转换类型">
          <el-select v-model="pdfForm.type" placeholder="选择转换类型">
            <el-option label="Word转PDF" value="word-to-pdf" />
            <el-option label="PDF转Word" value="pdf-to-word" />
            <el-option label="Excel转PDF" value="excel-to-pdf" />
            <el-option label="图片转PDF" value="image-to-pdf" />
          </el-select>
        </el-form-item>
        <el-form-item label="上传文件">
          <el-upload
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showPDFDialog = false">取消</el-button>
        <el-button type="primary" @click="convertPDF">开始转换</el-button>
      </template>
    </el-dialog>
    
    <!-- 网页爬虫对话框 -->
    <el-dialog
      v-model="showCrawlerDialog"
      title="网页爬虫工具"
      width="600px"
    >
      <el-form :model="crawlerForm" label-width="80px">
        <el-form-item label="目标URL">
          <el-input v-model="crawlerForm.url" placeholder="请输入要爬取的网页URL" />
        </el-form-item>
        <el-form-item label="爬取类型">
          <el-select v-model="crawlerForm.type" placeholder="选择爬取类型">
            <el-option label="文本内容" value="text" />
            <el-option label="图片链接" value="images" />
            <el-option label="链接地址" value="links" />
            <el-option label="表格数据" value="tables" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCrawlerDialog = false">取消</el-button>
        <el-button type="primary" @click="startCrawler">开始爬取</el-button>
      </template>
    </el-dialog>
    
    <!-- 测试用例生成对话框 -->
    <el-dialog
      v-model="showTestcaseDialog"
      title="测试用例生成工具"
      width="600px"
    >
      <el-form :model="testcaseForm" label-width="80px">
        <el-form-item label="功能描述">
          <el-input 
            v-model="testcaseForm.description" 
            type="textarea" 
            :rows="4"
            placeholder="请描述要测试的功能..."
          />
        </el-form-item>
        <el-form-item label="测试类型">
          <el-select v-model="testcaseForm.type" placeholder="选择测试类型">
            <el-option label="功能测试" value="functional" />
            <el-option label="性能测试" value="performance" />
            <el-option label="安全测试" value="security" />
            <el-option label="兼容性测试" value="compatibility" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showTestcaseDialog = false">取消</el-button>
        <el-button type="primary" @click="generateTestcase">生成测试用例</el-button>
      </template>
    </el-dialog>
    
    <!-- 其他工具对话框 -->
    <el-dialog
      v-model="showFormatterDialog"
      title="代码格式化工具"
      width="600px"
    >
      <el-form :model="formatterForm" label-width="80px">
        <el-form-item label="编程语言">
          <el-select v-model="formatterForm.language" placeholder="选择编程语言">
            <el-option label="JavaScript" value="javascript" />
            <el-option label="Python" value="python" />
            <el-option label="Java" value="java" />
            <el-option label="CSS" value="css" />
          </el-select>
        </el-form-item>
        <el-form-item label="代码内容">
          <el-input 
            v-model="formatterForm.code" 
            type="textarea" 
            :rows="8"
            placeholder="粘贴要格式化的代码..."
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showFormatterDialog = false">取消</el-button>
        <el-button type="primary" @click="formatCode">格式化代码</el-button>
      </template>
    </el-dialog>
    
    <!-- 二维码生成对话框 -->
    <el-dialog
      v-model="showQRCodeDialog"
      title="二维码生成工具"
      width="400px"
    >
      <el-form :model="qrcodeForm" label-width="80px">
        <el-form-item label="内容">
          <el-input v-model="qrcodeForm.content" placeholder="输入要生成二维码的内容" />
        </el-form-item>
        <el-form-item label="尺寸">
          <el-input-number v-model="qrcodeForm.size" :min="100" :max="500" />
        </el-form-item>
      </el-form>
      
      <div class="qrcode-preview" v-if="qrcodeForm.content">
        <img src="https://via.placeholder.com/200x200/4A90E2/FFFFFF?text=二维码" alt="二维码预览" />
      </div>
      
      <template #footer>
        <el-button @click="showQRCodeDialog = false">取消</el-button>
        <el-button type="primary" @click="generateQRCode">生成二维码</el-button>
      </template>
    </el-dialog>
    
    <!-- 哈希生成对话框 -->
    <el-dialog
      v-model="showHashDialog"
      title="哈希生成工具"
      width="500px"
    >
      <el-form :model="hashForm" label-width="80px">
        <el-form-item label="算法">
          <el-select v-model="hashForm.algorithm" placeholder="选择哈希算法">
            <el-option label="MD5" value="md5" />
            <el-option label="SHA1" value="sha1" />
            <el-option label="SHA256" value="sha256" />
            <el-option label="SHA512" value="sha512" />
          </el-select>
        </el-form-item>
        <el-form-item label="输入内容">
          <el-input 
            v-model="hashForm.input" 
            type="textarea" 
            :rows="4"
            placeholder="输入要计算哈希的内容..."
          />
        </el-form-item>
        <el-form-item label="哈希值" v-if="hashForm.output">
          <el-input v-model="hashForm.output" readonly />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showHashDialog = false">取消</el-button>
        <el-button type="primary" @click="generateHash">生成哈希</el-button>
      </template>
    </el-dialog>
    
    <!-- Base64编码对话框 -->
    <el-dialog
      v-model="showBase64Dialog"
      title="Base64编码工具"
      width="500px"
    >
      <el-form :model="base64Form" label-width="80px">
        <el-form-item label="操作类型">
          <el-radio-group v-model="base64Form.type">
            <el-radio label="encode">编码</el-radio>
            <el-radio label="decode">解码</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="输入内容">
          <el-input 
            v-model="base64Form.input" 
            type="textarea" 
            :rows="4"
            placeholder="输入要编码或解码的内容..."
          />
        </el-form-item>
        <el-form-item label="输出结果" v-if="base64Form.output">
          <el-input v-model="base64Form.output" type="textarea" :rows="4" readonly />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showBase64Dialog = false">取消</el-button>
        <el-button type="primary" @click="processBase64">处理</el-button>
      </template>
    </el-dialog>
    
    <!-- 数据分析对话框 -->
    <el-dialog
      v-model="showAnalysisDialog"
      title="数据分析工具"
      width="700px"
    >
      <el-form :model="analysisForm" label-width="80px">
        <el-form-item label="数据类型">
          <el-select v-model="analysisForm.type" placeholder="选择数据类型">
            <el-option label="CSV文件" value="csv" />
            <el-option label="Excel文件" value="excel" />
            <el-option label="JSON数据" value="json" />
          </el-select>
        </el-form-item>
        <el-form-item label="上传文件">
          <el-upload
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAnalysisDialog = false">取消</el-button>
        <el-button type="primary" @click="analyzeData">开始分析</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 对话框状态
const showPDFDialog = ref(false)
const showCrawlerDialog = ref(false)
const showTestcaseDialog = ref(false)
const showFormatterDialog = ref(false)
const showQRCodeDialog = ref(false)
const showHashDialog = ref(false)
const showBase64Dialog = ref(false)
const showAnalysisDialog = ref(false)

// 表单数据
const pdfForm = reactive({
  type: '',
  file: null
})

const crawlerForm = reactive({
  url: '',
  type: ''
})

const testcaseForm = reactive({
  description: '',
  type: ''
})

const formatterForm = reactive({
  language: '',
  code: ''
})

const qrcodeForm = reactive({
  content: '',
  size: 200
})

const hashForm = reactive({
  algorithm: '',
  input: '',
  output: ''
})

const base64Form = reactive({
  type: 'encode',
  input: '',
  output: ''
})

const analysisForm = reactive({
  type: '',
  file: null
})

// 最近使用的工具
const recentTools = ref([
  {
    id: 1,
    name: 'PDF转换',
    description: 'Word转PDF',
    time: '2小时前',
    icon: 'Document'
  },
  {
    id: 2,
    name: '代码格式化',
    description: 'JavaScript代码',
    time: '4小时前',
    icon: 'Tools'
  },
  {
    id: 3,
    name: '二维码生成',
    description: '生成链接二维码',
    time: '6小时前',
    icon: 'Grid'
  }
])

// 文件上传处理
const handleFileChange = (file: any) => {
  pdfForm.file = file.raw
}

// 使用工具
const useTool = (tool: any) => {
  ElMessage.info(`使用工具: ${tool.name}`)
}

// 转换PDF
const convertPDF = () => {
  if (!pdfForm.type || !pdfForm.file) {
    ElMessage.warning('请选择转换类型并上传文件')
    return
  }
  ElMessage.success('PDF转换任务已提交')
  showPDFDialog.value = false
}

// 开始爬虫
const startCrawler = () => {
  if (!crawlerForm.url || !crawlerForm.type) {
    ElMessage.warning('请填写URL并选择爬取类型')
    return
  }
  ElMessage.success('爬虫任务已启动')
  showCrawlerDialog.value = false
}

// 生成测试用例
const generateTestcase = () => {
  if (!testcaseForm.description || !testcaseForm.type) {
    ElMessage.warning('请填写功能描述并选择测试类型')
    return
  }
  ElMessage.success('测试用例生成完成')
  showTestcaseDialog.value = false
}

// 格式化代码
const formatCode = () => {
  if (!formatterForm.language || !formatterForm.code) {
    ElMessage.warning('请选择编程语言并输入代码')
    return
  }
  ElMessage.success('代码格式化完成')
  showFormatterDialog.value = false
}

// 生成二维码
const generateQRCode = () => {
  if (!qrcodeForm.content) {
    ElMessage.warning('请输入要生成二维码的内容')
    return
  }
  ElMessage.success('二维码生成完成')
  showQRCodeDialog.value = false
}

// 生成哈希
const generateHash = () => {
  if (!hashForm.algorithm || !hashForm.input) {
    ElMessage.warning('请选择算法并输入内容')
    return
  }
  hashForm.output = `生成的${hashForm.algorithm}哈希值: ${hashForm.input}`
  ElMessage.success('哈希生成完成')
}

// 处理Base64
const processBase64 = () => {
  if (!base64Form.input) {
    ElMessage.warning('请输入要处理的内容')
    return
  }
  base64Form.output = base64Form.type === 'encode' 
    ? `编码结果: ${base64Form.input}` 
    : `解码结果: ${base64Form.input}`
  ElMessage.success('Base64处理完成')
}

// 分析数据
const analyzeData = () => {
  if (!analysisForm.type) {
    ElMessage.warning('请选择数据类型')
    return
  }
  ElMessage.success('数据分析完成')
  showAnalysisDialog.value = false
}

onMounted(() => {
  // 初始化数据
})
</script>

<style scoped>
.geek-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 32px;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: #909399;
  font-size: 16px;
}

.tools-section {
  margin-bottom: 40px;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.tool-card {
  background: white;
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 1px solid #f0f0f0;
}

.tool-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.tool-icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  font-size: 32px;
  color: white;
}

.tool-icon.pdf {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.tool-icon.crawler {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.tool-icon.testcase {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.tool-icon.formatter {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.tool-icon.qrcode {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.tool-icon.hash {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.tool-icon.base64 {
  background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
}

.tool-icon.analysis {
  background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
}

.tool-card h3 {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.tool-card p {
  color: #606266;
  margin: 0;
  line-height: 1.5;
}

.recent-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.recent-section h2 {
  margin: 0 0 24px 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.recent-list {
  display: grid;
  gap: 16px;
}

.tool-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
}

.tool-icon-small {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #e3f2fd;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  color: #2196f3;
  font-size: 20px;
}

.tool-info {
  flex: 1;
}

.tool-info h4 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.tool-info p {
  color: #606266;
  margin-bottom: 8px;
}

.tool-time {
  color: #909399;
  font-size: 12px;
}

.qrcode-preview {
  text-align: center;
  margin-top: 16px;
}

.qrcode-preview img {
  width: 200px;
  height: 200px;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .geek-page {
    padding: 16px;
  }
  
  .tools-grid {
    grid-template-columns: 1fr;
  }
  
  .tool-card {
    padding: 24px 16px;
  }
}
</style>
