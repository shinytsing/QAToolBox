
// 调试PDF转换API响应
function debugPDFConversion() {
    const formData = new FormData();
    formData.append('type', 'text-to-pdf');
    formData.append('text_content', '测试文本内容');
    
    fetch('/tools/api/pdf-converter/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        return response.json();
    })
    .then(data => {
        console.log('API Response:', data);
        
        if (data.success) {
            console.log('download_url:', data.download_url);
            console.log('filename:', data.filename);
            console.log('conversion_type:', data.conversion_type);
            
            if (data.download_url) {
                console.log('✅ download_url存在，可以正常下载');
            } else {
                console.log('❌ download_url不存在或为空');
            }
        } else {
            console.log('❌ 转换失败:', data.error);
        }
    })
    .catch(error => {
        console.error('请求失败:', error);
    });
}

// 在浏览器控制台中运行: debugPDFConversion()
