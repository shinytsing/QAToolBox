#!/usr/bin/env python3
"""
调试简单日记页面的问题
"""

import os
import sys
import django

# 设置Django环境
sys.path.append('/Users/gaojie/PycharmProjects/QAToolBox')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from apps.tools.views.simple_diary_views import simple_diary_home
from apps.tools.models.diary_models import LifeDiaryEntry, DiaryAchievement

def test_view_function():
    """测试视图函数"""
    print("🧪 测试视图函数...")
    
    try:
        # 创建测试用户
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        
        # 创建请求
        factory = RequestFactory()
        request = factory.get('/tools/simple-diary/')
        request.user = user
        
        # 调用视图函数
        response = simple_diary_home(request)
        
        print(f"✅ 视图函数执行成功，状态码: {response.status_code}")
        print(f"✅ 响应内容长度: {len(response.content)}")
        
        # 检查响应内容
        content = response.content.decode('utf-8')
        if '简单生活日记' in content:
            print("✅ 页面标题正确")
        else:
            print("❌ 页面标题不正确")
            
        if '--text-color: #2c3e50' in content:
            print("✅ CSS变量已定义")
        else:
            print("❌ CSS变量未定义")
            
        return True
        
    except Exception as e:
        print(f"❌ 视图函数执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_models():
    """测试模型"""
    print("\n🧪 测试模型...")
    
    try:
        # 测试LifeDiaryEntry模型
        user = User.objects.filter(username='testuser').first()
        if user:
            # 测试随机问题
            question = LifeDiaryEntry.get_random_question()
            print(f"✅ 随机问题获取成功: {question}")
            
            # 测试连续天数
            streak = LifeDiaryEntry.get_writing_streak(user)
            print(f"✅ 连续天数获取成功: {streak}")
            
            # 测试字数统计
            entry = LifeDiaryEntry.objects.filter(user=user).first()
            if entry:
                word_count = entry.word_count
                print(f"✅ 字数统计获取成功: {word_count}")
            else:
                print("⚠️ 没有找到日记条目")
                
        return True
        
    except Exception as e:
        print(f"❌ 模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_rendering():
    """测试模板渲染"""
    print("\n🧪 测试模板渲染...")
    
    try:
        from django.template.loader import render_to_string
        from django.contrib.auth.models import User
        
        user = User.objects.filter(username='testuser').first()
        if user:
            context = {
                'today_entry': None,
                'daily_question': '今天最让你印象深刻的颜色是？',
                'recent_achievements': [],
                'streak_days': 0,
                'month_entries_count': 0,
                'today': '2024-01-01',
            }
            
            # 渲染模板
            html = render_to_string('tools/simple_diary_home.html', context)
            
            print(f"✅ 模板渲染成功，内容长度: {len(html)}")
            
            if '简单生活日记' in html:
                print("✅ 模板内容正确")
            else:
                print("❌ 模板内容不正确")
                
            return True
        else:
            print("❌ 测试用户不存在")
            return False
            
    except Exception as e:
        print(f"❌ 模板渲染失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🔍 开始调试简单日记页面...")
    
    success = True
    success &= test_view_function()
    success &= test_models()
    success &= test_template_rendering()
    
    if success:
        print("\n🎉 所有测试通过！")
    else:
        print("\n❌ 部分测试失败，请检查错误信息")
