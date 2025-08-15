#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试PDF转换器API，检查download_url字段
"""

import requests
import json
import os
import re

def get_csrf_token():
    """获取CSRF令牌"""
    session = requests.Session()
    response = session.get('http://localhost:8000/tools/pdf_converter_test/')
    
    # 从响应中提取CSRF令牌
    if 'csrf-token' in response.text:
        match = re.search(r'content="([^"]+)"', response.text)
        if match:
            return match.group(1)
    
    # 从cookies中获取
    csrf_token = session.cookies.get('csrftoken')
    return csrf_token

def test_pdf_conversion_api():
    """测试PDF转换API，检查返回的download_url"""
    url = 'http://localhost:8000/tools/api/pdf-converter-test/'
    
    # 创建会话
    session = requests.Session()
    
    # 获取CSRF令牌
    csrf_token = get_csrf_token()
    print(f"获取到CSRF令牌: {csrf_token}")
    
    # 测试PDF转Word
    print("🧪 测试PDF转Word转换...")
    
    # 创建一个简单的测试PDF文件
    test_pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF'
    
    # 保存测试PDF文件
    test_pdf_path = 'test_document.pdf'
    with open(test_pdf_path, 'wb') as f:
        f.write(test_pdf_content)
    
    try:
        with open(test_pdf_path, 'rb') as f:
            files = {'file': ('test_document.pdf', f.read(), 'application/pdf')}
            data = {'type': 'pdf-to-word'}
            
            # 添加CSRF令牌
            headers = {
                'X-CSRFToken': csrf_token,
                'Referer': 'http://localhost:8000/tools/pdf_converter_test/'
            }
            
            print(f"发送请求到: {url}")
            print(f"请求数据: {data}")
            print(f"请求头: {headers}")
            
            response = session.post(url, data=data, files=files, headers=headers, timeout=30)
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"✅ API响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    
                    if result.get('success'):
                        download_url = result.get('download_url')
                        if download_url:
                            print(f"✅ download_url存在: {download_url}")
                            
                            # 测试下载链接
                            download_response = session.get(f"http://localhost:8000{download_url}", timeout=30)
                            if download_response.status_code == 200:
                                print(f"✅ 下载链接正常，文件大小: {len(download_response.content)} 字节")
                                return True
                            else:
                                print(f"❌ 下载链接失败: {download_response.status_code}")
                                return False
                        else:
                            print("❌ download_url不存在或为空")
                            print(f"完整响应: {result}")
                            return False
                    else:
                        print(f"❌ 转换失败: {result.get('error')}")
                        return False
                except Exception as e:
                    print(f"❌ JSON解析失败: {e}")
                    print(f"响应内容: {response.text[:500]}")
                    return False
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"响应内容: {response.text[:500]}")
                return False
                
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False
    finally:
        # 清理测试文件
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)

def test_text_to_pdf():
    """测试文本转PDF"""
    url = 'http://localhost:8000/tools/api/pdf-converter-test/'
    
    # 创建会话
    session = requests.Session()
    
    # 获取CSRF令牌
    csrf_token = get_csrf_token()
    
    print("\n🧪 测试文本转PDF转换...")
    
    data = {
        'type': 'text-to-pdf',
        'text_content': '这是一个测试文本，用于检查download_url是否正确返回。'
    }
    
    # 添加CSRF令牌
    headers = {
        'X-CSRFToken': csrf_token,
        'Referer': 'http://localhost:8000/tools/pdf_converter_test/'
    }
    
    try:
        response = session.post(url, data=data, headers=headers, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('success'):
                download_url = result.get('download_url')
                if download_url:
                    print(f"✅ download_url存在: {download_url}")
                    return True
                else:
                    print("❌ download_url不存在或为空")
                    return False
            else:
                print(f"❌ 转换失败: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

if __name__ == '__main__':
    print("🔍 开始调试PDF转换器API...")
    
    # 测试文本转PDF
    text_result = test_text_to_pdf()
    
    # 测试PDF转Word
    pdf_result = test_pdf_conversion_api()
    
    print(f"\n📊 测试结果:")
    print(f"文本转PDF: {'✅ 成功' if text_result else '❌ 失败'}")
    print(f"PDF转Word: {'✅ 成功' if pdf_result else '❌ 失败'}")
    
    if not text_result or not pdf_result:
        print("\n⚠️ 发现问题，请检查API实现")
    else:
        print("\n✅ 所有测试通过")
