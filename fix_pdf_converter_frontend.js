// 修复后的PDF转换器前端代码
// 解决 download_url 为 undefined 的问题

// 全局变量
let selectedFile = null;
let selectedType = '';

// 获取CSRF Token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 显示通知
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification-modern ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-circle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 显示动画
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // 自动隐藏
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// 修复后的转换函数
function performConversion() {
    if (!selectedFile && selectedType !== 'text-to-pdf') {
        showNotification('请先选择文件！', 'error');
        return;
    }
    
    if (!selectedType) {
        showNotification('请先选择转换类型！', 'error');
        return;
    }
    
    console.log('开始转换:', { selectedType, selectedFile: selectedFile?.name });
    
    const formData = new FormData();
    
    if (selectedType === 'text-to-pdf') {
        // 文本转PDF
        const textInput = document.getElementById('textInput');
        if (!textInput || !textInput.value.trim()) {
            showNotification('请输入要转换的文本内容！', 'error');
            return;
        }
        formData.append('type', 'text-to-pdf');
        formData.append('text_content', textInput.value.trim());
    } else {
        // 文件转换
        formData.append('file', selectedFile);
        formData.append('type', selectedType);
    }
    
    // 显示进度
    simulateProgress();
    
    // 发送API请求
    fetch('/tools/api/pdf-converter/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        console.log('API响应状态:', response.status);
        console.log('Content-Type:', response.headers.get('Content-Type'));
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        // 检查响应类型
        const contentType = response.headers.get('Content-Type');
        if (contentType && contentType.includes('application/json')) {
            return response.json();
        } else {
            // 如果不是JSON，可能是重定向到登录页面
            return response.text().then(text => {
                console.log('非JSON响应内容:', text.substring(0, 200));
                throw new Error('服务器返回非JSON响应，可能需要登录认证');
            });
        }
    })
    .then(data => {
        console.log('API响应数据:', data);
        
        if (data.success) {
            showConversionResult(data);
        } else {
            showNotification(data.error || '转换失败', 'error');
            const conversionProgress = document.getElementById('conversionProgress');
            if (conversionProgress) conversionProgress.style.display = 'none';
        }
    })
    .catch(error => {
        console.error('转换错误:', error);
        let errorMessage = error.message;
        
        // 提供更友好的错误提示
        if (error.message.includes('需要登录认证')) {
            errorMessage = '请先登录后再使用PDF转换功能';
        } else if (error.message.includes('Unexpected token')) {
            errorMessage = '会话已过期，请重新登录后重试';
        }
        
        showNotification('转换过程中发生错误: ' + errorMessage, 'error');
        const conversionProgress = document.getElementById('conversionProgress');
        if (conversionProgress) conversionProgress.style.display = 'none';
    });
}

// 修复后的结果显示函数
function showConversionResult(data) {
    console.log('显示转换结果:', data);
    
    // 清除进度模拟
    if (window.progressInterval) {
        clearInterval(window.progressInterval);
    }
    
    const conversionProgress = document.getElementById('conversionProgress');
    const resultContent = document.getElementById('resultContent');
    const conversionResult = document.getElementById('conversionResult');
    
    if (conversionProgress) conversionProgress.style.display = 'none';
    
    if (!resultContent) {
        console.error('结果内容元素未找到');
        return;
    }
    
    const fileName = selectedFile ? selectedFile.name : '文本内容';
    
    // 检查API响应中的必需字段
    if (!data.download_url) {
        console.error('API响应中缺少download_url字段:', data);
        showNotification('转换成功但无法获取下载链接，请检查API响应', 'error');
        return;
    }
    
    if (data.type === 'images') {
        // 显示图片结果
        let imagesHtml = '<div class="image-gallery-modern">';
        data.data.forEach((image, index) => {
            imagesHtml += `
                <div class="image-item-modern">
                    <img src="data:image/png;base64,${image.data}" alt="页面 ${image.page}">
                    <div class="page-info">第 ${image.page} 页</div>
                </div>
            `;
        });
        imagesHtml += '</div>';
        
        resultContent.innerHTML = `
            <div class="result-icon-modern">
                <i class="fas fa-images"></i>
            </div>
            <div class="result-title-modern">✅ 转换完成</div>
            <div class="result-description-modern">
                文件 <strong>${fileName}</strong> 已成功转换为图片格式，共 ${data.total_pages} 页
                <br>总大小: ${formatFileSize(data.total_size)}
            </div>
            ${imagesHtml}
            <div class="result-actions-modern">
                <button class="convert-again-btn-modern" onclick="convertAgain()">
                    <i class="fas fa-redo"></i>
                    转换其他文件
                </button>
            </div>
        `;
    } else {
        // 显示文件下载结果
        const fileSize = data.file_size ? formatFileSize(data.file_size) : '';
        const conversionType = data.conversion_type || selectedType || 'unknown';
        const outputFileName = getOutputFileName(fileName, conversionType);
        
        console.log('准备显示下载结果:', {
            download_url: data.download_url,
            filename: data.filename,
            outputFileName: outputFileName
        });
        
        resultContent.innerHTML = `
            <div class="result-icon-modern">
                <i class="fas fa-check-circle"></i>
            </div>
            <div class="result-title-modern">✅ 转换完成</div>
            <div class="result-description-modern">
                ${conversionType === 'text-to-pdf' ? '文本内容' : `文件 <strong>${fileName}</strong>`} 已成功转换为 ${getTypeName(conversionType)} 格式
                ${fileSize ? `<br>文件大小: ${fileSize}` : ''}
                <br><strong>输出文件名: ${outputFileName}</strong>
            </div>
            <div class="result-actions-modern">
                <a href="${data.download_url}" class="download-btn-modern" download="${outputFileName}" id="autoDownloadLink">
                    <i class="fas fa-download"></i>
                    重新下载
                </a>
                <button class="convert-again-btn-modern" onclick="convertAgain()">
                    <i class="fas fa-redo"></i>
                    转换其他文件
                </button>
            </div>
        `;
        
        // 自动触发下载
        setTimeout(() => {
            console.log('开始自动下载:', data.download_url);
            downloadFile(data.download_url, outputFileName);
            showNotification(`文件 "${outputFileName}" 正在下载...`, 'info');
        }, 1000);
    }
    
    if (conversionResult) conversionResult.style.display = 'block';
    showNotification('文件转换完成！', 'success');
}

// 修复后的下载函数
function downloadFile(url, filename) {
    console.log(`开始下载: ${url}, 文件名: ${filename}`);
    
    if (!url) {
        console.error('下载URL为空');
        showNotification('下载链接无效', 'error');
        return;
    }
    
    // 方法1: 使用fetch下载
    fetch(url)
        .then(response => {
            console.log('Download response status:', response.status);
            if (response.ok) {
                return response.blob();
            }
            throw new Error(`HTTP ${response.status}`);
        })
        .then(blob => {
            console.log('Download blob size:', blob.size);
            
            // 创建下载链接
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = filename;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(downloadUrl);
            
            console.log(`下载成功: ${filename}`);
            showNotification(`文件 "${filename}" 下载成功`, 'success');
        })
        .catch(error => {
            console.error(`下载失败: ${error.message}`);
            
            // 方法2: 备用下载方法
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            link.target = '_blank';
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            console.log(`使用备用方法下载: ${filename}`);
            showNotification(`使用备用方法下载: ${filename}`, 'info');
        });
}

// 辅助函数
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function getOutputFileName(originalName, conversionType) {
    const nameMap = {
        'text-to-pdf': 'converted_text.pdf',
        'pdf-to-word': originalName.replace(/\.pdf$/i, '.docx'),
        'word-to-pdf': originalName.replace(/\.(doc|docx)$/i, '.pdf'),
        'pdf-to-image': originalName.replace(/\.pdf$/i, '_images.zip'),
        'image-to-pdf': originalName.replace(/\.(jpg|jpeg|png|gif|bmp|tiff)$/i, '.pdf'),
        'pdf-to-text': originalName.replace(/\.pdf$/i, '.txt')
    };
    return nameMap[conversionType] || `converted_${originalName}`;
}

function getTypeName(conversionType) {
    const nameMap = {
        'text-to-pdf': 'PDF',
        'pdf-to-word': 'Word',
        'word-to-pdf': 'PDF',
        'pdf-to-image': '图片',
        'image-to-pdf': 'PDF',
        'pdf-to-text': '文本'
    };
    return nameMap[conversionType] || conversionType;
}

function simulateProgress() {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    let progress = 0;
    
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        
        if (progressFill) progressFill.style.width = progress + '%';
        
        if (progressText) {
            if (progress < 30) {
                progressText.textContent = '正在分析文件...';
            } else if (progress < 60) {
                progressText.textContent = '正在转换格式...';
            } else {
                progressText.textContent = '正在优化输出...';
            }
        }
    }, 200);
    
    window.progressInterval = interval;
}

function convertAgain() {
    // 重置所有状态变量
    selectedFile = null;
    selectedType = '';
    
    // 隐藏转换结果和进度
    const conversionResult = document.getElementById('conversionResult');
    const fileUpload = document.getElementById('fileUpload');
    const conversionProgress = document.getElementById('conversionProgress');
    
    if (conversionResult) conversionResult.style.display = 'none';
    if (fileUpload) fileUpload.style.display = 'none';
    if (conversionProgress) conversionProgress.style.display = 'none';
    
    // 重置文件信息显示
    const fileInfo = document.getElementById('fileInfo');
    if (fileInfo) fileInfo.style.display = 'none';
    
    // 重置转换按钮
    const convertBtn = document.getElementById('convertBtn');
    if (convertBtn) convertBtn.style.display = 'none';
    
    // 取消选择所有转换类型卡片
    document.querySelectorAll('.type-card-modern').forEach(card => {
        card.classList.remove('selected');
    });
    
    // 重置上传区域
    const uploadArea = document.getElementById('uploadArea');
    if (uploadArea) {
        uploadArea.style.display = 'block';
        uploadArea.innerHTML = `
            <div class="upload-icon-modern">
                <i class="fas fa-cloud-upload-alt"></i>
            </div>
            <div class="upload-text-modern">拖拽文件到此处或点击选择文件</div>
            <div class="upload-hint-modern" id="uploadHint">支持多种格式文件</div>
        `;
        
        // 重新创建fileInput元素并绑定事件
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.id = 'fileInput';
        fileInput.accept = '.pdf,.doc,.docx,.jpg,.jpeg,.png,.txt';
        fileInput.style.display = 'none';
        fileInput.addEventListener('change', handleFileUpload);
        uploadArea.appendChild(fileInput);
        
        // 恢复原始的onclick事件
        uploadArea.onclick = function() { safeClick('fileInput'); };
    }
    
    showNotification('已重置转换界面，可以开始新的转换', 'success');
}

// 文件上传处理函数（需要根据实际HTML结构调整）
function handleFileUpload(event) {
    const files = event.target.files;
    if (files.length > 0) {
        selectedFile = files[0];
        console.log('选择文件:', selectedFile.name);
        showNotification(`已选择文件: ${selectedFile.name}`, 'success');
    }
}

// 安全的点击函数
function safeClick(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.click();
    } else {
        console.warn(`Element with id '${elementId}' not found`);
    }
}

// 导出函数供HTML使用
window.performConversion = performConversion;
window.showConversionResult = showConversionResult;
window.downloadFile = downloadFile;
window.convertAgain = convertAgain;
window.handleFileUpload = handleFileUpload;
window.safeClick = safeClick;
