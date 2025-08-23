#!/usr/bin/env python3
"""
测试增强功能的脚本
包括地图功能、联系卖家、消息通知、想要功能、收藏功能等
"""

import os
import sys
import django
import json
import requests
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.append('.')
django.setup()

from django.contrib.auth.models import User
from apps.tools.models.legacy_models import ShipBaoItem, ShipBaoWantItem, ShipBaoFavorite
from apps.tools.models.chat_models import ChatRoom, ChatMessage, ChatNotification


def test_shipbao_features():
    """测试船宝功能"""
    print("🚢 测试船宝功能...")
    
    # 创建测试用户
    seller, _ = User.objects.get_or_create(username='test_seller', defaults={'email': 'seller@test.com'})
    buyer, _ = User.objects.get_or_create(username='test_buyer', defaults={'email': 'buyer@test.com'})
    
    # 创建测试商品
    item, created = ShipBaoItem.objects.get_or_create(
        title='测试商品 - iPhone 15',
        defaults={
            'seller': seller,
            'description': '全新iPhone 15，原封未拆',
            'category': 'electronics',
            'price': 6999.00,
            'condition': 5,
            'location': '北京市朝阳区',
            'location_city': '北京',
            'location_region': '朝阳区',
            'status': 'pending'
        }
    )
    
    if created:
        print(f"✅ 创建测试商品: {item.title}")
    else:
        print(f"📱 使用现有商品: {item.title}")
    
    # 测试想要功能
    want_item, want_created = ShipBaoWantItem.objects.get_or_create(
        user=buyer,
        item=item,
        defaults={'message': '我对这个商品很感兴趣！'}
    )
    
    if want_created:
        item.increment_want_count()
        print(f"❤️ 用户 {buyer.username} 想要商品")
    
    # 测试收藏功能
    favorite, fav_created = ShipBaoFavorite.objects.get_or_create(
        user=buyer,
        item=item
    )
    
    if fav_created:
        item.increment_favorite_count()
        print(f"⭐ 用户 {buyer.username} 收藏商品")
    
    print(f"📊 商品统计: 想要人数={item.want_count}, 收藏人数={item.favorite_count}")
    return item, seller, buyer


def test_chat_features(item, seller, buyer):
    """测试聊天功能"""
    print("\n💬 测试聊天功能...")
    
    # 创建聊天室
    room, created = ChatRoom.objects.get_or_create(
        room_id=f'shipbao_{item.id}_{buyer.id}_{seller.id}',
        defaults={
            'user1': buyer,
            'user2': seller,
            'room_type': 'private',
            'status': 'active',
            'name': f'关于商品: {item.title}'
        }
    )
    
    if created:
        print(f"✅ 创建聊天室: {room.name}")
    else:
        print(f"💭 使用现有聊天室: {room.name}")
    
    # 发送测试消息
    message = ChatMessage.objects.create(
        room=room,
        sender=buyer,
        content='你好，我对这个商品很感兴趣，价格可以商量吗？',
        message_type='text'
    )
    
    print(f"📤 发送消息: {message.content[:30]}...")
    
    # 创建通知
    notification, notif_created = ChatNotification.objects.get_or_create(
        user=seller,
        room=room,
        message=message,
        defaults={'is_read': False}
    )
    
    if notif_created:
        print(f"🔔 创建通知给 {seller.username}")
    
    return room, message, notification


def test_api_endpoints():
    """测试API端点"""
    print("\n🌐 测试API端点...")
    
    # 本地服务器URL
    base_url = 'http://localhost:8000'
    
    endpoints = [
        '/tools/api/location/',
        '/tools/api/map_picker/?query=北京',
        '/tools/api/notifications/summary/',
        '/tools/api/shipbao/items/',
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - 响应正常")
            else:
                print(f"⚠️ {endpoint} - 状态码: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - 连接失败: {e}")


def test_map_features():
    """测试地图功能"""
    print("\n🗺️ 测试地图功能...")
    
    from apps.tools.views.map_base_views import search_location_suggestions, get_ip_location
    from unittest.mock import Mock
    
    # 测试地址搜索
    suggestions = search_location_suggestions('北京')
    print(f"🔍 搜索'北京'得到 {len(suggestions)} 个建议")
    for i, suggestion in enumerate(suggestions[:3]):
        print(f"  {i+1}. {suggestion['name']} - {suggestion['address']}")
    
    # 测试IP定位
    mock_request = Mock()
    mock_request.META = {'REMOTE_ADDR': '127.0.0.1'}
    location = get_ip_location(mock_request)
    print(f"📍 IP定位结果: {location['city']}, {location['region']}")


def generate_test_report():
    """生成测试报告"""
    print("\n📋 生成测试报告...")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'features_tested': [
            '地图功能和地址定位',
            '联系卖家功能（集成心动链接）',
            '聊天系统消息通知',
            '商品想要功能',
            '收藏功能',
            'API端点测试'
        ],
        'statistics': {
            'total_items': ShipBaoItem.objects.count(),
            'total_want_records': ShipBaoWantItem.objects.count(),
            'total_favorites': ShipBaoFavorite.objects.count(),
            'total_chat_rooms': ChatRoom.objects.count(),
            'total_notifications': ChatNotification.objects.count(),
        }
    }
    
    with open('test_enhanced_features_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("✅ 测试报告已保存到 test_enhanced_features_report.json")
    
    # 打印统计信息
    print("\n📈 数据库统计:")
    for key, value in report['statistics'].items():
        print(f"  {key}: {value}")


def main():
    """主测试函数"""
    print("🎯 开始测试增强功能...")
    print("=" * 50)
    
    try:
        # 测试船宝功能
        item, seller, buyer = test_shipbao_features()
        
        # 测试聊天功能
        room, message, notification = test_chat_features(item, seller, buyer)
        
        # 测试地图功能
        test_map_features()
        
        # 测试API端点
        test_api_endpoints()
        
        # 生成测试报告
        generate_test_report()
        
        print("\n" + "=" * 50)
        print("🎉 所有测试完成！")
        print("\n📌 要启动开发服务器测试前端功能，请运行:")
        print("   python manage.py runserver")
        print("\n📌 然后访问以下页面测试:")
        print(f"   - 商品详情: http://localhost:8000/tools/shipbao/item/{item.id}/")
        print(f"   - 聊天室: http://localhost:8000/tools/heart_link/chat/{room.room_id}/")
        print("   - 船宝首页: http://localhost:8000/tools/shipbao/")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
