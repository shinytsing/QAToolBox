#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试NCM文件的脚本
"""

import os
import struct
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def create_test_ncm_file():
    """创建一个测试用的NCM文件"""
    print("🎵 创建测试NCM文件")
    print("=" * 50)
    
    # 创建测试目录
    test_dir = "test_audio"
    os.makedirs(test_dir, exist_ok=True)
    
    # 测试文件路径
    test_ncm_path = os.path.join(test_dir, "test_real.ncm")
    
    try:
        with open(test_ncm_path, 'wb') as f:
            # 1. 文件头
            f.write(b'CTENFDAM')
            
            # 2. 版本信息
            f.write(b'\x00\x00')
            
            # 3. 密钥数据
            # 生成一个简单的密钥数据
            key_data = b'test_key_data_16'  # 16字节
            key_length = len(key_data)
            
            # XOR加密密钥数据
            encrypted_key = bytes([byte ^ 0x64 for byte in key_data])
            
            # 写入密钥数据长度
            f.write(struct.pack('<I', key_length))
            
            # 写入加密的密钥数据
            f.write(encrypted_key)
            
            # 4. 元数据
            # 创建测试元数据
            metadata = {
                "musicName": "测试歌曲",
                "artist": ["测试艺术家"],
                "album": "测试专辑",
                "duration": 180000  # 3分钟，毫秒
            }
            
            meta_json = json.dumps(metadata, ensure_ascii=False)
            meta_bytes = meta_json.encode('utf-8')
            
            # 添加22字节的头部
            meta_with_header = b'\x00' * 22 + meta_bytes
            
            # 填充到16字节的倍数
            padded_meta = pad(meta_with_header, 16)
            
            # AES加密元数据
            meta_key = b'MoOtOiTvINGwd2E6'
            meta_cipher = AES.new(meta_key, AES.MODE_ECB)
            encrypted_meta = meta_cipher.encrypt(padded_meta)
            
            # XOR加密
            encrypted_meta = bytes([byte ^ 0x63 for byte in encrypted_meta])
            
            # 写入元数据长度
            f.write(struct.pack('<I', len(encrypted_meta)))
            
            # 写入加密的元数据
            f.write(encrypted_meta)
            
            # 5. 5字节填充
            f.write(b'\x00' * 5)
            
            # 6. 专辑封面
            # 创建一个简单的测试图片数据
            test_image_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'  # 最小JPEG
            
            # 添加22字节的头部
            image_with_header = b'\x00' * 22 + test_image_data
            
            # 填充到16字节的倍数
            padded_image = pad(image_with_header, 16)
            
            # AES加密图片数据
            image_cipher = AES.new(meta_key, AES.MODE_ECB)
            encrypted_image = image_cipher.encrypt(padded_image)
            
            # XOR加密
            encrypted_image = bytes([byte ^ 0x63 for byte in encrypted_image])
            
            # 写入图片空间（总空间）
            f.write(struct.pack('<I', len(encrypted_image)))
            
            # 写入图片大小
            f.write(struct.pack('<I', len(encrypted_image)))
            
            # 写入加密的图片数据
            f.write(encrypted_image)
            
            # 7. 音频数据（模拟）
            # 创建一个简单的音频数据（这里只是占位符）
            audio_data = b'\x00' * 1024  # 1KB的测试音频数据
            
            # RC4加密音频数据（简化版本）
            # 这里我们只是简单地XOR加密
            encrypted_audio = bytes([byte ^ 0xAA for byte in audio_data])
            
            # 写入音频数据
            f.write(encrypted_audio)
        
        print(f"✅ 成功创建测试NCM文件: {test_ncm_path}")
        print(f"📊 文件大小: {os.path.getsize(test_ncm_path)} 字节")
        
        return test_ncm_path
        
    except Exception as e:
        print(f"❌ 创建测试NCM文件失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_created_ncm():
    """测试创建的NCM文件"""
    print("\n🧪 测试创建的NCM文件")
    print("=" * 50)
    
    # 导入解密函数
    import sys
    from pathlib import Path
    
    # 添加项目根目录到Python路径
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    
    import django
    django.setup()
    
    from apps.tools.legacy_views import decrypt_ncm_file_correct
    
    test_file = "test_audio/test_real.ncm"
    
    if not os.path.exists(test_file):
        print("❌ 测试文件不存在")
        return False
    
    try:
        print("🔍 正在解密测试NCM文件...")
        result = decrypt_ncm_file_correct(test_file)
        
        if result:
            print("✅ NCM文件解密成功")
            
            # 检查元数据
            metadata = result.get('metadata', {})
            print(f"📝 元数据:")
            print(f"   - 标题: {metadata.get('title', '未知')}")
            print(f"   - 艺术家: {metadata.get('artist', '未知')}")
            print(f"   - 专辑: {metadata.get('album', '未知')}")
            print(f"   - 时长: {metadata.get('duration', '未知')}秒")
            
            # 检查专辑封面
            album_cover = result.get('album_cover')
            if album_cover:
                print("🖼️ 专辑封面:")
                print(f"   - 大小: {album_cover.get('size', 0)} 字节")
                print(f"   - 格式: {album_cover.get('format', '未知')}")
                
                # 保存封面
                cover_path = "test_album_cover_real.jpg"
                with open(cover_path, 'wb') as f:
                    f.write(album_cover['data'])
                print(f"   - 已保存到: {cover_path}")
            
            # 检查音频数据
            audio_data = result.get('audio_data')
            if audio_data:
                print(f"🎵 音频数据: {len(audio_data)} 字节")
            
            return True
        else:
            print("❌ NCM文件解密失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🎵 NCM测试文件创建工具")
    print("=" * 60)
    
    # 创建测试NCM文件
    ncm_file = create_test_ncm_file()
    
    if not ncm_file:
        print("❌ 无法创建测试文件")
        return
    
    # 测试创建的NCM文件
    test_success = test_created_ncm()
    
    # 输出结果
    print("\n📊 测试结果")
    print("=" * 50)
    print(f"NCM文件创建: {'✅ 成功' if ncm_file else '❌ 失败'}")
    print(f"NCM文件测试: {'✅ 成功' if test_success else '❌ 失败'}")
    
    if ncm_file and test_success:
        print("\n🎉 所有测试通过！NCM文件创建和解密功能正常")
    else:
        print("\n⚠️  部分测试失败，请检查相关功能")

if __name__ == "__main__":
    main()
