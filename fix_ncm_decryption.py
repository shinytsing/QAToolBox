#!/usr/bin/env python3
"""
完全重写的NCM解密算法
"""
import os
import struct
import base64
import json
import uuid

def decrypt_ncm_complete(ncm_path):
    """完全重写的NCM解密算法"""
    try:
        from Crypto.Cipher import AES
    except ImportError:
        try:
            from Cryptodome.Cipher import AES
        except ImportError:
            raise Exception("需要安装pycryptodome库: pip install pycryptodome")
    
    print("🔧 使用完全重写的NCM解密算法...")
    
    with open(ncm_path, 'rb') as f:
        # 检查文件头
        header = f.read(8)
        if header != b'CTENFDAM':
            raise Exception("不是有效的NCM文件")
        
        print(f"✅ 文件头验证通过: {header}")
        
        # 跳过版本信息
        f.seek(2, 1)
        
        # 读取密钥长度
        key_length = struct.unpack('<I', f.read(4))[0]
        print(f"🔑 密钥长度: {key_length}")
        
        # 读取密钥数据
        key_data = f.read(key_length)
        print(f"🔑 原始密钥数据长度: {len(key_data)}")
        print(f"🔑 原始密钥数据前32字节: {key_data[:32].hex()}")
        
        # XOR 0x64
        key_data_xor = bytes([byte ^ 0x64 for byte in key_data])
        print(f"🔑 XOR 0x64后: {key_data_xor[:32].hex()}")
        
        # AES解密
        core_key = b'hzHRAmso5kInbaxW'
        cipher = AES.new(core_key, AES.MODE_ECB)
        decrypted_key = cipher.decrypt(key_data_xor)
        print(f"🔑 AES解密后: {decrypted_key[:32].hex()}")
        
        # 移除PKCS7填充
        while decrypted_key and decrypted_key[-1] == 0:
            decrypted_key = decrypted_key[:-1]
        print(f"🔑 移除填充后: {decrypted_key[:32].hex()}")
        print(f"🔑 解密后密钥长度: {len(decrypted_key)}")
        
        # 尝试解析JSON
        try:
            key_json_start = decrypted_key.find(b'{')
            if key_json_start != -1:
                key_json_data = decrypted_key[key_json_start:]
                json_end = key_json_data.find(b'}')
                if json_end != -1:
                    key_json_data = key_json_data[:json_end + 1]
                    key_info = json.loads(key_json_data.decode('utf-8'))
                    print(f"🔑 JSON解析成功: {key_info}")
                    if 'key' in key_info:
                        rc4_key = bytes(key_info['key'])
                        print(f"🔑 从JSON提取RC4密钥: {rc4_key[:32].hex()}")
                    else:
                        raise Exception("JSON中没有key字段")
                else:
                    raise Exception("找不到JSON结束位置")
            else:
                raise Exception("找不到JSON开始位置")
        except Exception as e:
            print(f"❌ JSON解析失败: {e}")
            # 备用方案：跳过neteasecloudmusic前缀
            netease_prefix = b'neteasecloudmusic'
            prefix_pos = decrypted_key.find(netease_prefix)
            if prefix_pos != -1:
                rc4_key = decrypted_key[prefix_pos + len(netease_prefix):]
                print(f"🔑 跳过前缀提取RC4密钥: {rc4_key[:32].hex()}")
            else:
                raise Exception("无法提取RC4密钥")
        
        print(f"🔑 最终RC4密钥长度: {len(rc4_key)}")
        
        # 读取元数据长度
        meta_length = struct.unpack('<I', f.read(4))[0]
        print(f"📝 元数据长度: {meta_length}")
        
        # 跳过元数据
        if meta_length > 0:
            f.seek(meta_length, 1)
        
        # 跳过CRC
        f.seek(9, 1)
        
        # 读取盒子长度
        box_length = struct.unpack('<I', f.read(4))[0]
        print(f"📦 盒子长度: {box_length}")
        
        # 跳过盒子数据
        if box_length > 0:
            f.seek(box_length, 1)
        
        # 获取音频数据位置
        audio_start = f.tell()
        print(f"🎵 音频数据开始位置: {audio_start}")
        
        # 创建输出文件
        temp_dir = os.path.dirname(ncm_path) or os.getcwd()
        unique_id = str(uuid.uuid4())[:8]
        output_path = os.path.join(temp_dir, f'decrypted_complete_{unique_id}.mp3')
        
        print(f"📄 输出文件: {output_path}")
        
        # RC4解密音频数据
        with open(output_path, 'wb') as out_file:
            # 初始化RC4状态
            S = list(range(256))
            j = 0
            
            # 密钥调度算法 (KSA)
            for i in range(256):
                j = (j + S[i] + rc4_key[i % len(rc4_key)]) % 256
                S[i], S[j] = S[j], S[i]
            
            # 伪随机生成算法 (PRGA)
            i = j = 0
            chunk_count = 0
            total_size = 0
            
            while True:
                chunk = f.read(0x8000)  # 32KB
                if not chunk:
                    break
                
                chunk_count += 1
                total_size += len(chunk)
                
                if chunk_count % 50 == 0:
                    print(f"🔄 处理第{chunk_count}块，总大小: {total_size:,} bytes")
                
                # RC4解密
                decrypted = bytearray()
                for byte in chunk:
                    i = (i + 1) % 256
                    j = (j + S[i]) % 256
                    S[i], S[j] = S[j], S[i]
                    k = S[(S[i] + S[j]) % 256]
                    decrypted.append(byte ^ k)
                
                out_file.write(decrypted)
        
        print(f"✅ 解密完成，处理了{chunk_count}个数据块，总大小: {total_size:,} bytes")
        
        # 验证输出文件
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            file_size = os.path.getsize(output_path)
            print(f"✅ 解密成功，文件大小: {file_size:,} bytes")
            
            # 检查文件头
            with open(output_path, 'rb') as check_file:
                header = check_file.read(16)
                print(f"🔍 解密后文件头: {header.hex()}")
                
                # 检查是否是有效的音频格式
                if header.startswith(b'ID3'):
                    print("✅ 检测到MP3文件（ID3标签）")
                    return output_path
                elif header[0:2] == b'\xff\xfb' or header[0:2] == b'\xff\xfa':
                    print("✅ 检测到MP3文件（帧头）")
                    return output_path
                elif header.startswith(b'RIFF'):
                    print("✅ 检测到WAV文件")
                    return output_path
                elif header.startswith(b'fLaC'):
                    print("✅ 检测到FLAC文件")
                    return output_path
                elif b'ftyp' in header[4:8]:
                    print("✅ 检测到M4A/MP4文件")
                    return output_path
                else:
                    print("❌ 无法识别音频格式")
                    return None
        
        return None
        
    except Exception as e:
        print(f"❌ 解密失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # 查找最新的NCM文件
    temp_dir = "media/temp_audio"
    if not os.path.exists(temp_dir):
        print("❌ 临时目录不存在")
        exit(1)
    
    ncm_files = []
    for file in os.listdir(temp_dir):
        if file.endswith('.ncm'):
            file_path = os.path.join(temp_dir, file)
            ncm_files.append((file_path, os.path.getmtime(file_path)))
    
    if not ncm_files:
        print("❌ 没有找到NCM文件")
        exit(1)
    
    # 使用最新的NCM文件
    ncm_files.sort(key=lambda x: x[1], reverse=True)
    latest_ncm = ncm_files[0][0]
    
    print(f"📁 使用文件: {latest_ncm}")
    result = decrypt_ncm_complete(latest_ncm)
    
    if result:
        print(f"✅ 解密成功: {result}")
    else:
        print("❌ 解密失败")
