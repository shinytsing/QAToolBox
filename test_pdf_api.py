#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF转换API测试脚本
验证Django环境中的PDF转换功能
"""

import os
import sys
import tempfile
import requests
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

def test_pdf_converter_direct():
    """直接测试PDF转换器类"""
    print("🧪 直接测试PDF转换器...")
    
    try:
        import django
        django.setup()
        
        from apps.tools.pdf_converter_api import PDFConverter, PDF2DOCX_AVAILABLE
        
        print(f"✅ PDF转换器导入成功")
        print(f"   pdf2docx可用性: {PDF2DOCX_AVAILABLE}")
        
        if PDF2DOCX_AVAILABLE:
            print("✅ pdf2docx库在Django环境中可用")
            
            # 创建一个简单的测试PDF
            test_pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF'
            
            # 创建文件对象
            from io import BytesIO
            pdf_file = BytesIO(test_pdf_content)
            pdf_file.name = "test.pdf"
            
            # 测试转换
            converter = PDFConverter()
            success, result, file_type = converter.pdf_to_word(pdf_file)
            
            if success:
                print("✅ PDF转Word转换成功!")
                print(f"   输出类型: {file_type}")
                print(f"   输出大小: {len(result)} 字节")
            else:
                print(f"❌ PDF转Word转换失败: {result}")
        else:
            print("❌ pdf2docx库在Django环境中不可用")
            
    except Exception as e:
        print(f"❌ 直接测试失败: {e}")

def test_pdf_converter_api():
    """测试PDF转换API端点"""
    print("\n🧪 测试PDF转换API端点...")
    
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
            data = {'type': 'pdf-to-word'}
            
            # 发送请求到API
            response = requests.post('http://localhost:8000/tools/api/pdf-converter/', 
                                   files=files, data=data, timeout=30)
            
            print(f"API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ PDF转换API测试成功!")
                    print(f"   下载链接: {result.get('download_url', 'N/A')}")
                else:
                    print(f"❌ PDF转换API返回错误: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ API请求失败: {response.status_code}")
                print(f"   响应内容: {response.text[:200]}")
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
                
    except Exception as e:
        print(f"❌ API测试失败: {e}")

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
        
        # 检查全局变量
        from apps.tools.pdf_converter_api import PDF2DOCX_AVAILABLE, DOCX2PDF_AVAILABLE
        print(f"✅ pdf2docx可用性: {PDF2DOCX_AVAILABLE}")
        print(f"✅ docx2pdf可用性: {DOCX2PDF_AVAILABLE}")
        
    except Exception as e:
        print(f"❌ Django环境检查失败: {e}")

def main():
    """主函数"""
    print("🔍 PDF转换API测试")
    print("=" * 50)
    
    # 检查Django环境
    check_django_environment()
    
    # 直接测试PDF转换器
    test_pdf_converter_direct()
    
    # 测试API端点
    test_pdf_converter_api()
    
    print("\n✅ 测试完成！")
    print("如果所有测试都通过，PDF转换功能应该可以正常使用。")

if __name__ == "__main__":
    main() 