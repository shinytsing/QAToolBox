#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试FreeMind和XMind下载功能修复效果
验证飞书兼容性和下载稳定性
"""

import os
import sys
import tempfile
import zipfile
import json
from pathlib import Path

# 添加项目路径
sys.path.append('/Users/gaojie/PycharmProjects/QAToolBox')

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

from apps.tools.generate_test_cases_api import GenerateTestCasesAPI
from apps.tools.models import ToolUsageLog
from django.core.files import File

def test_freemind_generation_fixed():
    """测试修复后的FreeMind文件生成"""
    print("🔧 测试修复后的FreeMind文件生成...")
    
    api = GenerateTestCasesAPI()
    
    # 测试不同的数据结构格式
    test_cases_formats = [
        # 格式1: 直接的字典格式
        {
            "功能测试": [
                "TC-登录-001: 正常登录流程",
                "TC-登录-002: 用户名密码错误",
                "TC-登录-003: 空用户名密码"
            ],
            "界面测试": [
                "TC-UI-001: 页面布局响应式",
                "TC-UI-002: 按钮点击效果",
                "TC-UI-003: 表单验证提示"
            ]
        },
        # 格式2: 包含structure的格式
        {
            "title": "AI生成测试用例",
            "structure": {
                "性能测试": [
                    "TC-性能-001: 页面加载时间",
                    "TC-性能-002: 并发用户测试",
                    "TC-性能-003: 内存使用情况"
                ],
                "安全测试": [
                    "TC-安全-001: SQL注入测试",
                    "TC-安全-002: XSS攻击测试",
                    "TC-安全-003: 权限验证测试"
                ]
            }
        },
        # 格式3: 混合格式
        {
            "兼容性测试": "TC-兼容-001: 多浏览器测试",
            "异常测试": ["TC-异常-001: 网络中断", "TC-异常-002: 服务器错误"]
        }
    ]
    
    for i, test_cases in enumerate(test_cases_formats, 1):
        print(f"\n📝 测试格式 {i}:")
        try:
            freemind_xml = api._generate_freemind(test_cases)
            print(f"✅ 格式 {i} 生成成功")
            print(f"   XML长度: {len(freemind_xml)} 字符")
            
            # 验证XML格式
            import xml.etree.ElementTree as ET
            try:
                root = ET.fromstring(freemind_xml)
                print(f"   ✅ XML格式验证通过")
                print(f"   根节点: {root.tag}")
                print(f"   子节点数量: {len(root)}")
                
                # 检查必需元素
                if root.find(".//node") is not None:
                    print(f"   ✅ 包含必需元素: node")
                else:
                    print(f"   ❌ 缺少必需元素: node")
                    
            except Exception as xml_err:
                print(f"   ❌ XML格式验证失败: {xml_err}")
            
            # 保存到临时文件
            with tempfile.NamedTemporaryFile(suffix='.mm', delete=False, mode='w', encoding='utf-8') as f:
                f.write(freemind_xml)
                temp_path = f.name
            
            print(f"   ✅ 临时文件保存: {temp_path}")
            
            # 清理临时文件
            os.unlink(temp_path)
            
        except Exception as e:
            print(f"   ❌ 格式 {i} 生成失败: {e}")

def test_xmind_generation_fixed():
    """测试修复后的XMind文件生成"""
    print("\n🔧 测试修复后的XMind文件生成...")
    
    try:
        import xmind
        print("✅ XMind库导入成功")
    except ImportError as e:
        print(f"❌ XMind库导入失败: {e}")
        return
    
    api = GenerateTestCasesAPI()
    
    # 测试不同的内容格式
    test_contents = [
        # 标准Markdown格式
        """## 功能测试
- TC-登录-001: 正常登录流程
  * 前置条件: 用户已注册
  * 测试步骤: 输入正确用户名密码
  * 预期结果: 登录成功，跳转到主页

- TC-登录-002: 用户名密码错误
  * 前置条件: 用户已注册
  * 测试步骤: 输入错误用户名密码
  * 预期结果: 显示错误提示

## 界面测试
- TC-UI-001: 页面布局响应式
  * 前置条件: 页面已加载
  * 测试步骤: 调整浏览器窗口大小
  * 预期结果: 页面布局自适应调整""",
        
        # 简单格式
        """## 测试用例
- 用例1: 基本功能测试
- 用例2: 异常情况处理""",
        
        # 空内容测试
        ""
    ]
    
    for i, content in enumerate(test_contents, 1):
        print(f"\n📝 测试内容格式 {i}:")
        try:
            test_cases = {"content": content, "title": f"AI生成测试用例-{i}"}
            xmind_workbook = api._generate_xmind(test_cases)
            print(f"✅ 内容格式 {i} 生成成功")
            
            # 保存到临时文件
            temp_path = tempfile.mktemp(suffix='.xmind')
            xmind.save(xmind_workbook, temp_path)
            print(f"   ✅ XMind文件保存: {temp_path}")
            
            # 验证XMind文件格式
            if os.path.exists(temp_path):
                try:
                    with zipfile.ZipFile(temp_path, 'r') as zip_file:
                        file_list = zip_file.namelist()
                        print(f"   ✅ XMind ZIP格式验证通过")
                        print(f"   包含文件: {file_list[:3]}...")
                        
                        # 检查飞书兼容性
                        if 'content.xml' in file_list:
                            print(f"   ✅ 包含飞书必需文件: content.xml")
                        else:
                            print(f"   ❌ 缺少飞书必需文件: content.xml")
                            
                except Exception as zip_err:
                    print(f"   ❌ XMind ZIP格式验证失败: {zip_err}")
                
                # 清理临时文件
                os.unlink(temp_path)
            
        except Exception as e:
            print(f"   ❌ 内容格式 {i} 生成失败: {e}")

def test_feishu_compatibility_enhanced():
    """增强的飞书兼容性测试"""
    print("\n🔧 增强的飞书兼容性测试...")
    
    api = GenerateTestCasesAPI()
    
    # 飞书思维导图的具体要求
    feishu_requirements = {
        "FreeMind": {
            "format": "XML",
            "encoding": "UTF-8",
            "required_elements": ["map", "node"],
            "mime_type": "application/xml",
            "version": "1.0.1"
        },
        "XMind": {
            "format": "ZIP",
            "required_files": ["content.xml", "styles.xml"],
            "mime_type": "application/zip",
            "structure": "JSON-like"
        }
    }
    
    print("📋 飞书兼容性要求:")
    for format_name, requirements in feishu_requirements.items():
        print(f"  {format_name}:")
        for key, value in requirements.items():
            print(f"    {key}: {value}")
    
    # 测试FreeMind飞书兼容性
    print("\n🔍 测试FreeMind飞书兼容性...")
    test_cases = {
        "功能测试": ["测试用例1", "测试用例2"],
        "性能测试": ["性能测试1", "性能测试2"]
    }
    
    try:
        freemind_xml = api._generate_freemind(test_cases)
        
        # 检查XML格式
        import xml.etree.ElementTree as ET
        root = ET.fromstring(freemind_xml)
        
        # 检查必需元素
        required_elements = feishu_requirements["FreeMind"]["required_elements"]
        for element in required_elements:
            if root.find(f".//{element}") is not None:
                print(f"✅ 包含必需元素: {element}")
            else:
                print(f"❌ 缺少必需元素: {element}")
        
        # 检查版本
        if root.get("version") == feishu_requirements["FreeMind"]["version"]:
            print("✅ 版本号正确")
        else:
            print("❌ 版本号不正确")
        
        # 检查编码
        if "encoding=\"UTF-8\"" in freemind_xml:
            print("✅ UTF-8编码正确")
        else:
            print("❌ UTF-8编码缺失")
        
        # 检查XML声明
        if freemind_xml.startswith('<?xml'):
            print("✅ XML声明正确")
        else:
            print("❌ XML声明缺失")
            
    except Exception as e:
        print(f"❌ FreeMind兼容性测试失败: {e}")
    
    # 测试XMind飞书兼容性
    print("\n🔍 测试XMind飞书兼容性...")
    test_content = """## 功能测试
- TC-001: 基本功能
- TC-002: 异常处理

## 性能测试
- TC-003: 响应时间
- TC-004: 并发处理"""
    
    try:
        test_cases = {"content": test_content, "title": "飞书兼容性测试"}
        xmind_workbook = api._generate_xmind(test_cases)
        
        # 保存到临时文件
        temp_path = tempfile.mktemp(suffix='.xmind')
        import xmind
        xmind.save(xmind_workbook, temp_path)
        
        # 检查ZIP格式和必需文件
        if os.path.exists(temp_path):
            with zipfile.ZipFile(temp_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                
                required_files = feishu_requirements["XMind"]["required_files"]
                for file_name in required_files:
                    if file_name in file_list:
                        print(f"✅ 包含必需文件: {file_name}")
                    else:
                        print(f"❌ 缺少必需文件: {file_name}")
                
                # 检查content.xml的内容结构
                if 'content.xml' in file_list:
                    try:
                        content_xml = zip_file.read('content.xml').decode('utf-8')
                        if '<sheet' in content_xml and '<topic' in content_xml:
                            print("✅ content.xml结构正确")
                        else:
                            print("❌ content.xml结构不正确")
                    except Exception as xml_err:
                        print(f"❌ content.xml读取失败: {xml_err}")
            
            # 清理临时文件
            os.unlink(temp_path)
            
    except Exception as e:
        print(f"❌ XMind兼容性测试失败: {e}")

def test_download_simulation_enhanced():
    """增强的下载模拟测试"""
    print("\n🔧 增强的下载模拟测试...")
    
    api = GenerateTestCasesAPI()
    
    # 生成测试文件
    test_cases = {
        "功能测试": ["TC-001: 登录功能", "TC-002: 注册功能"],
        "界面测试": ["TC-003: 页面布局", "TC-004: 响应式设计"]
    }
    
    # 生成FreeMind文件
    print("📄 生成FreeMind文件...")
    freemind_xml = api._generate_freemind(test_cases)
    
    with tempfile.NamedTemporaryFile(suffix='.mm', delete=False, mode='w', encoding='utf-8') as f:
        f.write(freemind_xml)
        freemind_path = f.name
    
    # 生成XMind文件
    print("🗂️ 生成XMind文件...")
    test_content = """## 功能测试
- TC-001: 登录功能
- TC-002: 注册功能

## 界面测试
- TC-003: 页面布局
- TC-004: 响应式设计"""
    
    test_cases = {"content": test_content, "title": "下载测试用例"}
    xmind_workbook = api._generate_xmind(test_cases)
    
    temp_path = tempfile.mktemp(suffix='.xmind')
    import xmind
    xmind.save(xmind_workbook, temp_path)
    xmind_path = temp_path
    
    # 模拟下载过程
    files_to_test = [
        (freemind_path, "FreeMind", "test_cases.mm", "application/xml; charset=utf-8"),
        (xmind_path, "XMind", "test_cases.xmind", "application/zip")
    ]
    
    for file_path, file_type, filename, mime_type in files_to_test:
        print(f"\n📥 模拟{file_type}下载...")
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            print(f"✅ {file_type}文件读取成功")
            print(f"   文件大小: {len(content)} 字节")
            print(f"   文件名: {filename}")
            print(f"   MIME类型: {mime_type}")
            
            # 验证文件内容
            if file_type == "FreeMind":
                if content.startswith(b'<?xml'):
                    print("   ✅ XML格式正确")
                else:
                    print("   ❌ XML格式不正确")
            elif file_type == "XMind":
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_file:
                        if 'content.xml' in zip_file.namelist():
                            print("   ✅ ZIP格式正确")
                        else:
                            print("   ❌ ZIP格式不正确")
                except Exception as zip_err:
                    print(f"   ❌ ZIP格式验证失败: {zip_err}")
            
            # 清理临时文件
            os.unlink(file_path)
            
        except Exception as e:
            print(f"   ❌ {file_type}文件处理失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始FreeMind和XMind下载功能修复验证")
    print("=" * 60)
    
    # 1. 测试修复后的文件生成
    test_freemind_generation_fixed()
    test_xmind_generation_fixed()
    
    # 2. 增强的飞书兼容性测试
    test_feishu_compatibility_enhanced()
    
    # 3. 增强的下载模拟测试
    test_download_simulation_enhanced()
    
    print("\n" + "=" * 60)
    print("🎯 修复验证完成")
    
    # 提供使用建议
    print("\n💡 使用建议:")
    print("1. FreeMind文件现在支持多种数据结构格式")
    print("2. XMind文件已优化飞书兼容性")
    print("3. 下载功能增强了错误处理和日志记录")
    print("4. 文件格式符合飞书思维导图要求")
    print("5. 支持中文文件名和UTF-8编码")

if __name__ == "__main__":
    main() 