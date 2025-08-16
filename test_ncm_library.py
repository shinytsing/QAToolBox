#!/usr/bin/env python3
"""
使用ncmdump库测试NCM解密
"""
import os
import sys
import subprocess

# 检查是否安装了ncmdump
try:
    import ncmdump
    print("✅ ncmdump库已安装")
except ImportError:
    print("❌ ncmdump库未安装，尝试安装...")
    subprocess.run([sys.executable, "-m", "pip", "install", "ncmdump"])
    try:
        import ncmdump
        print("✅ ncmdump库安装成功")
    except ImportError:
        print("❌ ncmdump库安装失败")
        sys.exit(1)

def test_ncm_decryption():
    ncm_file = "src/static/audio/meditation/MISTERK,Tphunk,89DX - Sakana~_副本.ncm"
    
    if not os.path.exists(ncm_file):
        print(f"❌ NCM文件不存在: {ncm_file}")
        return
    
    try:
        # 使用ncmdump解密
        print(f"🔍 使用ncmdump解密NCM文件: {ncm_file}")
        
        # 解密并保存
        output_file = "src/static/audio/meditation/MISTERK_ncmdump_decrypted.mp3"
        
        # 使用ncmdump.dump函数
        success = ncmdump.dump(ncm_file, output_file)
        
        if success:
            print(f"✅ ncmdump解密成功，输出文件: {output_file}")
            
            # 检查文件大小
            if os.path.exists(output_file):
                size = os.path.getsize(output_file)
                print(f"📁 解密文件大小: {size:,} bytes")
                
                # 检查文件头部
                with open(output_file, 'rb') as f:
                    header = f.read(32)
                print(f"📊 文件头32字节: {header.hex()}")
                
                # 测试ffprobe
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                    '-show_format', '-show_streams', output_file
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ ffprobe可以读取解密后的文件")
                else:
                    print("❌ ffprobe无法读取解密后的文件")
                    
        else:
            print("❌ ncmdump解密失败")
            
    except Exception as e:
        print(f"❌ ncmdump解密出错: {e}")

if __name__ == "__main__":
    test_ncm_decryption()
