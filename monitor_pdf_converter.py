#!/usr/bin/env python3
"""
PDF转换器操作监控脚本
实时监控用户操作和API请求
"""

import requests
import time
import json
from datetime import datetime

def monitor_pdf_converter():
    """监控PDF转换器操作"""
    print("🔍 PDF转换器操作监控已启动")
    print("=" * 60)
    print("📝 监控内容:")
    print("  - 页面访问状态")
    print("  - API请求状态")
    print("  - 错误信息")
    print("  - 转换结果")
    print("=" * 60)
    print("⏳ 等待用户操作...")
    print()
    
    # 等待服务器启动
    time.sleep(3)
    
    try:
        # 创建会话
        session = requests.Session()
        
        # 监控页面访问
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📄 检查页面访问...")
        page_response = session.get('http://localhost:8000/tools/pdf_converter/', timeout=10)
        if page_response.status_code == 200:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 页面访问正常")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 页面访问失败: {page_response.status_code}")
            return
        
        # 获取CSRF token
        csrf_token = session.cookies.get('csrftoken')
        if not csrf_token:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 无法获取CSRF token")
            return
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ CSRF token获取成功")
        
        print()
        print("🎯 现在请按照以下步骤操作:")
        print("1. 访问 http://localhost:8000/tools/pdf_converter/")
        print("2. 点击 'PDF转Word' 卡片")
        print("3. 上传一个PDF文件")
        print("4. 点击 '开始转换' 按钮")
        print()
        print("🔍 监控器将实时显示操作结果...")
        print()
        
        # 持续监控API请求
        while True:
            try:
                # 检查API端点状态
                api_response = session.get('http://localhost:8000/tools/api/pdf-converter/', timeout=5)
                if api_response.status_code == 405:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ API端点正常 (405是预期的，因为只支持POST)")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ API端点异常: {api_response.status_code}")
                
                time.sleep(2)
                
            except KeyboardInterrupt:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🛑 监控已停止")
                break
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 监控错误: {e}")
                time.sleep(5)
                
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 监控启动失败: {e}")

def test_simple_conversion():
    """测试简单转换"""
    print("🧪 执行简单转换测试...")
    
    try:
        session = requests.Session()
        
        # 访问页面获取CSRF token
        page_response = session.get('http://localhost:8000/tools/pdf_converter/', timeout=10)
        csrf_token = session.cookies.get('csrftoken')
        
        if not csrf_token:
            print("❌ 无法获取CSRF token")
            return False
        
        # 创建测试PDF文件
        test_pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF'
        
        # 发送转换请求
        files = {
            'file': ('test.pdf', test_pdf_content, 'application/pdf')
        }
        
        form_data = {
            'type': 'pdf-to-word',
            'csrfmiddlewaretoken': csrf_token
        }
        
        headers = {
            'Referer': 'http://localhost:8000/tools/pdf_converter/',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json, text/plain, */*'
        }
        
        print("📤 发送转换请求...")
        api_response = session.post(
            'http://localhost:8000/tools/api/pdf-converter/',
            data=form_data,
            files=files,
            headers=headers,
            timeout=30
        )
        
        print(f"📥 响应状态码: {api_response.status_code}")
        
        if api_response.status_code == 200:
            try:
                response_json = api_response.json()
                if response_json.get('success'):
                    print("✅ 转换成功")
                    print(f"📄 下载链接: {response_json.get('download_url', 'N/A')}")
                    return True
                else:
                    print(f"❌ 转换失败: {response_json.get('error', '未知错误')}")
                    return False
            except Exception as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"📄 响应内容: {api_response.text[:200]}")
                return False
        else:
            print(f"❌ 请求失败: {api_response.status_code}")
            print(f"📄 响应内容: {api_response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PDF转换器监控工具")
    print("=" * 60)
    
    # 先执行简单测试
    print("🧪 执行基础功能测试...")
    test_result = test_simple_conversion()
    
    if test_result:
        print("✅ 基础功能正常，开始监控...")
        print()
        monitor_pdf_converter()
    else:
        print("❌ 基础功能有问题，请检查服务器状态")
