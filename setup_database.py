#!/usr/bin/env python
"""
QAToolBox 数据库初始化脚本
用于创建数据库、执行迁移、创建超级用户和初始数据
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import transaction

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# 导入模型
from django.contrib.auth.models import User
from apps.users.models import UserRole, UserStatus, UserMembership, UserTheme, Profile
from apps.content.models import AILink, Announcement
from apps.tools.models import SocialMediaPlatformConfig

def create_superuser():
    """创建超级用户"""
    try:
        # 检查是否已存在超级用户
        if User.objects.filter(is_superuser=True).exists():
            print("超级用户已存在，跳过创建")
            return
        
        # 创建超级用户
        username = 'admin'
        email = 'admin@qatoolbox.com'
        password = 'admin123456'
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        # 创建用户角色
        UserRole.objects.create(
            user=user,
            role='admin'
        )
        
        # 创建用户状态
        UserStatus.objects.create(
            user=user,
            status='active'
        )
        
        # 创建用户会员
        UserMembership.objects.create(
            user=user,
            membership_type='vip'
        )
        
        # 创建用户主题
        UserTheme.objects.create(
            user=user,
            mode='work',
            theme_style='default'
        )
        
        # 创建用户资料
        Profile.objects.create(
            user=user,
            bio='系统管理员'
        )
        
        print(f"✅ 超级用户创建成功:")
        print(f"   用户名: {username}")
        print(f"   邮箱: {email}")
        print(f"   密码: {password}")
        
    except Exception as e:
        print(f"❌ 创建超级用户失败: {e}")

def create_initial_data():
    """创建初始数据"""
    try:
        # 创建AI友情链接
        ai_links_data = [
            {
                'name': 'ChatGPT',
                'url': 'https://chat.openai.com',
                'category': 'other',
                'description': 'OpenAI开发的AI聊天机器人',
                'icon_url': 'https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg',
                'sort_order': 1
            },
            {
                'name': 'Midjourney',
                'url': 'https://www.midjourney.com',
                'category': 'visual',
                'description': 'AI图像生成工具',
                'icon_url': 'https://www.midjourney.com/favicon.ico',
                'sort_order': 2
            },
            {
                'name': 'RoboNeo',
                'url': 'https://www.roboneo.com/home',
                'category': 'visual',
                'description': 'AI视觉创作平台，提供先进的图像生成和编辑功能',
                'icon_url': 'https://www.google.com/s2/favicons?domain=roboneo.com',
                'sort_order': 3
            },
            {
                'name': 'GitHub Copilot',
                'url': 'https://github.com/features/copilot',
                'category': 'programming',
                'description': 'AI编程助手',
                'icon_url': 'https://github.githubassets.com/images/modules/copilot/cp-head-square.png',
                'sort_order': 4
            },
            {
                'name': 'Notion AI',
                'url': 'https://www.notion.so',
                'category': 'other',
                'description': 'AI驱动的笔记和协作工具',
                'icon_url': 'https://www.notion.so/images/favicon.ico',
                'sort_order': 5
            },
            {
                'name': 'Viggle AI',
                'url': 'https://viggle.ai/home',
                'category': 'image',
                'description': 'AI视频生成工具，创建动态视频内容',
                'sort_order': 6
            },
            {
                'name': 'MiniMax',
                'url': 'https://www.minimaxi.com/',
                'category': 'other',
                'description': '全栈自研的新一代AI模型矩阵，包含文本、视频、音频等多种AI能力',
                'sort_order': 7
            }
        ]
        
        for link_data in ai_links_data:
            AILink.objects.get_or_create(
                name=link_data['name'],
                defaults=link_data
            )
        
        print("✅ AI友情链接创建成功")
        
        # 创建社交媒体平台配置
        platform_configs = [
            {
                'platform': 'xiaohongshu',
                'api_endpoint': 'https://api.xiaohongshu.com',
                'is_active': True,
                'rate_limit': 100
            },
            {
                'platform': 'douyin',
                'api_endpoint': 'https://api.douyin.com',
                'is_active': True,
                'rate_limit': 100
            },
            {
                'platform': 'netease',
                'api_endpoint': 'https://api.music.163.com',
                'is_active': True,
                'rate_limit': 200
            },
            {
                'platform': 'weibo',
                'api_endpoint': 'https://api.weibo.com',
                'is_active': True,
                'rate_limit': 100
            },
            {
                'platform': 'bilibili',
                'api_endpoint': 'https://api.bilibili.com',
                'is_active': True,
                'rate_limit': 100
            },
            {
                'platform': 'zhihu',
                'api_endpoint': 'https://api.zhihu.com',
                'is_active': True,
                'rate_limit': 100
            }
        ]
        
        for config in platform_configs:
            SocialMediaPlatformConfig.objects.get_or_create(
                platform=config['platform'],
                defaults=config
            )
        
        print("✅ 社交媒体平台配置创建成功")
        
        # 创建欢迎公告
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            Announcement.objects.get_or_create(
                title='欢迎使用QAToolBox',
                defaults={
                    'content': '''
                    <h3>🎉 欢迎来到QAToolBox！</h3>
                    <p>这是一个多功能工具集合平台，包含以下四大主题模块：</p>
                    <ul>
                        <li><strong>生活模式</strong>：生活日记、爆款文案、冥想指导</li>
                        <li><strong>极客模式</strong>：数据爬虫、PDF转换引擎、测试用例生成器</li>
                        <li><strong>狂暴模式</strong>：锻炼中心</li>
                        <li><strong>Emo模式</strong>：自我分析、故事版生成、命运解析</li>
                    </ul>
                    <p>开始探索各种功能吧！如有问题或建议，请随时反馈。</p>
                    ''',
                    'priority': 'medium',
                    'status': 'published',
                    'is_popup': True,
                    'created_by': admin_user
                }
            )
            print("✅ 欢迎公告创建成功")
        
    except Exception as e:
        print(f"❌ 创建初始数据失败: {e}")

def setup_database():
    """完整的数据库设置流程"""
    print("🚀 开始设置QAToolBox数据库...")
    
    try:
        # 1. 执行数据库迁移
        print("📦 执行数据库迁移...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ 数据库迁移完成")
        
        # 2. 收集静态文件
        print("📁 收集静态文件...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ 静态文件收集完成")
        
        # 3. 创建超级用户
        print("👤 创建超级用户...")
        create_superuser()
        
        # 4. 创建初始数据
        print("📊 创建初始数据...")
        create_initial_data()
        
        print("\n🎉 数据库设置完成！")
        print("\n📋 下一步操作：")
        print("1. 启动开发服务器: python manage.py runserver")
        print("2. 访问管理后台: http://localhost:8000/admin")
        print("3. 使用超级用户登录: admin / admin123456")
        
    except Exception as e:
        print(f"❌ 数据库设置失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    setup_database() 