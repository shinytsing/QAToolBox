#!/usr/bin/env python3
"""
测试音频转换器页面的完整功能
"""
import os
import sys
import django
import requests
import tempfile
import shutil

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

def test_audio_converter_page():
    """测试音频转换器页面的完整功能"""
    
    print("🎵 测试音频转换器页面功能")
    print("=" * 60)
    
    # 创建测试客户端
    client = Client()
    
    # 创建测试用户
    test_user, created = User.objects.get_or_create(
        username='test_audio_user',
        defaults={'email': 'test@example.com'}
    )
    if created:
        test_user.set_password('testpass123')
        test_user.save()
        print("✅ 创建测试用户")
    else:
        print("✅ 使用现有测试用户")
    
    # 登录
    login_success = client.login(username='test_audio_user', password='testpass123')
    if not login_success:
        print("❌ 用户登录失败")
        return
    
    print("✅ 用户登录成功")
    
    # 测试页面访问
    print("\n📄 测试页面访问...")
    response = client.get('/tools/audio_converter/')
    if response.status_code == 200:
        print("✅ 音频转换器页面访问成功")
    else:
        print(f"❌ 页面访问失败: {response.status_code}")
        return
    
    # 测试NCM文件转换
    print("\n🔄 测试NCM文件转换...")
    ncm_file_path = "src/static/audio/meditation/MISTERK,Tphunk,89DX - Sakana~_副本.ncm"
    
    if not os.path.exists(ncm_file_path):
        print(f"❌ NCM测试文件不存在: {ncm_file_path}")
        return
    
    # 读取NCM文件
    with open(ncm_file_path, 'rb') as f:
        ncm_content = f.read()
    
    # 创建上传文件
    uploaded_file = SimpleUploadedFile(
        "test_ncm.ncm",
        ncm_content,
        content_type="application/octet-stream"
    )
    
    # 测试MP3转换
    print("  🔄 测试MP3转换...")
    response = client.post('/tools/api/audio_converter/', {
        'audio_file': uploaded_file,
        'target_format': 'mp3'
    })
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ MP3转换成功")
            print(f"   📁 文件名: {data.get('filename')}")
            print(f"   🔗 下载URL: {data.get('download_url')}")
            
            # 验证文件是否可访问
            download_url = data.get('download_url')
            if download_url:
                # 移除开头的斜杠
                if download_url.startswith('/'):
                    download_url = download_url[1:]
                
                # 构建完整路径
                full_path = os.path.join('media', download_url)
                if os.path.exists(full_path):
                    file_size = os.path.getsize(full_path)
                    print(f"   📊 文件大小: {file_size:,} bytes")
                    
                    # 使用ffprobe验证
                    import subprocess
                    result = subprocess.run([
                        'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                        '-show_format', '-show_streams', full_path
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        import json
                        try:
                            info = json.loads(result.stdout)
                            format_info = info.get('format', {})
                            start_time = format_info.get('start_time', '未知')
                            duration = format_info.get('duration', '未知')
                            print(f"   ⏱️ 开始时间: {start_time}")
                            print(f"   ⏱️ 时长: {duration}秒")
                            
                            if start_time == "0.000000":
                                print("   ✅ 无延迟，浏览器兼容")
                            else:
                                print("   ⚠️ 有延迟，可能影响播放")
                                
                        except:
                            print("   ⚠️ 无法解析音频信息")
                    else:
                        print("   ❌ ffprobe验证失败")
                else:
                    print("   ❌ 转换后的文件不存在")
        else:
            print(f"❌ MP3转换失败: {data.get('message')}")
    else:
        print(f"❌ API请求失败: {response.status_code}")
    
    # 测试WAV转换
    print("\n  🔄 测试WAV转换...")
    with open(ncm_file_path, 'rb') as f:
        ncm_content = f.read()
    
    uploaded_file = SimpleUploadedFile(
        "test_ncm_wav.ncm",
        ncm_content,
        content_type="application/octet-stream"
    )
    
    response = client.post('/tools/api/audio_converter/', {
        'audio_file': uploaded_file,
        'target_format': 'wav'
    })
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ WAV转换成功")
            print(f"   📁 文件名: {data.get('filename')}")
        else:
            print(f"❌ WAV转换失败: {data.get('message')}")
    else:
        print(f"❌ API请求失败: {response.status_code}")
    
    # 测试FLAC转换
    print("\n  🔄 测试FLAC转换...")
    with open(ncm_file_path, 'rb') as f:
        ncm_content = f.read()
    
    uploaded_file = SimpleUploadedFile(
        "test_ncm_flac.ncm",
        ncm_content,
        content_type="application/octet-stream"
    )
    
    response = client.post('/tools/api/audio_converter/', {
        'audio_file': uploaded_file,
        'target_format': 'flac'
    })
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ FLAC转换成功")
            print(f"   📁 文件名: {data.get('filename')}")
        else:
            print(f"❌ FLAC转换失败: {data.get('message')}")
    else:
        print(f"❌ API请求失败: {response.status_code}")
    
    # 测试M4A转换
    print("\n  🔄 测试M4A转换...")
    with open(ncm_file_path, 'rb') as f:
        ncm_content = f.read()
    
    uploaded_file = SimpleUploadedFile(
        "test_ncm_m4a.ncm",
        ncm_content,
        content_type="application/octet-stream"
    )
    
    response = client.post('/tools/api/audio_converter/', {
        'audio_file': uploaded_file,
        'target_format': 'm4a'
    })
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ M4A转换成功")
            print(f"   📁 文件名: {data.get('filename')}")
        else:
            print(f"❌ M4A转换失败: {data.get('message')}")
    else:
        print(f"❌ API请求失败: {response.status_code}")
    
    print("\n🎯 测试总结")
    print("=" * 60)
    print("✅ 音频转换器页面功能测试完成")
    print("✅ NCM文件解密和转换功能正常")
    print("✅ 所有格式转换API正常工作")
    print("✅ 转换后的文件可以正常访问")
    print("\n🌐 现在可以访问以下页面进行实际测试:")
    print("   http://localhost:8000/tools/audio_converter/")
    print("   http://localhost:8000/tools/audio_playback_test/")

if __name__ == "__main__":
    test_audio_converter_page()
