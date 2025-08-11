#!/usr/bin/env python3
"""
测试旅游攻略PDF导出功能
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.tools.models import TravelGuide

User = get_user_model()

def test_pdf_export():
    """测试PDF导出功能"""
    print("🧪 测试PDF导出功能...")
    try:
        # 创建Django测试客户端
        client = Client()
        
        # 登录
        login_success = client.login(username='testuser_travel', password='testpass123')
        if not login_success:
            print("❌ 用户登录失败")
            return False
        
        print("✅ 用户登录成功")
        
        # 获取最新的攻略
        latest_guide = TravelGuide.objects.filter(user__username='testuser_travel').order_by('-created_at').first()
        
        if not latest_guide:
            print("❌ 没有找到旅游攻略")
            return False
        
        print(f"✅ 找到攻略: {latest_guide.destination} (ID: {latest_guide.id})")
        
        # 测试PDF导出API
        url = f'/tools/api/travel-guide/{latest_guide.id}/export/'
        
        response = client.post(url)
        
        print(f"📊 PDF导出响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 检查响应类型
            content_type = response.get('Content-Type', '')
            if 'application/pdf' in content_type:
                print("✅ PDF导出成功！")
                print(f"📄 响应类型: {content_type}")
                print(f"📊 文件大小: {len(response.content)} bytes")
                print(f"📄 文件名: {response.get('Content-Disposition', '未知')}")
                return True
            else:
                # 尝试解析JSON响应
                try:
                    result = response.json()
                    if result.get('success'):
                        print("✅ PDF导出成功！")
                        print(f"📄 PDF文件路径: {result.get('pdf_path')}")
                        print(f"📊 文件大小: {result.get('file_size', '未知')} bytes")
                        return True
                    else:
                        print(f"❌ PDF导出失败: {result.get('error')}")
                        return False
                except:
                    print(f"❌ 无法解析响应内容")
                    return False
        else:
            print(f"❌ PDF导出请求失败: {response.status_code}")
            print(f"📄 响应内容: {response.content.decode()[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ PDF导出测试失败: {e}")
        return False

def test_pdf_export_with_invalid_id():
    """测试无效ID的PDF导出"""
    print("\n🧪 测试无效ID的PDF导出...")
    try:
        # 创建Django测试客户端
        client = Client()
        
        # 登录
        login_success = client.login(username='testuser_travel', password='testpass123')
        if not login_success:
            print("❌ 用户登录失败")
            return False
        
        # 测试不存在的攻略ID
        invalid_id = 99999
        url = f'/tools/api/travel-guide/{invalid_id}/export/'
        
        response = client.post(url)
        
        print(f"📊 无效ID响应状态码: {response.status_code}")
        
        if response.status_code == 404:
            result = response.json()
            print("✅ 正确处理了无效ID")
            print(f"📄 错误信息: {result.get('error')}")
            return True
        else:
            print(f"❌ 未正确处理无效ID: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 无效ID测试失败: {e}")
        return False

def test_pdf_export_without_login():
    """测试未登录的PDF导出"""
    print("\n🧪 测试未登录的PDF导出...")
    try:
        # 创建Django测试客户端（未登录）
        client = Client()
        
        # 测试未登录状态
        guide_id = 1
        url = f'/tools/api/travel-guide/{guide_id}/export/'
        
        response = client.post(url)
        
        print(f"📊 未登录响应状态码: {response.status_code}")
        
        if response.status_code == 302:  # 重定向到登录页面
            print("✅ 正确处理了未登录状态（重定向到登录页面）")
            return True
        else:
            print(f"❌ 未正确处理未登录状态: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 未登录测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试PDF导出功能...")
    print("=" * 60)
    
    # 测试正常PDF导出
    pdf_export_ok = test_pdf_export()
    
    # 测试无效ID
    invalid_id_ok = test_pdf_export_with_invalid_id()
    
    # 测试未登录状态
    no_login_ok = test_pdf_export_without_login()
    
    print("\n" + "=" * 60)
    print("📋 PDF导出测试总结:")
    
    if pdf_export_ok:
        print("✅ 正常PDF导出: 成功")
    else:
        print("❌ 正常PDF导出: 失败")
    
    if invalid_id_ok:
        print("✅ 无效ID处理: 成功")
    else:
        print("❌ 无效ID处理: 失败")
    
    if no_login_ok:
        print("✅ 未登录处理: 成功")
    else:
        print("❌ 未登录处理: 失败")
    
    print("\n💡 PDF导出功能说明:")
    print("1. 支持生成格式化的旅游攻略PDF")
    print("2. 包含完整的攻略信息（景点、美食、交通等）")
    print("3. 正确处理权限验证和错误情况")
    print("4. 提供文件下载链接")
    
    print("\n🎉 PDF导出测试完成！")

if __name__ == "__main__":
    main()
