#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF转图片Web界面测试脚本
专门诊断PDF转图片功能在Web界面中的问题
"""

import os
import sys
import tempfile
import requests
import json
import io

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

def test_pdf_to_image_direct():
    """直接测试PDF转图片功能"""
    print("🧪 直接测试PDF转图片功能...")
    
    try:
        import django
        django.setup()
        
        from apps.tools.pdf_converter_api import PDFConverter
        
        # 创建一个简单的测试PDF
        test_pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF'
        
        # 创建文件对象
        pdf_file = io.BytesIO(test_pdf_content)
        pdf_file.name = "test.pdf"
        
        # 测试转换
        converter = PDFConverter()
        success, result, file_type = converter.pdf_to_images(pdf_file)
        
        if success:
            print("✅ PDF转图片直接测试成功!")
            print(f"   输出类型: {file_type}")
            print(f"   图片数量: {len(result)}")
            for i, img in enumerate(result):
                print(f"   图片{i+1}: {img['width']}x{img['height']}, 大小: {img['size']} 字节")
            return True
        else:
            print(f"❌ PDF转图片直接测试失败: {result}")
            return False
            
    except Exception as e:
        print(f"❌ PDF转图片直接测试异常: {e}")
        return False

def test_pdf_to_image_api():
    """测试PDF转图片API端点"""
    print("\n🧪 测试PDF转图片API端点...")
    
    try:
        # 创建一个简单的测试PDF
        test_pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF'
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf.write(test_pdf_content)
            temp_pdf_path = temp_pdf.name
        
        try:
            # 准备请求数据
            files = {'file': ('test.pdf', open(temp_pdf_path, 'rb'), 'application/pdf')}
            data = {'type': 'pdf-to-image'}
            
            # 发送请求到API
            response = requests.post('http://localhost:8000/tools/api/pdf-converter/', 
                                   files=files, data=data, timeout=30)
            
            print(f"API响应状态码: {response.status_code}")
            print(f"API响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"API响应JSON: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    
                    if result.get('success'):
                        print("✅ PDF转图片API测试成功!")
                        if result.get('type') == 'images':
                            print(f"   图片数量: {len(result.get('data', []))}")
                            print(f"   总大小: {result.get('total_size', 0)} 字节")
                        else:
                            print(f"   下载链接: {result.get('download_url', 'N/A')}")
                    else:
                        print(f"❌ PDF转图片API返回错误: {result.get('error', 'Unknown error')}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ API响应不是有效的JSON: {e}")
                    print(f"   响应内容: {response.text[:500]}")
                    
            else:
                print(f"❌ API请求失败: {response.status_code}")
                print(f"   响应内容: {response.text[:500]}")
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
                
    except Exception as e:
        print(f"❌ PDF转图片API测试失败: {e}")

def test_pdf_to_image_batch_api():
    """测试PDF转图片批量API端点"""
    print("\n🧪 测试PDF转图片批量API端点...")
    
    try:
        # 创建一个简单的测试PDF
        test_pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF'
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf.write(test_pdf_content)
            temp_pdf_path = temp_pdf.name
        
        try:
            # 准备请求数据
            files = [('files', ('test.pdf', open(temp_pdf_path, 'rb'), 'application/pdf'))]
            data = {'type': 'pdf-to-image'}
            
            # 发送请求到批量API
            response = requests.post('http://localhost:8000/tools/api/pdf-converter/batch/', 
                                   files=files, data=data, timeout=30)
            
            print(f"批量API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"批量API响应JSON: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    
                    if result.get('success'):
                        print("✅ PDF转图片批量API测试成功!")
                        results = result.get('results', [])
                        print(f"   处理文件数: {len(results)}")
                        for i, res in enumerate(results):
                            if res.get('success'):
                                print(f"   文件{i+1}: ✅ 成功")
                            else:
                                print(f"   文件{i+1}: ❌ 失败 - {res.get('error', 'Unknown error')}")
                    else:
                        print(f"❌ PDF转图片批量API返回错误: {result.get('error', 'Unknown error')}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ 批量API响应不是有效的JSON: {e}")
                    print(f"   响应内容: {response.text[:500]}")
                    
            else:
                print(f"❌ 批量API请求失败: {response.status_code}")
                print(f"   响应内容: {response.text[:500]}")
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
                
    except Exception as e:
        print(f"❌ PDF转图片批量API测试失败: {e}")

def check_django_environment():
    """检查Django环境"""
    print("🎯 检查Django环境...")
    
    try:
        import django
        from django.conf import settings
        
        print(f"✅ Django版本: {django.get_version()}")
        print(f"✅ 设置模块: {settings.SETTINGS_MODULE}")
        print(f"✅ 调试模式: {settings.DEBUG}")
        
        # 检查PDF转换器模块
        from apps.tools.pdf_converter_api import PDFConverter
        print("✅ PDF转换器模块导入成功")
        
        # 检查pdf转图片方法
        converter = PDFConverter()
        if hasattr(converter, 'pdf_to_images'):
            print("✅ pdf_to_images方法存在")
        else:
            print("❌ pdf_to_images方法不存在")
            
    except Exception as e:
        print(f"❌ Django环境检查失败: {e}")

def main():
    """主函数"""
    print("🔍 PDF转图片功能Web界面测试")
    print("=" * 60)
    
    # 检查Django环境
    check_django_environment()
    
    # 直接测试PDF转图片功能
    direct_success = test_pdf_to_image_direct()
    
    # 测试API端点
    test_pdf_to_image_api()
    
    # 测试批量API端点
    test_pdf_to_image_batch_api()
    
    # 输出测试结果总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    if direct_success:
        print("✅ 直接测试: PDF转图片功能正常")
        print("⚠️  Web API可能存在问题，请检查API响应")
    else:
        print("❌ 直接测试: PDF转图片功能异常")
        print("🔧 需要检查PDF转换器实现")
    
    print("\n✅ 测试完成！")

if __name__ == "__main__":
    main() 