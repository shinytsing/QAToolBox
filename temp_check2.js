
// 简化的代理系统 - 专注核心功能
let systemReady = false;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 代理系统初始化...');
    try {
        initializeSystem();
        log('系统初始化完成');
    } catch (error) {
        console.error('初始化失败:', error);
        log('系统初始化失败: ' + error.message, 'error');
    }
});

// 初始化商业化翻墙服务
async function initializeSystem() {
    try {
        log('正在初始化专业翻墙服务...');
        document.getElementById('systemStatus').textContent = '初始化中...';
        
        // 检测代理服务状态
        await checkProxyStatus();
        
        // 自动获取IP对比以显示服务状态
        await getIPComparison();
        
        // 测试YouTube访问（需要翻墙）
        await testYouTubeAccess();
        
        systemReady = true;
        document.getElementById('systemStatus').textContent = '就绪';
        log('✅ 翻墙服务已就绪');
        log('🌐 可直接访问YouTube、Google等全球网站');
        
    } catch (error) {
        log(`❌ 服务初始化失败: ${error.message}`, 'error');
        document.getElementById('systemStatus').textContent = '错误';
    }
}

// 检测代理服务状态
async function checkProxyStatus() {
    try {
        log('🔍 检测代理服务状态...');
        
        // 检测本地代理服务器
        const localProxyStatus = await testLocalProxy();
        if (localProxyStatus) {
            document.getElementById('proxyStatus').textContent = '本地代理可用';
            document.getElementById('proxyStatus').style.color = '#00ff88';
            log('✅ 本地代理服务器运行正常');
        } else {
            document.getElementById('proxyStatus').textContent = '本地代理不可用';
            document.getElementById('proxyStatus').style.color = '#ff6b6b';
            log('⚠️  本地代理服务器未运行，将使用备用方案');
        }
        
    } catch (error) {
        log(`❌ 代理状态检测失败: ${error.message}`, 'error');
        document.getElementById('proxyStatus').textContent = '检测失败';
        document.getElementById('proxyStatus').style.color = '#ff6b6b';
    }
}

// 测试本地代理服务器
async function testLocalProxy() {
    try {
        const response = await fetch('http://127.0.0.1:8080', {
            method: 'GET',
            mode: 'no-cors',
            timeout: 3000
        });
        return true;
    } catch (error) {
        return false;
    }
}

// 测试YouTube访问（需要翻墙）
async function testYouTubeAccess() {
    try {
        log('🔍 测试YouTube访问...');
        
        // 使用本地代理测试YouTube访问
        const response = await fetch('/tools/api/proxy/web-browse/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ url: 'https://www.youtube.com' })
        });
        
        const data = await response.json();
        
        if (data.success) {
            log('✅ YouTube访问正常，代理服务工作良好', 'success');
            document.getElementById('systemStatus').textContent = '代理正常';
            document.getElementById('systemStatus').style.color = '#00ff88';
        } else {
            log(`⚠️  YouTube访问异常: ${data.error}`, 'warning');
            document.getElementById('systemStatus').textContent = '代理异常';
            document.getElementById('systemStatus').style.color = '#ffaa00';
        }
    } catch (error) {
        log(`❌ YouTube访问失败: ${error.message}`, 'error');
        document.getElementById('systemStatus').textContent = '网络错误';
        document.getElementById('systemStatus').style.color = '#ff6b6b';
    }
}

// 日志输出
function log(message, type = 'info') {
    const terminal = document.getElementById('proxyTerminal');
    const timestamp = new Date().toLocaleTimeString();
    const color = type === 'error' ? '#ff4444' : type === 'success' ? '#00ff41' : '#00ffe7';
    
    terminal.innerHTML += `<div style="color: ${color};">[${timestamp}] ${message}</div>`;
    terminal.scrollTop = terminal.scrollHeight;
    console.log(`[${timestamp}] ${message}`);
}

// ===== 核心功能1: IP对比功能 =====
async function getIPComparison() {
    try {
        log('正在获取IP对比信息...');
        document.getElementById('localIP').textContent = '检测中...';
        document.getElementById('proxyIP').textContent = '检测中...';
        
        const response = await fetch('/tools/api/proxy/ip-comparison/');
        const data = await response.json();
        
        if (data.success) {
            displayIPComparison(data.data);
            log('✅ IP对比获取完成', 'success');
        } else {
            log(`❌ IP对比获取失败: ${data.error}`, 'error');
            document.getElementById('localIP').textContent = '获取失败';
            document.getElementById('proxyIP').textContent = '获取失败';
        }
    } catch (error) {
        log(`❌ 网络错误: ${error.message}`, 'error');
        document.getElementById('localIP').textContent = '网络错误';
        document.getElementById('proxyIP').textContent = '网络错误';
    }
}



// 显示IP对比结果
function displayIPComparison(data) {
    const resultsDiv = document.getElementById('ipComparisonResults');
    let html = '<div class="proxy-result-item">';
    
    // 更新状态栏
    if (data.direct_ip.success) {
        document.getElementById('localIP').textContent = data.direct_ip.ip;
        html += `
            <div style="margin-bottom: 15px;">
                <strong>🌐 本地IP:</strong> ${data.direct_ip.ip}
                <br><small>位置: ${data.direct_ip.country} ${data.direct_ip.region} ${data.direct_ip.city}</small>
                <br><small>ISP: ${data.direct_ip.isp}</small>
            </div>
        `;
    } else {
        document.getElementById('localIP').textContent = '获取失败';
        html += `
            <div style="margin-bottom: 15px;">
                <strong>🌐 本地IP:</strong> 获取失败
                <br><small>错误: ${data.direct_ip.error}</small>
            </div>
        `;
    }
    
    // 代理IP
    if (data.proxy_ip && data.proxy_ip.success) {
        document.getElementById('proxyIP').textContent = data.proxy_ip.ip;
        html += `
            <div style="margin-bottom: 15px;">
                <strong>🔗 代理IP:</strong> ${data.proxy_ip.ip}
                <br><small>位置: ${data.proxy_ip.country} ${data.proxy_ip.region} ${data.proxy_ip.city}</small>
                <br><small>代理: ${data.proxy_ip.proxy_used}</small>
            </div>
        `;
    } else {
        document.getElementById('proxyIP').textContent = 'N/A';
        html += `
            <div style="margin-bottom: 15px;">
                <strong>🔗 代理IP:</strong> 无法获取
                <br><small>说明: 需要使用Trojan客户端配置</small>
            </div>
        `;
    }
    
    html += '</div>';
    resultsDiv.innerHTML = html;
}

// ===== 核心功能2: 一键代理设置功能 =====
// 注意: 此功能需要相应的HTML元素支持，当前版本已注释
/*
async function setupProxy() {
    const targetUrl = document.getElementById('targetWebsite').value.trim();
    if (!targetUrl) {
        log('❌ 请输入要访问的外网地址', 'error');
        return;
    }
    
    try {
        log(`正在为 ${targetUrl} 设置最佳代理...`);
        document.getElementById('proxySetupResults').innerHTML = '<div class="loading"></div> 正在分析最佳代理...';
        
        const response = await fetch('/tools/api/proxy/setup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ url: targetUrl })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayProxySetup(data.data, targetUrl);
            log(`✅ 代理设置完成`, 'success');
        } else {
            log(`❌ 代理设置失败: ${data.error}`, 'error');
            document.getElementById('proxySetupResults').innerHTML = `<div class="proxy-result-item error">设置失败: ${data.error}</div>`;
        }
    } catch (error) {
        log(`❌ 网络错误: ${error.message}`, 'error');
        document.getElementById('proxySetupResults').innerHTML = `<div class="proxy-result-item error">网络错误: ${error.message}</div>`;
    }
}

// 显示代理设置结果
function displayProxySetup(data, targetUrl) {
    const resultsDiv = document.getElementById('proxySetupResults');
    
    if (data.success) {
        const proxy = data.recommended_proxy;
        const item = document.createElement('div');
        item.className = 'proxy-result-item success';
        item.innerHTML = `
            <div style="margin-bottom: 15px;">
                <strong>🎯 推荐代理节点:</strong> ${proxy.name}
                <br><small>服务器: ${proxy.server}:${proxy.port}</small>
                <br><small>位置: ${proxy.country} | 类型: ${proxy.type}</small>
                <br><small>推荐理由: ${data.reason}</small>
            </div>
            
            <div style="margin-bottom: 15px;">
                <strong>🌐 目标网站:</strong> ${targetUrl}
            </div>
            
            <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; margin: 10px 0;">
                ${proxy.type === 'trojan' ? `
                    <h4 style="color: #00ffe7; margin-bottom: 10px;">🔐 Trojan配置信息</h4>
                    <p><strong>服务器:</strong> ${proxy.server}</p>
                    <p><strong>端口:</strong> ${proxy.port}</p>
                    <p><strong>密码:</strong> ${proxy.password}</p>
                    <p><strong>协议:</strong> Trojan</p>
                    
                    <div style="background: rgba(255,107,157,0.1); padding: 10px; border-radius: 5px; margin: 10px 0; color: #ff6b9d;">
                        💡 <strong>使用方法:</strong><br>
                        1. 下载Clash、V2Ray等客户端<br>
                        2. 将以上配置信息添加到客户端<br>
                        3. 启用代理后即可访问 ${targetUrl}
                    </div>
                    
                    <button class="proxy-btn" onclick="copyTrojanConfig('${proxy.server}', '${proxy.port}', '${proxy.password}')">
                        📋 复制配置信息
                    </button>
                ` : `
                    <h4 style="color: #00ffe7; margin-bottom: 10px;">🔗 HTTP代理设置</h4>
                    <p><strong>代理地址:</strong> ${proxy.server}</p>
                    <p><strong>代理端口:</strong> ${proxy.port}</p>
                    <p><strong>协议:</strong> HTTP</p>
                    
                    <div style="background: rgba(255,107,157,0.1); padding: 10px; border-radius: 5px; margin: 10px 0; color: #ff6b9d;">
                        💡 <strong>使用方法:</strong><br>
                        在浏览器或系统网络设置中配置HTTP代理即可访问外网
                    </div>
                `}
            </div>
            
            <button class="proxy-btn success" onclick="testProxyAccess('${proxy.name}', '${targetUrl}')">
                🚀 测试代理访问
            </button>
        `;
        resultsDiv.innerHTML = '';
        resultsDiv.appendChild(item);
    } else {
        const item = document.createElement('div');
        item.className = 'proxy-result-item error';
        item.innerHTML = `
            <strong>❌ 代理设置失败</strong>
            <br>错误: ${data.error}
            <br>目标网站: ${targetUrl}
        `;
        resultsDiv.innerHTML = '';
        resultsDiv.appendChild(item);
    }
}
*/

// ===== 核心功能: Web翻墙浏览器 =====

let currentBrowserUrl = '';
let browserHistory = [];
let currentHistoryIndex = -1;
let isPictureInPicture = false;

// 打开Web代理浏览器
async function openWebBrowser() {
    const url = document.getElementById('webBrowserUrl').value.trim();
    if (!url) {
        log('❌ 请输入要访问的网址', 'error');
        return;
    }
    
    // 显示浏览器模态框
    document.getElementById('webBrowserModal').style.display = 'flex';
    document.getElementById('browserAddressBar').value = url;
    
    // 加载网页
    await loadWebPage(url);
}

// 快速访问预设网站
async function quickAccess(url) {
    document.getElementById('webBrowserUrl').value = url;
    await openWebBrowser();
}

// 加载网页内容
async function loadWebPage(url) {
    try {
        // 确保URL格式正确
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            url = 'https://' + url;
        }
        
        log(`正在加载: ${url}`);
        
        // 显示加载状态
        document.getElementById('browserLoading').style.display = 'flex';
        document.getElementById('browserContainer').innerHTML = '';
        
        const response = await fetch('/tools/api/proxy/web-browse/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        
        // 隐藏加载状态
        document.getElementById('browserLoading').style.display = 'none';
        
        if (data.success) {
            // 处理内容编码和显示
            let content = data.data.content;
            
            // 确保内容包含正确的编码声明
            if (!content.includes('charset') && !content.includes('encoding')) {
                if (content.includes('<head>')) {
                    content = content.replace('<head>', '<head><meta charset="UTF-8">');
                } else if (content.includes('<html>')) {
                    content = content.replace('<html>', '<html><head><meta charset="UTF-8"></head>');
                } else {
                    content = `<!DOCTYPE html><html><head><meta charset="UTF-8"><title>代理浏览器</title></head><body>${content}</body></html>`;
                }
            }
            
            // 添加基础样式来改善显示效果
            const baseStyles = `
                <style>
                    body { 
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        margin: 20px;
                        background-color: #fff;
                    }
                    img { max-width: 100%; height: auto; }
                    a { color: #1976d2; text-decoration: none; }
                    a:hover { text-decoration: underline; }
                </style>
            `;
            
            if (content.includes('</head>')) {
                content = content.replace('</head>', baseStyles + '</head>');
            } else {
                content = baseStyles + content;
            }
            
            // 创建iframe显示内容
            const iframe = document.createElement('iframe');
            iframe.className = 'web-browser-iframe';
            // 更宽松的sandbox设置以支持更多交互
            iframe.sandbox = 'allow-same-origin allow-scripts allow-forms allow-popups allow-top-navigation allow-pointer-lock allow-orientation-lock allow-presentation allow-downloads';
            
            // 使用blob URL来避免编码问题
            const blob = new Blob([content], { type: 'text/html; charset=utf-8' });
            const blobUrl = URL.createObjectURL(blob);
            
            iframe.onload = function() {
                URL.revokeObjectURL(blobUrl);
                log(`✅ 网页内容加载完成: ${data.data.final_url}`, 'success');
                log(`📊 内容长度: ${data.data.content_length} 字符`, 'info');
                log(`🔤 使用编码: ${data.data.charset_used || 'unknown'}`, 'info');
                
                // 改进iframe交互处理
                setTimeout(() => {
                    try {
                        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                        if (iframeDoc && iframeDoc.body) {
                            const bodyText = iframeDoc.body.innerText || iframeDoc.body.textContent;
                            if (!bodyText || bodyText.trim().length < 10) {
                                log(`⚠️  iframe内容可能为空，建议在新窗口打开`, 'warning');
                                // 尝试使用srcdoc方式
                                iframe.srcdoc = content;
                            } else if (bodyText.includes('�') || bodyText.match(/[^\x00-\x7F\u4e00-\u9fff\u3400-\u4dbf]/g)) {
                                log(`⚠️  检测到可能的乱码字符，建议在新窗口打开获得更好体验`, 'warning');
                            } else {
                                log(`✅ iframe内容验证通过`, 'success');
                            }
                            
                            // 添加点击提示
                            const interactionHint = document.createElement('div');
                            interactionHint.style.cssText = `
                                position: absolute;
                                top: 10px;
                                right: 10px;
                                background: rgba(0, 0, 0, 0.8);
                                color: white;
                                padding: 8px 12px;
                                border-radius: 5px;
                                font-size: 12px;
                                z-index: 1000;
                                cursor: pointer;
                                transition: opacity 0.3s;
                            `;
                            interactionHint.innerHTML = '💡 交互受限？点击"新窗口打开"获得完整体验';
                            interactionHint.onclick = () => openInNewWindow();
                            
                            const browserContainer = document.getElementById('browserContainer');
                            browserContainer.style.position = 'relative';
                            browserContainer.appendChild(interactionHint);
                            
                            // 5秒后自动隐藏提示
                            setTimeout(() => {
                                if (interactionHint && interactionHint.parentNode) {
                                    interactionHint.style.opacity = '0';
                                    setTimeout(() => {
                                        if (interactionHint.parentNode) {
                                            interactionHint.parentNode.removeChild(interactionHint);
                                        }
                                    }, 300);
                                }
                            }, 5000);
                        }
                    } catch (e) {
                        log(`ℹ️  iframe交互受限（跨域保护），建议使用"新窗口打开"功能`, 'info');
                    }
                }, 1000);
            };
            
            iframe.onerror = function() {
                URL.revokeObjectURL(blobUrl);
                log(`❌ iframe加载失败，尝试使用srcdoc方式`, 'error');
                
                // 尝试使用srcdoc作为备选方案
                iframe.src = '';
                iframe.srcdoc = content;
            };
            
            iframe.src = blobUrl;
            
            document.getElementById('browserContainer').innerHTML = '';
            document.getElementById('browserContainer').appendChild(iframe);
            
            // 更新浏览历史
            currentBrowserUrl = url;
            if (currentHistoryIndex === -1 || browserHistory[currentHistoryIndex] !== url) {
                browserHistory = browserHistory.slice(0, currentHistoryIndex + 1);
                browserHistory.push(url);
                currentHistoryIndex = browserHistory.length - 1;
            }
            
            log(`✅ 网页加载成功: ${url}`, 'success');
            
        } else {
            document.getElementById('browserContainer').innerHTML = 
                `<div class="browser-placeholder">
                    <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: #ff4444; margin-bottom: 1rem;"></i>
                    <p>网页加载失败</p>
                    <p>${data.error}</p>
                </div>`;
            log(`❌ 网页加载失败: ${data.error}`, 'error');
        }
        
    } catch (error) {
        document.getElementById('browserLoading').style.display = 'none';
        document.getElementById('browserContainer').innerHTML = 
            `<div class="browser-placeholder">
                <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: #ff4444; margin-bottom: 1rem;"></i>
                <p>网络错误</p>
                <p>${error.message}</p>
            </div>`;
        log(`❌ 网络错误: ${error.message}`, 'error');
    }
}

// 浏览器导航
async function browserNavigate() {
    const url = document.getElementById('browserAddressBar').value.trim();
    if (url) {
        await loadWebPage(url);
    }
}

// 浏览器后退
function browserBack() {
    if (currentHistoryIndex > 0) {
        currentHistoryIndex--;
        const url = browserHistory[currentHistoryIndex];
        document.getElementById('browserAddressBar').value = url;
        loadWebPage(url);
    }
}

// 浏览器前进
function browserForward() {
    if (currentHistoryIndex < browserHistory.length - 1) {
        currentHistoryIndex++;
        const url = browserHistory[currentHistoryIndex];
        document.getElementById('browserAddressBar').value = url;
        loadWebPage(url);
    }
}

// 浏览器刷新
function browserRefresh() {
    if (currentBrowserUrl) {
        loadWebPage(currentBrowserUrl);
    }
}

// 切换画中画模式
function togglePictureInPicture() {
    const modal = document.getElementById('webBrowserModal');
    
    if (!isPictureInPicture) {
        // 切换到画中画模式
        modal.classList.add('picture-in-picture');
        document.querySelector('.web-browser-modal .fas.fa-compress').className = 'fas fa-expand';
        isPictureInPicture = true;
        log('✅ 已切换到画中画模式', 'success');
    } else {
        // 切换到全屏模式
        modal.classList.remove('picture-in-picture');
        document.querySelector('.web-browser-modal .fas.fa-expand').className = 'fas fa-compress';
        isPictureInPicture = false;
        log('✅ 已切换到全屏模式', 'success');
    }
}

// 关闭浏览器
function closeBrowser() {
    document.getElementById('webBrowserModal').style.display = 'none';
    isPictureInPicture = false;
    currentBrowserUrl = '';
    log('🔧 Web代理浏览器已关闭');
}

// 在新窗口打开当前页面
function openInNewWindow() {
    if (!currentBrowserUrl) {
        log('❌ 没有可打开的页面', 'error');
        return;
    }
    
    // 创建一个代理访问链接
    const proxyUrl = `/tools/api/proxy/web-browse/?url=${encodeURIComponent(currentBrowserUrl)}`;
    
    // 打开新窗口并显示代理内容
    const newWindow = window.open('', '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
    if (newWindow) {
        newWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>代理浏览器 - ${currentBrowserUrl}</title>
                <meta charset="UTF-8">
                <style>
                    body { margin: 0; padding: 20px; font-family: Arial, sans-serif; }
                    .header { background: #f5f5f5; padding: 10px; margin-bottom: 20px; border-radius: 5px; }
                    .url { color: #666; font-size: 14px; }
                    iframe { width: 100%; height: 80vh; border: 1px solid #ddd; border-radius: 5px; }
                    .loading { text-align: center; padding: 50px; color: #666; }
                </style>
            </head>
            <body>
                <div class="header">
                    <strong>代理浏览器</strong>
                    <div class="url">访问: ${currentBrowserUrl}</div>
                </div>
                <div id="content" class="loading">正在加载页面内容...</div>
                <script>
                    // 获取页面内容并显示
                    const csrfToken = document.cookie.split(';').find(row => row.startsWith('csrftoken='))?.split('=')[1] || '';
                    const targetUrl = '${currentBrowserUrl}';
                    const apiUrl = '/tools/api/proxy/web-browse/';
                    
                    fetch(apiUrl, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({ url: targetUrl })
                    })
                    .then(response => response.json())
                    .then(data => {
                        const contentDiv = document.getElementById('content');
                        if (data.success) {
                            const iframe = document.createElement('iframe');
                            iframe.srcdoc = data.data.content;
                            iframe.style.width = '100%';
                            iframe.style.height = '80vh';
                            iframe.style.border = '1px solid #ddd';
                            iframe.style.borderRadius = '5px';
                            contentDiv.innerHTML = '';
                            contentDiv.appendChild(iframe);
                        } else {
                            contentDiv.innerHTML = '<div style="color: red;">加载失败: ' + data.error + '</div>';
                        }
                    })
                    .catch(error => {
                        document.getElementById('content').innerHTML = '<div style="color: red;">网络错误: ' + error.message + '</div>';
                    });
                </script>
            </body>
            </html>
        `);
        log('🔗 页面已在新窗口打开，可以正常交互', 'success');
    } else {
        log('❌ 无法打开新窗口，请检查浏览器设置', 'error');
    }
}

// 刷新当前页面
function refreshCurrentPage() {
    if (!currentBrowserUrl) {
        log('❌ 没有可刷新的页面', 'error');
        return;
    }
    
    log('🔄 刷新页面: ' + currentBrowserUrl);
    loadWebPage(currentBrowserUrl);
}

// 全屏模式切换
function toggleFullscreen() {
    const modal = document.getElementById('webBrowserModal');
    
    if (!document.fullscreenElement) {
        // 进入全屏
        if (modal.requestFullscreen) {
            modal.requestFullscreen();
        } else if (modal.webkitRequestFullscreen) {
            modal.webkitRequestFullscreen();
        } else if (modal.mozRequestFullScreen) {
            modal.mozRequestFullScreen();
        }
        log('📺 进入全屏模式', 'success');
    } else {
        // 退出全屏
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
        }
        log('🪟 退出全屏模式', 'success');
    }
}

// ===== 辅助函数 =====

// 复制Trojan配置信息到剪贴板
async function copyTrojanConfig(server, port, password) {
    const configText = `
服务器: ${server}
端口: ${port}
密码: ${password}
协议: Trojan
    `.trim();
    
    try {
        await navigator.clipboard.writeText(configText);
        log('✅ 配置信息已复制到剪贴板', 'success');
    } catch (error) {
        log('❌ 复制失败，请手动复制配置信息', 'error');
        // 创建临时文本区域进行复制（兼容性方案）
        const textArea = document.createElement('textarea');
        textArea.value = configText;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            log('✅ 配置信息已复制到剪贴板', 'success');
        } catch (e) {
            log('❌ 复制失败', 'error');
        }
        document.body.removeChild(textArea);
    }
}

// 测试代理访问
async function testProxyAccess(proxyName, targetUrl) {
    try {
        log(`正在测试代理访问: ${proxyName} -> ${targetUrl}`);
        
        const response = await fetch('/tools/api/proxy/create-url/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ 
                proxy: proxyName, 
                url: targetUrl 
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (data.data.proxy_config.type === 'trojan') {
                log('✅ Trojan代理配置已生成，请使用客户端连接', 'success');
            } else {
                log('✅ HTTP代理访问链接已创建', 'success');
                // 对于HTTP代理，可以尝试在新窗口打开
                window.open(data.data.proxy_url, '_blank');
            }
        } else {
            log(`❌ 创建代理访问链接失败: ${data.error}`, 'error');
        }
    } catch (error) {
        log(`❌ 网络错误: ${error.message}`, 'error');
    }
}

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

// 键盘快捷键
document.addEventListener('keydown', function(e) {
    // 全局快捷键
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        getIPComparison();
        log('🔄 刷新网络状态');
    }
    if (e.ctrlKey && e.key === 'w') {
        e.preventDefault();
        const url = document.getElementById('webBrowserUrl').value.trim();
        if (url) {
            openWebBrowser();
        } else {
            log('❌ 请先输入网址，然后按Ctrl+W打开翻墙浏览器');
        }
    }
    
    // 浏览器内快捷键
    if (document.getElementById('webBrowserModal').style.display === 'flex') {
        if (e.key === 'Escape') {
            closeBrowser();
        }
        if (e.ctrlKey && e.key === 'p') {
            e.preventDefault();
            togglePictureInPicture();
        }
    }
});

// 浏览器地址栏回车事件
document.addEventListener('DOMContentLoaded', function() {
    const browserAddressBar = document.getElementById('browserAddressBar');
    if (browserAddressBar) {
        browserAddressBar.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                browserNavigate();
            }
