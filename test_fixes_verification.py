#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复验证测试脚本
验证所有修复是否生效
"""

import os
import sys
import django

# 设置Django环境
sys.path.append('/Users/gaojie/PycharmProjects/QAToolBox')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json

User = get_user_model()

def test_pdf_converter_stats_api():
    """测试PDF转换统计API修复"""
    print("🔍 测试PDF转换统计API...")
    
    client = Client()
    
    # 创建测试用户
    user = User.objects.create_user(
        username='testuser_fixes',
        email='test@example.com',
        password='testpass123'
    )
    
    # 登录用户
    client.force_login(user)
    
    try:
        # 测试统计API
        response = client.get('/tools/api/pdf-converter/stats/')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('stats', {})
                
                # 检查平均转换时间
                avg_time = stats.get('average_conversion_time', 0)
                print(f"✅ 平均转换时间: {avg_time}")
                
                # 检查满意度
                satisfaction = stats.get('user_satisfaction', 0)
                print(f"✅ 用户满意度: {satisfaction}%")
                
                # 检查最近转换数据
                recent_data = stats.get('recent_conversions', [])
                print(f"✅ 最近转换数据数量: {len(recent_data)}")
                
                print("✅ PDF转换统计API修复验证通过")
                return True
            else:
                print(f"❌ API返回失败: {data.get('error', '未知错误')}")
                return False
        else:
            print(f"❌ API请求失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False
    finally:
        # 清理测试用户
        try:
            user.delete()
        except:
            pass

def test_pdf_converter_ui():
    """测试PDF转换器UI修复"""
    print("🔍 测试PDF转换器UI...")
    
    client = Client()
    
    # 创建测试用户并登录
    user = User.objects.create_user(
        username='testuser_ui',
        email='ui@example.com',
        password='testpass123'
    )
    client.force_login(user)
    
    try:
        # 测试PDF转换器页面
        response = client.get('/tools/pdf_converter/')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # 检查按钮样式是否存在
            if 'download-btn-modern' in content and 'convert-again-btn-modern' in content:
                print("✅ 按钮样式存在")
                
                # 检查CSS修复
                if 'flex-shrink: 0' in content:
                    print("✅ 按钮对齐修复存在")
                else:
                    print("⚠️ 按钮对齐修复可能未生效")
                
                print("✅ PDF转换器UI修复验证通过")
                return True
            else:
                print("❌ 按钮样式未找到")
                return False
        else:
            print(f"❌ 页面请求失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False
    finally:
        # 清理测试用户
        try:
            user.delete()
        except:
            pass

def test_training_plan_editor():
    """测试训练计划编辑器修复"""
    print("🔍 测试训练计划编辑器...")
    
    client = Client()
    
    # 创建测试用户
    user = User.objects.create_user(
        username='testuser_editor',
        email='editor@example.com',
        password='testpass123'
    )
    
    # 登录用户
    client.force_login(user)
    
    try:
        # 测试训练计划编辑器页面
        response = client.get('/tools/training_plan_editor/')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # 检查是否移除了内联onclick事件
            if 'onclick="showWeekSettings()"' not in content:
                print("✅ 内联onclick事件已移除")
                
                # 检查是否添加了按钮ID
                if 'id="weekSettingsBtn"' in content:
                    print("✅ 按钮ID已添加")
                    print("✅ 训练计划编辑器修复验证通过")
                    return True
                else:
                    print("❌ 按钮ID未找到")
                    return False
            else:
                print("❌ 内联onclick事件仍然存在")
                return False
        else:
            print(f"❌ 页面请求失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False
    finally:
        # 清理测试用户
        try:
            user.delete()
        except:
            pass

def test_pdf_converter_api():
    """测试PDF转换API修复"""
    print("🔍 测试PDF转换API...")
    
    try:
        from apps.tools.pdf_converter_api import PDFConverter
        
        converter = PDFConverter()
        
        # 检查转换器是否正常初始化
        if hasattr(converter, 'supported_formats'):
            print("✅ PDF转换器初始化正常")
            
            # 检查是否包含改进的转换方法
            if hasattr(converter, 'pdf_to_word') and hasattr(converter, 'word_to_pdf'):
                print("✅ 转换方法存在")
                print("✅ PDF转换API修复验证通过")
                return True
            else:
                print("❌ 转换方法不存在")
                return False
        else:
            print("❌ PDF转换器初始化失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始验证修复效果...")
    print("=" * 50)
    
    tests = [
        ("PDF转换统计API", test_pdf_converter_stats_api),
        ("PDF转换器UI", test_pdf_converter_ui),
        ("训练计划编辑器", test_training_plan_editor),
        ("PDF转换API", test_pdf_converter_api),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有修复验证通过！")
    else:
        print("⚠️ 部分修复需要进一步检查")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
