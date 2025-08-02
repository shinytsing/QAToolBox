#!/usr/bin/env python3
"""
免费音乐API测试脚本
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_music_api():
    """测试免费音乐API功能"""
    print("🎵 开始测试免费音乐API功能...")
    
    # 测试不同模式的音乐API
    modes = ['work', 'life', 'training', 'emo']
    
    for mode in modes:
        print(f"\n📻 测试 {mode} 模式音乐...")
        try:
            response = requests.get(f"{BASE_URL}/tools/api/music/?mode={mode}&action=random")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    song = data.get('data', {})
                    print(f"✅ {mode} 模式: {song.get('name', '未知歌曲')} - {song.get('artist', '未知歌手')}")
                else:
                    print(f"❌ {mode} 模式: {data.get('error', '未知错误')}")
            else:
                print(f"❌ {mode} 模式: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {mode} 模式: 连接错误 - {e}")
    
    # 测试获取所有模式信息
    print(f"\n🎨 测试模式信息API...")
    try:
        response = requests.get(f"{BASE_URL}/tools/api/music/?action=modes")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                modes_info = data.get('data', [])
                print(f"✅ 模式信息API: 找到 {len(modes_info)} 个模式")
                for mode_info in modes_info:
                    print(f"   - {mode_info.get('mode')}: {mode_info.get('description')}")
            else:
                print(f"❌ 模式信息API: {data.get('error', '未知错误')}")
        else:
            print(f"❌ 模式信息API: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 模式信息API: 连接错误 - {e}")
    
    # 测试搜索功能
    print(f"\n🔍 测试音乐搜索功能...")
    try:
        response = requests.get(f"{BASE_URL}/tools/api/music/?action=search&keyword=music&mode=work")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                songs = data.get('data', [])
                print(f"✅ 搜索功能: 找到 {len(songs)} 首相关歌曲")
            else:
                print(f"❌ 搜索功能: {data.get('error', '未知错误')}")
        else:
            print(f"❌ 搜索功能: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 搜索功能: 连接错误 - {e}")
    
    # 测试公告API
    print(f"\n📢 测试公告API...")
    try:
        response = requests.get(f"{BASE_URL}/content/api/announcements/")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                announcements = data.get('announcements', [])
                print(f"✅ 公告API: 找到 {len(announcements)} 条公告")
            else:
                print(f"❌ 公告API: {data.get('error', '未知错误')}")
        else:
            print(f"❌ 公告API: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 公告API: 连接错误 - {e}")

def test_music_test_page():
    """测试音乐测试页面"""
    print(f"\n🌐 测试音乐测试页面...")
    try:
        response = requests.get(f"{BASE_URL}/music-test/")
        if response.status_code == 200:
            print("✅ 音乐测试页面: 可以正常访问")
        else:
            print(f"❌ 音乐测试页面: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 音乐测试页面: 连接错误 - {e}")

def test_direct_api():
    """直接测试音乐API类"""
    print(f"\n🔧 直接测试音乐API类...")
    try:
        from apps.tools.utils.music_api import free_music_api
        
        # 测试获取可用模式
        modes = free_music_api.get_available_modes()
        print(f"✅ 可用模式: {', '.join(modes)}")
        
        # 测试每个模式的音乐
        for mode in modes:
            tracks = free_music_api.get_music_by_mode(mode)
            print(f"✅ {mode} 模式: 找到 {len(tracks)} 首音乐")
            
            if tracks:
                random_song = free_music_api.get_random_song(mode)
                if random_song:
                    print(f"   - 随机歌曲: {random_song.get('name')} - {random_song.get('artist')}")
        
        # 测试搜索功能
        search_results = free_music_api.search_song('music', 'work')
        print(f"✅ 搜索测试: 找到 {len(search_results)} 首相关歌曲")
        
    except Exception as e:
        print(f"❌ 直接API测试: {e}")

if __name__ == "__main__":
    print("🚀 免费音乐API功能测试开始")
    print("=" * 50)
    
    test_music_api()
    test_direct_api()
    test_music_test_page()
    
    print("\n" + "=" * 50)
    print("🎉 测试完成！")
    print("\n📝 使用说明:")
    print("1. 访问 http://localhost:8001 体验完整功能")
    print("2. 访问 http://localhost:8001/music-test/ 测试音乐功能")
    print("3. 右上角设置菜单可以控制音乐播放")
    print("4. 切换不同模式会自动加载对应类型的免费音乐")
    print("5. 支持多种免费音乐源: Jamendo、Free Music Archive、ccMixter等")
    print("6. 如果在线API不可用，会自动切换到本地音乐文件") 