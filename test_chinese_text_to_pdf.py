#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试中文字符转PDF功能
"""

import os
import sys
import django

# 设置Django环境
sys.path.append('/Users/gaojie/PycharmProjects/QAToolBox')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.pdf_converter_api import PDFConverter

def test_chinese_text_to_pdf():
    """测试中文字符转PDF"""
    print("🔍 测试中文字符转PDF...")
    converter = PDFConverter()
    
    # 测试中文字符
    test_text = """这是一个测试文档

包含多种中文字符：
- 简体中文：你好世界
- 繁体中文：你好世界
- 数字：1234567890
- 英文：Hello World
- 混合：Hello 世界 123

特殊字符：
！@#￥%……&*（）——+{}|:"<>?[]\\;',./

段落测试：
这是第一个段落，包含一些中文内容。这是第一个段落，包含一些中文内容。

这是第二个段落，测试换行和格式。这是第二个段落，测试换行和格式。

这是第三个段落，包含更多内容。这是第三个段落，包含更多内容。

结束。"""
    
    try:
        success, result, file_type = converter.text_to_pdf(test_text)
        if success:
            print("✅ 中文字符转PDF成功")
            print(f"   生成PDF大小: {len(result)} bytes")
            
            # 保存PDF文件用于检查
            with open('test_chinese_output.pdf', 'wb') as f:
                f.write(result)
            print("   PDF文件已保存为: test_chinese_output.pdf")
            
            # 测试PDF转文本，验证内容是否正确
            from django.core.files.uploadedfile import SimpleUploadedFile
            pdf_file = SimpleUploadedFile("test_chinese.pdf", result, content_type="application/pdf")
            
            success2, result2, file_type2 = converter.pdf_to_text(pdf_file)
            if success2:
                print("✅ PDF转文本验证成功")
                print(f"   提取的文本长度: {len(result2)} 字符")
                print(f"   文本预览: {result2[:100]}...")
            else:
                print(f"❌ PDF转文本验证失败: {result2}")
                
            pdf_file.close()
            
        else:
            print(f"❌ 中文字符转PDF失败: {result}")
    except Exception as e:
        print(f"❌ 中文字符转PDF异常: {str(e)}")

def test_mixed_language_text():
    """测试混合语言文本"""
    print("🔍 测试混合语言文本...")
    converter = PDFConverter()
    
    test_text = """Mixed Language Test 混合语言测试

English: Hello World, this is a test document.
中文：你好世界，这是一个测试文档。
日本語：こんにちは世界、これはテスト文書です。
한국어: 안녕하세요 세계, 이것은 테스트 문서입니다.

Numbers: 1234567890
Symbols: !@#$%^&*()_+-=[]{}|;':",./<>?

Paragraph 1: This is the first paragraph with mixed content.
第一段：这是第一段，包含混合内容。

Paragraph 2: This is the second paragraph.
第二段：这是第二段。

End of document.
文档结束。"""
    
    try:
        success, result, file_type = converter.text_to_pdf(test_text)
        if success:
            print("✅ 混合语言文本转PDF成功")
            print(f"   生成PDF大小: {len(result)} bytes")
            
            # 保存PDF文件
            with open('test_mixed_language_output.pdf', 'wb') as f:
                f.write(result)
            print("   PDF文件已保存为: test_mixed_language_output.pdf")
            
        else:
            print(f"❌ 混合语言文本转PDF失败: {result}")
    except Exception as e:
        print(f"❌ 混合语言文本转PDF异常: {str(e)}")

def test_special_characters():
    """测试特殊字符"""
    print("🔍 测试特殊字符...")
    converter = PDFConverter()
    
    test_text = """特殊字符测试 Special Characters Test

中文标点符号：，。！？；：""''（）【】《》
English punctuation: ,.!?;:""''()[]<>

数学符号：±×÷=≠≤≥≈∞∑∏∫∂√
Math symbols: ±×÷=≠≤≥≈∞∑∏∫∂√

货币符号：¥$€£¢₽₹₩
Currency symbols: ¥$€£¢₽₹₩

表情符号：😀😃😄😁😆😅😂🤣
Emojis: 😀😃😄😁😆😅😂🤣

希腊字母：αβγδεζηθικλμνξοπρστυφχψω
Greek letters: αβγδεζηθικλμνξοπρστυφχψω

俄文字母：абвгдеёжзийклмнопрстуфхцчшщъыьэюя
Russian letters: абвгдеёжзийклмнопрстуфхцчшщъыьэюя

阿拉伯数字：٠١٢٣٤٥٦٧٨٩
Arabic numerals: ٠١٢٣٤٥٦٧٨٩

结束测试 End of test"""
    
    try:
        success, result, file_type = converter.text_to_pdf(test_text)
        if success:
            print("✅ 特殊字符转PDF成功")
            print(f"   生成PDF大小: {len(result)} bytes")
            
            # 保存PDF文件
            with open('test_special_chars_output.pdf', 'wb') as f:
                f.write(result)
            print("   PDF文件已保存为: test_special_chars_output.pdf")
            
        else:
            print(f"❌ 特殊字符转PDF失败: {result}")
    except Exception as e:
        print(f"❌ 特殊字符转PDF异常: {str(e)}")

def main():
    """主测试函数"""
    print("🚀 开始测试中文字符转PDF功能...")
    print("=" * 50)
    
    # 测试所有中文字符功能
    test_chinese_text_to_pdf()
    print()
    
    test_mixed_language_text()
    print()
    
    test_special_characters()
    print()
    
    print("=" * 50)
    print("🎉 中文字符测试完成！")
    print("请检查生成的PDF文件，确认中文字符显示正常。")

if __name__ == "__main__":
    main() 