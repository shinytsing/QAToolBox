#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复PDF下载问题
"""

import requests
import json

def test_pdf_conversion_api():
    """测试PDF转换API，检查返回的download_url"""
    url = 'http://localhost:8000/tools/api/pdf-converter/'
    
    # 测试文本转PDF
    data = {
        'type': 'text-to-pdf',
        'text_content': '这是一个测试文本，用于检查download_url是否正确返回。'
    }
    
    try:
        print("🧪 测试PDF转换API...")
        response = requests.post(url, data=data, timeout=30)
        
        print(f"状态码: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ API响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                if result.get('success'):
                    download_url = result.get('download_url')
                    if download_url:
                        print(f"✅ download_url存在: {download_url}")
                        
                        # 测试下载链接
                        download_response = requests.get(f"http://localhost:8000{download_url}", timeout=30)
                        if download_response.status_code == 200:
                            print(f"✅ 下载链接正常，文件大小: {len(download_response.content)} 字节")
                            return True
                        else:
                            print(f"❌ 下载链接失败: {download_response.status_code}")
                            return False
                    else:
                        print("❌ download_url不存在或为空")
                        return False
                else:
                    print(f"❌ 转换失败: {result.get('error')}")
                    return False
            except Exception as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"响应内容: {response.text[:200]}")
                return False
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def check_api_response_structure():
    """检查API响应结构"""
    print("\n🔍 检查API响应结构...")
    
    # 模拟一个成功的API响应
    expected_response = {
        'success': True,
        'type': 'file',
        'download_url': '/tools/api/pdf-converter/download/test_file.pdf/',
        'filename': 'test_file.pdf',
        'original_filename': 'test.txt',
        'conversion_type': 'text-to-pdf'
    }
    
    print("期望的API响应结构:")
    print(json.dumps(expected_response, indent=2, ensure_ascii=False))
    
    # 检查前端代码期望的字段
    required_fields = ['success', 'download_url', 'filename', 'conversion_type']
    
    print(f"\n前端代码期望的字段: {required_fields}")
    
    for field in required_fields:
        if field in expected_response:
            print(f"✅ {field}: {expected_response[field]}")
        else:
            print(f"❌ {field}: 缺失")

def create_debug_script():
    """创建调试脚本"""
    debug_script = """
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
"""
    
    with open('debug_pdf_conversion.js', 'w', encoding='utf-8') as f:
        f.write(debug_script)
    
    print("✅ 调试脚本已创建: debug_pdf_conversion.js")
    print("在浏览器控制台中运行: debugPDFConversion()")

def main():
    """主函数"""
    print("🔧 PDF下载问题诊断和修复")
    print("=" * 50)
    
    # 1. 检查API响应结构
    check_api_response_structure()
    
    # 2. 测试API
    print("\n" + "=" * 50)
    api_success = test_pdf_conversion_api()
    
    # 3. 创建调试脚本
    print("\n" + "=" * 50)
    create_debug_script()
    
    # 4. 提供修复建议
    print("\n" + "=" * 50)
    print("📋 修复建议:")
    
    if api_success:
        print("✅ API工作正常，问题可能在前端代码")
        print("建议:")
        print("1. 在浏览器控制台中运行 debugPDFConversion()")
        print("2. 检查 showConversionResult 函数中的 data.download_url")
        print("3. 确保API响应包含所有必需字段")
    else:
        print("❌ API存在问题，需要检查后端代码")
        print("建议:")
        print("1. 检查PDF转换API的响应格式")
        print("2. 确保所有转换类型都正确设置 download_url")
        print("3. 检查文件保存和下载路径")
    
    print("\n🎯 下一步操作:")
    print("1. 在浏览器中打开开发者工具")
    print("2. 在控制台中运行: debugPDFConversion()")
    print("3. 查看API响应的具体内容")
    print("4. 根据调试结果进行相应修复")

if __name__ == "__main__":
    main()
