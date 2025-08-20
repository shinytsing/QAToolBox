#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试专辑封面提取的脚本
"""

import os
import sys
import struct
import json
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

from apps.tools.legacy_views import decrypt_ncm_file_correct

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_ncm_structure(ncm_path):
    """调试NCM文件结构"""
    print(f"🔍 调试NCM文件结构: {ncm_path}")
    print("=" * 60)
    
    try:
        with open(ncm_path, 'rb') as f:
            # 1. 文件头
            header = f.read(8)
            print(f"文件头: {header}")
            
            if header != b'CTENFDAM':
                print("❌ 不是有效的NCM文件")
                return
            
            # 2. 版本信息
            version = f.read(2)
            print(f"版本信息: {version.hex()}")
            
            # 3. 密钥数据长度
            key_length = struct.unpack('<I', f.read(4))[0]
            print(f"密钥数据长度: {key_length}")
            
            # 4. 跳过密钥数据
            f.seek(key_length, 1)
            print(f"跳过密钥数据: {key_length} 字节")
            
            # 5. 元数据长度
            meta_length = struct.unpack('<I', f.read(4))[0]
            print(f"元数据长度: {meta_length}")
            
            # 6. 跳过元数据
            if meta_length:
                f.seek(meta_length, 1)
                print(f"跳过元数据: {meta_length} 字节")
            
            # 7. 跳过5字节
            f.seek(5, 1)
            print("跳过5字节填充")
            
            # 8. 图片空间
            image_space = struct.unpack('<I', f.read(4))[0]
            print(f"图片空间: {image_space}")
            
            # 9. 图片大小
            image_size = struct.unpack('<I', f.read(4))[0]
            print(f"图片大小: {image_size}")
            
            if image_size > 0:
                print(f"✅ 找到图片数据，大小: {image_size} 字节")
                
                # 读取图片数据
                image_data = f.read(image_size)
                print(f"图片数据前32字节: {image_data[:32].hex()}")
                
                # 检查是否是JPEG
                if image_data.startswith(b'\xff\xd8\xff'):
                    print("✅ 图片数据以JPEG文件头开始")
                elif image_data.startswith(b'\x89PNG'):
                    print("✅ 图片数据以PNG文件头开始")
                else:
                    print("⚠️  图片数据不是标准格式")
                
                # 保存原始图片数据
                raw_image_path = "debug_raw_image.bin"
                with open(raw_image_path, 'wb') as img_f:
                    img_f.write(image_data)
                print(f"原始图片数据已保存到: {raw_image_path}")
                
            else:
                print("❌ 没有找到图片数据")
            
            # 10. 跳过剩余空间
            remaining_space = image_space - image_size
            if remaining_space > 0:
                f.seek(remaining_space, 1)
                print(f"跳过剩余空间: {remaining_space} 字节")
            
            # 11. 音频数据
            audio_data = f.read()
            print(f"音频数据大小: {len(audio_data)} 字节")
            print(f"音频数据前32字节: {audio_data[:32].hex()}")
            
    except Exception as e:
        print(f"❌ 调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

def test_album_cover_extraction():
    """测试专辑封面提取"""
    print("\n🎵 测试专辑封面提取")
    print("=" * 60)
    
    # 查找真实的NCM文件
    real_ncm_files = [
        "./media/temp_audio/debug_target.ncm",
        "./media/temp_audio/test_sample.ncm",
        "./src/static/audio/meditation/MISTERK,Tphunk,89DX - Sakana~_副本.ncm"
    ]
    
    for ncm_file_path in real_ncm_files:
        if not os.path.exists(ncm_file_path):
            print(f"❌ 文件不存在: {ncm_file_path}")
            continue
        
        print(f"\n📁 测试文件: {ncm_file_path}")
        print(f"📊 文件大小: {os.path.getsize(ncm_file_path)} 字节")
        
        # 调试文件结构
        debug_ncm_structure(ncm_file_path)
        
        try:
            # 使用解密函数
            print("\n🔍 使用解密函数提取...")
            ncm_result = decrypt_ncm_file_correct(ncm_file_path)
            
            if ncm_result:
                metadata = ncm_result.get('metadata', {})
                album_cover = ncm_result.get('album_cover')
                
                print(f"📝 元数据: {metadata}")
                
                if album_cover:
                    print("🖼️ 专辑封面提取成功!")
                    print(f"   - 大小: {album_cover.get('size', 0)} 字节")
                    print(f"   - 格式: {album_cover.get('format', '未知')}")
                    
                    # 保存专辑封面
                    cover_path = f"debug_album_cover_{os.path.basename(ncm_file_path)}.jpg"
                    with open(cover_path, 'wb') as f:
                        f.write(album_cover['data'])
                    print(f"   - 已保存到: {cover_path}")
                    
                    # 验证图片格式
                    image_data = album_cover['data']
                    if image_data.startswith(b'\xff\xd8\xff'):
                        print("   - 格式验证: ✅ JPEG")
                    elif image_data.startswith(b'\x89PNG'):
                        print("   - 格式验证: ✅ PNG")
                    else:
                        print("   - 格式验证: ⚠️ 未知格式")
                        print(f"   - 文件头: {image_data[:16].hex()}")
                else:
                    print("❌ 专辑封面提取失败")
            else:
                print("❌ NCM文件解析失败")
                
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {e}")
            import traceback
            traceback.print_exc()

def main():
    """主函数"""
    print("🎵 NCM专辑封面调试工具")
    print("=" * 60)
    
    # 测试专辑封面提取
    test_album_cover_extraction()
    
    print("\n📊 调试完成")
    print("=" * 60)
    print("请检查生成的调试文件:")
    print("- debug_raw_image.bin: 原始图片数据")
    print("- debug_album_cover_*.jpg: 提取的专辑封面")

if __name__ == "__main__":
    main()
