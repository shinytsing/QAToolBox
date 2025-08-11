#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单PDF转换测试
"""

import os
import sys
import requests
import tempfile
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def create_simple_test_pdf():
    """创建简单的测试PDF"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # 创建临时PDF文件
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_pdf_path = temp_file.name
        
        # 创建PDF内容
        c = canvas.Canvas(temp_pdf_path, pagesize=letter)
        c.drawString(100, 750, "Test PDF")
        c.drawString(100, 720, "This is a test PDF for conversion.")
        c.save()
        
        return temp_pdf_path
    except Exception as e:
        print(f"创建PDF失败: {e}")
        return None

def test_text_to_pdf():
    """测试文本转PDF"""
    url = 'http://localhost:8000/tools/api/pdf-converter/'
    
    data = {
        'type': 'text-to-pdf',
        'text_content': 'This is a test text for PDF conversion.'
    }
    
    try:
        print("🧪 测试文本转PDF...")
        response = requests.post(url, data=data, timeout=30)
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"JSON响应: {result}")
                
                if result.get('success'):
                    print("✅ 文本转PDF成功!")
                    download_url = result.get('download_url')
                    if download_url:
                        print(f"下载链接: {download_url}")
                        
                        # 测试下载
                        download_response = requests.get(f"http://localhost:8000{download_url}", timeout=30)
                        if download_response.status_code == 200:
                            print(f"✅ 下载成功! 文件大小: {len(download_response.content)} 字节")
                            return True
                        else:
                            print(f"❌ 下载失败: {download_response.status_code}")
                            return False
                    else:
                        print("⚠️ 没有下载链接")
                        return True
                else:
                    print(f"❌ 转换失败: {result.get('error')}")
                    return False
            except Exception as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"响应内容: {response.text[:200]}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_pdf_to_text():
    """测试PDF转文本"""
    # 创建测试PDF
    pdf_path = create_simple_test_pdf()
    if not pdf_path:
        return False
    
    url = 'http://localhost:8000/tools/api/pdf-converter/'
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': ('test.pdf', f.read())}
        
        data = {'type': 'pdf-to-text'}
        
        print("🧪 测试PDF转文本...")
        response = requests.post(url, data=data, files=files, timeout=30)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"JSON响应: {result}")
                
                if result.get('success'):
                    print("✅ PDF转文本成功!")
                    download_url = result.get('download_url')
                    if download_url:
                        print(f"下载链接: {download_url}")
                        
                        # 测试下载
                        download_response = requests.get(f"http://localhost:8000{download_url}", timeout=30)
                        if download_response.status_code == 200:
                            print(f"✅ 下载成功! 文件大小: {len(download_response.content)} 字节")
                            print(f"文本内容: {download_response.text[:100]}")
                            return True
                        else:
                            print(f"❌ 下载失败: {download_response.status_code}")
                            return False
                    else:
                        print("⚠️ 没有下载链接")
                        return True
                else:
                    print(f"❌ 转换失败: {result.get('error')}")
                    return False
            except Exception as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"响应内容: {response.text[:200]}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    finally:
        # 清理临时文件
        if pdf_path and os.path.exists(pdf_path):
            try:
                os.unlink(pdf_path)
            except:
                pass

if __name__ == "__main__":
    print("🚀 简单PDF转换测试")
    print("=" * 40)
    
    # 测试文本转PDF
    print("\n1️⃣ 测试文本转PDF")
    text_to_pdf_success = test_text_to_pdf()
    
    # 测试PDF转文本
    print("\n2️⃣ 测试PDF转文本")
    pdf_to_text_success = test_pdf_to_text()
    
    # 总结
    print("\n" + "=" * 40)
    print("📊 测试结果")
    print("=" * 40)
    print(f"文本转PDF: {'✅ 成功' if text_to_pdf_success else '❌ 失败'}")
    print(f"PDF转文本: {'✅ 成功' if pdf_to_text_success else '❌ 失败'}")
    
    if text_to_pdf_success and pdf_to_text_success:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️ 部分测试失败")
