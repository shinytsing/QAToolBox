#!/usr/bin/env python3
"""
详细调试NCM解密过程
"""

import os
import sys
import struct
import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# 添加Django路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

def debug_ncm_decryption(ncm_path):
    """详细调试NCM解密过程"""
    print(f"🔍 开始调试NCM文件: {ncm_path}")
    print("=" * 80)
    
    if not os.path.exists(ncm_path):
        print(f"❌ 文件不存在: {ncm_path}")
        return
    
    file_size = os.path.getsize(ncm_path)
    print(f"📁 文件大小: {file_size:,} bytes")
    
    try:
        with open(ncm_path, 'rb') as f:
            data = f.read()
        
        print(f"📊 文件头32字节: {data[:32].hex()}")
        
        # 检查NCM文件头
        if not data.startswith(b'CTENFDAM'):
            print("❌ 不是有效的NCM文件头")
            return
        
        print("✅ 检测到有效的NCM文件头")
        
        # 使用正确的NCM解析逻辑
        offset = 8  # 跳过文件头
        offset += 2  # 跳过版本信息
        
        # 读取密钥数据长度
        if offset + 4 > len(data):
            print("❌ 文件太短，无法读取密钥长度")
            return
        
        key_length = struct.unpack('<I', data[offset:offset+4])[0]
        print(f"🔑 密钥数据长度: {key_length} bytes")
        
        if key_length <= 0 or key_length > 1024 * 1024:
            print(f"❌ 密钥长度异常: {key_length}")
            return
            
        offset += 4
        
        # 读取密钥数据
        if offset + key_length > len(data):
            print("❌ 文件太短，无法读取密钥数据")
            return
        
        key_data = data[offset:offset+key_length]
        print(f"🔑 密钥数据前32字节: {key_data[:32].hex()}")
        offset += key_length
        
        # 读取修改计数
        if offset + 4 > len(data):
            print("❌ 文件太短，无法读取修改计数")
            return
        
        modify_count = struct.unpack('<I', data[offset:offset+4])[0]
        print(f"📝 修改计数: {modify_count}")
        offset += 4
        
        # 读取CRC32
        if offset + 4 > len(data):
            print("❌ 文件太短，无法读取CRC32")
            return
        
        crc32 = struct.unpack('<I', data[offset:offset+4])[0]
        print(f"🔍 CRC32: {crc32:08x}")
        offset += 4
        
        # 读取专辑图片数据长度
        if offset + 4 > len(data):
            print("❌ 文件太短，无法读取专辑图片长度")
            return
        
        album_cover_length = struct.unpack('<I', data[offset:offset+4])[0]
        print(f"🖼️ 专辑图片长度: {album_cover_length} bytes")
        offset += 4
        
        # 检查专辑图片长度是否合理
        if album_cover_length > 1024 * 1024:  # 最大1MB
            print(f"⚠️ 专辑图片长度异常，跳过: {album_cover_length}")
            # 尝试查找音频数据的开始位置
            audio_start_found = False
            
            # 方法1: 查找MP3帧头
            for i in range(offset, min(offset + 2048, len(data) - 4)):
                if data[i] == 0xFF and (data[i + 1] & 0xE0) == 0xE0:  # MP3帧头
                    offset = i
                    print(f"🔍 找到MP3帧头位置: {i}")
                    audio_start_found = True
                    break
            
            # 方法2: 查找ID3标签
            if not audio_start_found:
                for i in range(offset, min(offset + 2048, len(data) - 3)):
                    if data[i:i+3] == b'ID3':  # ID3标签
                        offset = i
                        print(f"🔍 找到ID3标签位置: {i}")
                        audio_start_found = True
                        break
            
            # 方法3: 查找常见的音频模式
            if not audio_start_found:
                for i in range(offset, min(offset + 4096, len(data) - 4)):
                    # 查找可能表示音频数据的模式
                    if (data[i] == 0xFF and data[i+1] in [0xE0, 0xE1, 0xE2, 0xE3, 0xE4, 0xE5, 0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xEB, 0xEC, 0xED, 0xEE, 0xEF, 0xF0, 0xF1, 0xF2, 0xF3, 0xF4, 0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xFA, 0xFB, 0xFC, 0xFD, 0xFE, 0xFF]):
                        offset = i
                        print(f"🔍 找到可能的音频数据位置: {i}")
                        audio_start_found = True
                        break
            
            if not audio_start_found:
                # 如果没找到，尝试不同的偏移量
                print(f"🔍 未找到音频数据标记，尝试不同偏移量...")
                for test_offset in [offset + 1024, offset + 2048, offset + 4096, offset + 8192]:
                    if test_offset < len(data):
                        print(f"🔍 尝试偏移量: {test_offset}")
                        offset = test_offset
                        break
        else:
            # 跳过专辑图片数据
            if offset + album_cover_length > len(data):
                print("❌ 文件太短，无法跳过专辑图片数据")
                return
            offset += album_cover_length
        
        # 直接读取剩余的音频数据
        audio_data = data[offset:]
        print(f"🎵 音频数据长度: {len(audio_data):,} bytes")
        print(f"🎵 音频数据前32字节: {audio_data[:32].hex()}")
        
        if len(audio_data) < 1024:
            print("❌ 音频数据太少")
            return
        
        # 尝试解密密钥数据
        print("\n🔓 尝试解密密钥数据...")
        
        # 使用固定的密钥
        core_key = b'hzHRAmso5kInbaxW'
        meta_key = b'mouwangzi'
        
        try:
            # 正确的NCM密钥解密流程
            # 1. 先XOR 0x64
            key_data_xor = bytes([byte ^ 0x64 for byte in key_data])
            print(f"🔓 XOR 0x64后: {key_data_xor[:32].hex()}")
            
            # 2. 使用AES解密
            cipher = AES.new(core_key, AES.MODE_ECB)
            decrypted_key_data = cipher.decrypt(key_data_xor)
            print(f"🔓 AES解密后: {decrypted_key_data[:32].hex()}")
            
            # 3. 移除填充
            try:
                decrypted_key_data = unpad(decrypted_key_data, AES.block_size)
                print(f"🔓 移除填充后: {decrypted_key_data[:32].hex()}")
            except:
                print("⚠️ 无法移除填充，尝试手动移除")
                # 手动移除末尾的0字节
                while decrypted_key_data and decrypted_key_data[-1] == 0:
                    decrypted_key_data = decrypted_key_data[:-1]
                print(f"🔓 手动移除填充后: {decrypted_key_data[:32].hex()}")
            
            # 4. 解析密钥字符串
            try:
                # 解码十六进制字符串
                key_str = decrypted_key_data.decode('ascii')
                print(f"🔑 解析的密钥字符串: {key_str}")
                
                # 提取RC4密钥（去掉neteasecloudmusic前缀）
                if key_str.startswith('neteasecloudmusic'):
                    rc4_key_str = key_str[len('neteasecloudmusic'):]
                    print(f"🔑 提取的RC4密钥字符串: {rc4_key_str}")
                    
                    # 将字符串转换为字节
                    rc4_key = rc4_key_str.encode('ascii')
                    print(f"🔑 RC4密钥长度: {len(rc4_key)} bytes")
                    print(f"🔑 RC4密钥: {rc4_key.hex()}")
                    
                    # 使用RC4解密音频数据
                    print("\n🎵 使用RC4解密音频数据...")
                    decrypted_audio = rc4_decrypt(audio_data, rc4_key)
                    
                    if decrypted_audio:
                        print(f"✅ 音频解密成功")
                        print(f"🎵 解密后音频数据前32字节: {decrypted_audio[:32].hex()}")
                        
                        # 保存解密后的音频数据
                        output_path = "src/static/audio/meditation/MISTERK_decrypted.mp3"
                        with open(output_path, 'wb') as f:
                            f.write(decrypted_audio)
                        
                        print(f"💾 解密后的音频已保存到: {output_path}")
                        print(f"📁 文件大小: {len(decrypted_audio):,} bytes")
                        
                        # 验证文件
                        if decrypted_audio.startswith(b'ID3'):
                            print("✅ 检测到ID3标签")
                        elif decrypted_audio[0] == 0xFF and (decrypted_audio[1] & 0xE0) == 0xE0:
                            print("✅ 检测到MP3帧头")
                        else:
                            print("⚠️ 未检测到标准MP3格式")
                        
                        return output_path
                    else:
                        print("❌ 音频解密失败")
                else:
                    print(f"❌ 密钥格式不正确: {key_str}")
                        
            except Exception as e:
                print(f"❌ 密钥解析失败: {e}")
                print(f"🔍 解密后的数据: {decrypted_key_data}")
                
        except Exception as e:
            print(f"❌ 密钥解密失败: {e}")
        
    except Exception as e:
        print(f"❌ 文件读取失败: {e}")
    
    return None

def rc4_decrypt(data, key):
    """RC4解密"""
    try:
        # RC4密钥调度算法
        S = list(range(256))
        j = 0
        for i in range(256):
            j = (j + S[i] + key[i % len(key)]) % 256
            S[i], S[j] = S[j], S[i]
        
        # RC4伪随机生成算法
        i = j = 0
        result = bytearray()
        
        for byte in data:
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            k = S[(S[i] + S[j]) % 256]
            result.append(byte ^ k)
        
        return bytes(result)
        
    except Exception as e:
        print(f"❌ RC4解密失败: {e}")
        return None

def main():
    """主函数"""
    ncm_file = "src/static/audio/meditation/MISTERK,Tphunk,89DX - Sakana~_副本.ncm"
    
    decrypted_path = debug_ncm_decryption(ncm_file)
    
    if decrypted_path and os.path.exists(decrypted_path):
        print(f"\n🎉 解密成功！")
        print(f"📁 解密文件: {decrypted_path}")
        
        # 测试ffmpeg是否可以处理
        print(f"\n🔍 测试ffmpeg处理...")
        try:
            import subprocess
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', decrypted_path
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ ffprobe可以读取解密后的文件")
            else:
                print(f"❌ ffprobe读取失败: {result.stderr}")
                
        except Exception as e:
            print(f"❌ ffprobe测试异常: {e}")
    else:
        print(f"\n❌ 解密失败！")

if __name__ == "__main__":
    main()
