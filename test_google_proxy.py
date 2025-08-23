#!/usr/bin/env python3
"""
测试Google代理访问和编码处理
"""

import requests
import chardet
import json

def test_google_encoding():
    """测试Google访问的编码处理"""
    print("🔍 测试Google.com编码处理...")
    
    # 测试URL
    test_url = 'https://www.google.com'
    
    # 禁用压缩的请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'identity',  # 禁用压缩
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print(f"📡 正在访问: {test_url}")
        response = requests.get(test_url, headers=headers, timeout=10, verify=False)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📋 内容类型: {response.headers.get('content-type', 'unknown')}")
        print(f"📏 原始内容长度: {len(response.content)} 字节")
        
        # 获取原始字节内容
        raw_content = response.content
        
        # 检测编码
        detected = chardet.detect(raw_content)
        print(f"🔤 检测到的编码: {detected.get('encoding', 'unknown')} (置信度: {detected.get('confidence', 0):.2f})")
        
        # 尝试不同编码方式
        encodings_to_try = ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']
        
        for encoding in encodings_to_try:
            try:
                decoded_content = raw_content.decode(encoding, errors='replace')
                print(f"\n🧪 使用编码 {encoding}:")
                print(f"   📏 解码后长度: {len(decoded_content)} 字符")
                
                # 检查内容质量
                sample = decoded_content[:200]
                ascii_count = sum(1 for c in sample if ord(c) < 128)
                non_ascii_count = len(sample) - ascii_count
                special_chars = sum(1 for c in sample if ord(c) > 127 and not ('\u4e00' <= c <= '\u9fff'))
                
                print(f"   🔢 ASCII字符: {ascii_count}, 非ASCII: {non_ascii_count}, 特殊字符: {special_chars}")
                
                if '�' in sample:
                    print(f"   ⚠️  包含替换字符，可能编码不正确")
                elif special_chars > non_ascii_count * 0.8:
                    print(f"   ⚠️  特殊字符过多，可能编码不正确")
                else:
                    print(f"   ✅ 编码质量良好")
                
                # 显示前100个字符作为样例
                print(f"   📝 内容样例: {sample[:100]}...")
                
            except UnicodeDecodeError as e:
                print(f"   ❌ {encoding} 解码失败: {e}")
        
        # 使用requests的自动编码处理
        print(f"\n🤖 requests自动处理:")
        print(f"   📏 文本长度: {len(response.text)} 字符")
        print(f"   🔤 使用编码: {response.encoding}")
        print(f"   🔍 检测编码: {response.apparent_encoding}")
        print(f"   📝 内容样例: {response.text[:100]}...")
        
        # 保存不同版本用于比较
        results = {
            'url': test_url,
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'detected_encoding': detected,
            'requests_encoding': response.encoding,
            'apparent_encoding': response.apparent_encoding,
            'raw_length': len(raw_content),
            'text_length': len(response.text),
            'content_sample': response.text[:500] if response.text else ''
        }
        
        with open('google_encoding_test.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 测试结果已保存到 google_encoding_test.json")
        
        return results
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return None

def test_proxy_access():
    """测试通过代理访问Google"""
    print("\n🔗 测试代理访问Google...")
    
    # 本地代理配置
    proxies = {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'identity',
    }
    
    try:
        print("📡 通过代理访问Google...")
        response = requests.get(
            'https://www.google.com',
            proxies=proxies,
            headers=headers,
            timeout=10,
            verify=False
        )
        
        print(f"✅ 代理访问成功 - 状态码: {response.status_code}")
        print(f"📏 内容长度: {len(response.text)} 字符")
        print(f"🔤 编码: {response.encoding}")
        print(f"📝 内容样例: {response.text[:100]}...")
        
    except requests.exceptions.ProxyError:
        print("❌ 代理连接失败 - 请确保Clash代理正在运行")
    except Exception as e:
        print(f"❌ 代理访问失败: {e}")

if __name__ == "__main__":
    # 测试直接访问
    direct_result = test_google_encoding()
    
    # 测试代理访问
    test_proxy_access()
    
    if direct_result:
        print(f"\n📊 总结:")
        print(f"   直接访问Google {'成功' if direct_result.get('status_code') == 200 else '失败'}")
        print(f"   内容长度: {direct_result.get('text_length', 0)} 字符")
        print(f"   编码处理: {direct_result.get('requests_encoding', 'unknown')}")
        
        # 检查是否包含乱码
        content_sample = direct_result.get('content_sample', '')
        if '�' in content_sample:
            print("   ⚠️  内容可能包含乱码")
        elif content_sample and len(content_sample.strip()) > 0:
            print("   ✅ 内容看起来正常")
        else:
            print("   ❌ 内容为空")
