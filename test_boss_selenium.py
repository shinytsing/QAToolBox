#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boss直聘Selenium功能测试
测试嵌入式登录功能
"""

import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

from apps.tools.services.boss_zhipin_selenium import BossZhipinSeleniumService
from apps.tools.services.boss_zhipin_api import BossZhipinAPI
from apps.tools.services.job_search_service import JobSearchService

def print_separator():
    print("=" * 60)

def test_selenium_service():
    """测试Boss直聘Selenium服务"""
    print("🧪 测试Boss直聘Selenium服务")
    print_separator()
    
    service = BossZhipinSeleniumService(headless=True)
    
    # 测试用户ID
    test_user_id = 1
    
    # 1. 测试获取登录页面URL
    print("1. 测试获取登录页面URL...")
    try:
        result = service.get_login_page_url(test_user_id)
        if result['success']:
            print("✅ 登录页面URL获取成功")
            print(f"   URL: {result['login_url']}")
        else:
            print("❌ 登录页面URL获取失败")
            print(f"   错误: {result['message']}")
    except Exception as e:
        print(f"❌ 登录页面URL测试异常: {str(e)}")
    
    print()
    
    # 2. 测试登录状态检查
    print("2. 测试登录状态检查...")
    try:
        result = service.check_login_status(test_user_id)
        if result['success']:
            print("✅ 登录状态检查成功")
            print(f"   登录状态: {result['is_logged_in']}")
            print(f"   页面标题: {result['page_title']}")
            print(f"   当前URL: {result['current_url']}")
            if result.get('user_info'):
                print(f"   用户信息: {result['user_info']}")
        else:
            print("❌ 登录状态检查失败")
            print(f"   错误: {result['message']}")
    except Exception as e:
        print(f"❌ 登录状态检查失败: {str(e)}")
    
    print()
    
    # 3. 测试获取用户token
    print("3. 测试获取用户token...")
    try:
        result = service.get_user_token(test_user_id)
        if result['success'] and result['is_logged_in']:
            print("✅ 用户token获取成功")
            print(f"   Token信息: {len(result['token_info'])} 个字段")
            print(f"   Cookies数量: {len(result['cookies'])}")
            print(f"   LocalStorage字段: {len(result['local_storage'])}")
        else:
            print("❌ 用户token获取失败")
            print(f"   错误: {result['message']}")
    except Exception as e:
        print(f"❌ 用户token获取失败: {str(e)}")

def test_boss_api():
    """测试带Selenium的Boss直聘API"""
    print("\n🧪 测试带Selenium的Boss直聘API")
    print_separator()
    
    api = BossZhipinAPI(use_selenium=True)
    test_user_id = 1
    
    # 1. 测试获取登录页面URL
    print("1. 测试获取登录页面URL...")
    try:
        result = api.get_login_page_url(test_user_id)
        if result['success']:
            print("✅ 登录页面URL获取成功")
            print(f"   URL: {result['login_url']}")
        else:
            print("❌ 登录页面URL获取失败")
            print(f"   错误: {result['message']}")
    except Exception as e:
        print(f"❌ 登录页面URL测试异常: {str(e)}")
    
    print()
    
    # 2. 测试登录状态检查
    print("2. 测试登录状态检查...")
    try:
        result = api.check_login_status_with_selenium(test_user_id)
        if result['success']:
            print("✅ 登录状态检查成功")
            print(f"   登录状态: {result['is_logged_in']}")
            print(f"   页面标题: {result['page_title']}")
            print(f"   当前URL: {result['current_url']}")
        else:
            print("❌ 登录状态检查失败")
            print(f"   错误: {result['message']}")
    except Exception as e:
        print(f"❌ 登录状态检查失败: {str(e)}")
    
    print()
    
    # 3. 测试获取用户token
    print("3. 测试获取用户token...")
    try:
        result = api.get_user_token_with_selenium(test_user_id)
        if result['success'] and result['is_logged_in']:
            print("✅ 用户token获取成功")
            print(f"   Token信息: {len(result['token_info'])} 个字段")
        else:
            print("❌ 用户token获取失败")
            print(f"   错误: {result['message']}")
    except Exception as e:
        print(f"❌ 用户token获取失败: {str(e)}")

def test_job_service():
    """测试求职服务"""
    print("\n🧪 测试求职服务")
    print_separator()
    
    service = JobSearchService(use_selenium=True)
    test_user_id = 1
    
    # 1. 测试获取登录页面URL
    print("1. 测试获取登录页面URL...")
    try:
        result = service.get_login_page_url(test_user_id)
        if result['success']:
            print("✅ 登录页面URL获取成功")
            print(f"   URL: {result['login_url']}")
        else:
            print("❌ 登录页面URL获取失败")
            print(f"   错误: {result['message']}")
    except Exception as e:
        print(f"❌ 登录页面URL测试异常: {str(e)}")
    
    print()
    
    # 2. 测试登录状态检查
    print("2. 测试登录状态检查...")
    try:
        result = service.check_login_status_with_selenium(test_user_id)
        if result['success']:
            print("✅ 登录状态检查成功")
            print(f"   登录状态: {result['is_logged_in']}")
            print(f"   页面标题: {result['page_title']}")
            print(f"   当前URL: {result['current_url']}")
        else:
            print("❌ 登录状态检查失败")
            print(f"   错误: {result['message']}")
    except Exception as e:
        print(f"❌ 登录状态检查失败: {str(e)}")
    
    print()
    
    # 3. 测试获取用户token
    print("3. 测试获取用户token...")
    try:
        result = service.get_user_token_with_selenium(test_user_id)
        if result['success'] and result['is_logged_in']:
            print("✅ 用户token获取成功")
            print(f"   Token信息: {len(result['token_info'])} 个字段")
        else:
            print("❌ 用户token获取失败")
            print(f"   错误: {result['message']}")
    except Exception as e:
        print(f"❌ 用户token获取失败: {str(e)}")

def performance_test():
    """性能测试"""
    print("\n🧪 性能测试")
    print_separator()
    
    service = JobSearchService(use_selenium=True)
    test_user_id = 1
    
    # 1. 测试登录页面URL获取响应时间
    print("1. 测试登录页面URL获取响应时间...")
    try:
        start_time = time.time()
        result = service.get_login_page_url(test_user_id)
        end_time = time.time()
        
        if result['success']:
            print(f"✅ 登录页面URL获取成功，响应时间: {end_time - start_time:.2f}秒")
        else:
            print(f"❌ 登录页面URL获取失败，响应时间: {end_time - start_time:.2f}秒")
            print(f"   错误: {result['message']}")
    except Exception as e:
        print(f"❌ 登录页面URL获取异常，响应时间: {time.time() - start_time:.2f}秒: {str(e)}")
    
    print()
    
    # 2. 测试登录状态检查响应时间
    print("2. 测试登录状态检查响应时间...")
    try:
        start_time = time.time()
        result = service.check_login_status_with_selenium(test_user_id)
        end_time = time.time()
        
        if result['success']:
            print(f"✅ 登录状态检查成功，响应时间: {end_time - start_time:.2f}秒")
        else:
            print(f"❌ 登录状态检查失败，响应时间: {end_time - start_time:.2f}秒")
            print(f"   错误: {result['message']}")
    except Exception as e:
        print(f"❌ 登录状态检查异常，响应时间: {time.time() - start_time:.2f}秒: {str(e)}")

def main():
    """主测试函数"""
    print("🚀 Boss直聘嵌入式登录功能测试开始")
    print_separator()
    
    try:
        # 测试Selenium服务
        test_selenium_service()
        
        # 测试Boss API
        test_boss_api()
        
        # 测试求职服务
        test_job_service()
        
        # 性能测试
        performance_test()
        
        print("\n🎉 所有测试完成！")
        print_separator()
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 