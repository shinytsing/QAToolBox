#!/usr/bin/env python
"""
修复用户 profile 缺失问题
"""
import os
import sys
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import Profile, UserRole, UserStatus, UserMembership, UserTheme

def create_user_profile(user):
    """为用户创建 profile 和相关对象"""
    try:
        # 创建 Profile
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'bio': f'{user.username} 的个人简介',
                'phone': '',
            }
        )
        if created:
            print(f"✅ 为用户 {user.username} 创建了 Profile")
        else:
            print(f"ℹ️  用户 {user.username} 已有 Profile")
        
        # 创建 UserRole
        role, created = UserRole.objects.get_or_create(
            user=user,
            defaults={'role': 'admin' if user.is_superuser else 'user'}
        )
        if created:
            print(f"✅ 为用户 {user.username} 创建了 UserRole")
        
        # 创建 UserStatus
        status, created = UserStatus.objects.get_or_create(
            user=user,
            defaults={'status': 'active'}
        )
        if created:
            print(f"✅ 为用户 {user.username} 创建了 UserStatus")
        
        # 创建 UserMembership
        membership, created = UserMembership.objects.get_or_create(
            user=user,
            defaults={'membership_type': 'premium' if user.is_superuser else 'free'}
        )
        if created:
            print(f"✅ 为用户 {user.username} 创建了 UserMembership")
        
        # 创建 UserTheme
        theme, created = UserTheme.objects.get_or_create(
            user=user,
            defaults={'mode': 'work'}
        )
        if created:
            print(f"✅ 为用户 {user.username} 创建了 UserTheme")
            
        return True
    except Exception as e:
        print(f"❌ 为用户 {user.username} 创建 profile 失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 开始修复用户 profile 问题...")
    
    # 获取所有用户
    users = User.objects.all()
    print(f"📊 找到 {users.count()} 个用户")
    
    success_count = 0
    for user in users:
        print(f"\n👤 处理用户: {user.username}")
        if create_user_profile(user):
            success_count += 1
    
    print(f"\n🎉 修复完成! 成功处理 {success_count}/{users.count()} 个用户")
    
    # 验证修复结果
    print("\n🔍 验证修复结果...")
    for user in users:
        try:
            profile = user.profile
            print(f"✅ {user.username}: Profile 存在")
        except Profile.DoesNotExist:
            print(f"❌ {user.username}: Profile 不存在")

if __name__ == '__main__':
    main()
