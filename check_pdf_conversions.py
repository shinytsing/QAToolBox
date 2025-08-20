#!/usr/bin/env python3
"""
检查PDF转换记录和满意度数据
"""

import os
import sys
import django
from django.db.models import Q, Avg, Count
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.models.legacy_models import PDFConversionRecord
from django.contrib.auth.models import User

def check_pdf_conversions():
    """检查PDF转换记录"""
    print("=" * 60)
    print("PDF转换记录检查")
    print("=" * 60)
    
    # 检查所有转换记录
    all_conversions = PDFConversionRecord.objects.all()
    print(f"总转换记录数: {all_conversions.count()}")
    
    if all_conversions.count() == 0:
        print("❌ 数据库中没有转换记录")
        return
    
    # 按用户分组检查
    users = User.objects.all()
    print(f"\n用户数量: {users.count()}")
    
    for user in users:
        print(f"\n👤 用户: {user.username} (ID: {user.id})")
        
        user_conversions = PDFConversionRecord.objects.filter(user=user)
        total_conversions = user_conversions.count()
        successful_conversions = user_conversions.filter(status='success').count()
        
        print(f"  总转换次数: {total_conversions}")
        print(f"  成功转换次数: {successful_conversions}")
        print(f"  成功率: {round(successful_conversions / total_conversions * 100, 1) if total_conversions > 0 else 0}%")
        
        # 检查满意度评分
        ratings = user_conversions.filter(
            status='success',
            satisfaction_rating__isnull=False
        ).values_list('satisfaction_rating', flat=True)
        
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            print(f"  满意度评分数量: {len(ratings)}")
            print(f"  平均评分: {avg_rating:.2f}/5")
            print(f"  满意度百分比: {(avg_rating / 5.0) * 100:.1f}%")
            print(f"  评分详情: {list(ratings)}")
        else:
            print(f"  满意度评分: 无评分记录")
        
        # 检查最近转换记录
        recent_conversions = user_conversions.filter(
            status='success'
        ).order_by('-created_at')[:5]
        
        if recent_conversions:
            print(f"  最近转换记录:")
            for i, conv in enumerate(recent_conversions, 1):
                print(f"    {i}. {conv.original_filename} ({conv.conversion_type})")
                print(f"       时间: {conv.created_at}")
                print(f"       转换时间: {conv.conversion_time}s")
                print(f"       满意度: {conv.satisfaction_rating or '无评分'}")
        else:
            print(f"  最近转换记录: 无")
        
        # 检查转换类型统计
        type_stats = user_conversions.values('conversion_type').annotate(
            count=Count('id'),
            success_count=Count('id', filter=Q(status='success'))
        )
        
        if type_stats:
            print(f"  转换类型统计:")
            for stat in type_stats:
                conv_type = stat['conversion_type']
                count = stat['count']
                success_count = stat['success_count']
                print(f"    {conv_type}: {success_count}/{count} (成功率: {round(success_count/count*100, 1) if count > 0 else 0}%)")

def check_satisfaction_calculation():
    """检查满意度计算逻辑"""
    print("\n" + "=" * 60)
    print("满意度计算逻辑检查")
    print("=" * 60)
    
    # 模拟满意度计算逻辑
    for user in User.objects.all():
        user_conversions = PDFConversionRecord.objects.filter(user=user)
        
        # 计算平均评分
        avg_rating = user_conversions.filter(
            status='success',
            satisfaction_rating__isnull=False
        ).aggregate(avg_rating=Avg('satisfaction_rating'))['avg_rating'] or 0
        
        # 转换为百分比
        user_satisfaction_percentage = (avg_rating / 5.0) * 100 if avg_rating > 0 else 0
        
        print(f"用户 {user.username}:")
        print(f"  平均评分: {avg_rating:.2f}/5")
        print(f"  满意度百分比: {user_satisfaction_percentage:.1f}%")
        
        # 检查是否有82.5%的情况
        if abs(user_satisfaction_percentage - 82.5) < 0.1:
            print(f"  ⚠️ 发现82.5%的满意度，检查原始数据:")
            ratings = user_conversions.filter(
                status='success',
                satisfaction_rating__isnull=False
            ).values_list('satisfaction_rating', flat=True)
            print(f"    原始评分: {list(ratings)}")
            if ratings:
                calculated_avg = sum(ratings) / len(ratings)
                calculated_percentage = (calculated_avg / 5.0) * 100
                print(f"    重新计算: {calculated_avg:.2f}/5 = {calculated_percentage:.1f}%")

def create_test_data():
    """创建测试数据"""
    print("\n" + "=" * 60)
    print("创建测试数据")
    print("=" * 60)
    
    # 获取第一个用户
    user = User.objects.first()
    if not user:
        print("❌ 没有找到用户")
        return
    
    print(f"为用户 {user.username} 创建测试转换记录...")
    
    # 创建一些测试转换记录
    test_records = [
        {
            'user': user,
            'conversion_type': 'pdf_to_word',
            'original_filename': 'test1.pdf',
            'file_size': 1024,
            'status': 'success',
            'conversion_time': 2.5,
            'satisfaction_rating': 4
        },
        {
            'user': user,
            'conversion_type': 'word_to_pdf',
            'original_filename': 'test2.docx',
            'file_size': 2048,
            'status': 'success',
            'conversion_time': 1.8,
            'satisfaction_rating': 5
        },
        {
            'user': user,
            'conversion_type': 'text_to_pdf',
            'original_filename': 'test3.txt',
            'file_size': 512,
            'status': 'success',
            'conversion_time': 0.5,
            'satisfaction_rating': 3
        }
    ]
    
    for record_data in test_records:
        record = PDFConversionRecord.objects.create(**record_data)
        print(f"✅ 创建记录: {record.original_filename} (评分: {record.satisfaction_rating})")
    
    print("✅ 测试数据创建完成")

def main():
    """主函数"""
    print("🔍 PDF转换记录和满意度数据检查")
    print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查现有数据
    check_pdf_conversions()
    check_satisfaction_calculation()
    
    # 询问是否创建测试数据
    print("\n" + "=" * 60)
    response = input("是否创建测试数据？(y/n): ").lower().strip()
    if response == 'y':
        create_test_data()
        print("\n重新检查数据:")
        check_pdf_conversions()
        check_satisfaction_calculation()
    
    print("\n" + "=" * 60)
    print("✅ 检查完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
