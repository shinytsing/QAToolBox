#!/usr/bin/env python3
"""
修复用户模型，为现有用户创建缺失的关联模型
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from apps.users.models import UserRole, UserStatus, UserMembership, UserActionLog, Profile

def fix_user_models():
    """为现有用户创建缺失的关联模型"""
    print("=== 修复用户模型 ===")
    
    users = User.objects.all()
    print(f"总用户数: {users.count()}")
    
    for user in users:
        print(f"\n处理用户: {user.username}")
        
        # 创建UserRole
        try:
            role = UserRole.objects.get(user=user)
            print(f"  ✓ UserRole已存在: {role.role}")
        except UserRole.DoesNotExist:
            role = UserRole.objects.create(user=user, role='user')
            print(f"  + 创建UserRole: {role.role}")
        
        # 创建UserStatus
        try:
            status = UserStatus.objects.get(user=user)
            print(f"  ✓ UserStatus已存在: {status.status}")
        except UserStatus.DoesNotExist:
            status = UserStatus.objects.create(user=user, status='active')
            print(f"  + 创建UserStatus: {status.status}")
        
        # 创建UserMembership
        try:
            membership = UserMembership.objects.get(user=user)
            print(f"  ✓ UserMembership已存在: {membership.membership_type}")
        except UserMembership.DoesNotExist:
            membership = UserMembership.objects.create(user=user, membership_type='free')
            print(f"  + 创建UserMembership: {membership.membership_type}")
        
        # 创建Profile
        try:
            profile = Profile.objects.get(user=user)
            print(f"  ✓ Profile已存在")
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user)
            print(f"  + 创建Profile")
    
    print("\n=== 修复完成 ===")

if __name__ == '__main__':
    fix_user_models() 