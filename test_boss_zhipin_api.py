#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Boss直聘API功能测试
测试扫码登录和发送联系请求功能
"""

import sys
import os
import django
import time

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.boss_zhipin_api import BossZhipinAPI
from apps.tools.services.job_search_service import JobSearchService


def test_boss_zhipin_api():
    """测试Boss直聘API功能"""
    print("🚀 开始测试Boss直聘API功能...")
    
    # 创建API实例
    boss_api = BossZhipinAPI()
    
    print("\n1. 测试生成二维码...")
    qr_result = boss_api.generate_qr_code()
    if qr_result.get('success'):
        print("✅ 二维码生成成功")
        print(f"   二维码ID: {qr_result.get('qr_code_id')}")
        print(f"   二维码URL: {qr_result.get('qr_code_url')}")
    else:
        print(f"❌ 二维码生成失败: {qr_result.get('message')}")
        return
    
    print("\n2. 测试检查登录状态...")
    qr_code_id = qr_result.get('qr_code_id')
    status_result = boss_api.check_qr_login_status(qr_code_id)
    print(f"   登录状态: {status_result.get('status')}")
    print(f"   状态消息: {status_result.get('message')}")
    
    print("\n3. 测试获取登录状态...")
    login_status = boss_api.get_login_status()
    print(f"   是否已登录: {login_status.get('is_logged_in')}")
    print(f"   用户Token: {login_status.get('user_token')}")
    print(f"   Cookies数量: {login_status.get('cookies_count')}")
    
    print("\n4. 测试搜索职位...")
    search_result = boss_api.search_jobs(
        job_title="Python开发工程师",
        location="北京",
        min_salary=15,
        max_salary=30,
        page=1,
        page_size=5
    )
    
    if search_result.get('success'):
        jobs = search_result.get('data', {}).get('jobs', [])
        print(f"✅ 搜索成功，找到 {len(jobs)} 个职位")
        for i, job in enumerate(jobs[:3], 1):
            print(f"   职位{i}: {job.get('title')} - {job.get('company')} - {job.get('salary_min')}K-{job.get('salary_max')}K")
    else:
        print(f"❌ 搜索失败: {search_result.get('message')}")
    
    print("\n5. 测试发送联系请求...")
    if jobs:
        job_id = jobs[0].get('id')
        contact_result = boss_api.send_contact_request(job_id)
        if contact_result.get('success'):
            print("✅ 联系请求发送成功")
        else:
            print(f"❌ 联系请求发送失败: {contact_result.get('message')}")
    
    print("\n6. 测试退出登录...")
    boss_api.logout()
    login_status_after = boss_api.get_login_status()
    print(f"   退出后登录状态: {login_status_after.get('is_logged_in')}")


def test_job_search_service():
    """测试求职服务功能"""
    print("\n\n🔧 开始测试求职服务功能...")
    
    # 创建服务实例
    job_service = JobSearchService()
    
    print("\n1. 测试生成二维码...")
    qr_result = job_service.generate_qr_code(user_id=1)
    if qr_result.get('success'):
        print("✅ 二维码生成成功")
    else:
        print(f"❌ 二维码生成失败: {qr_result.get('message')}")
    
    print("\n2. 测试检查登录状态...")
    status_result = job_service.check_qr_login_status(user_id=1)
    print(f"   检查结果: {status_result.get('message')}")
    
    print("\n3. 测试获取登录状态...")
    login_status = job_service.get_login_status(user_id=1)
    print(f"   登录状态: {login_status.get('is_logged_in')}")
    
    print("\n4. 测试退出登录...")
    logout_result = job_service.logout(user_id=1)
    print(f"   退出结果: {logout_result.get('message')}")


def test_contact_request_curl():
    """测试联系请求的curl命令"""
    print("\n\n📋 联系请求curl命令示例:")
    
    curl_command = '''curl 'https://www.zhipin.com/wapi/zpgeek/friend/add.json?securityId=iRaGjHDSwTDaX-k1Xte2V1lJSM6qwihE8T0HeTiFXqEoLjEjij-rh6NcxqYwHbliu-cqQrBZoW5fvbXti81DBQPudaeGNGkzOWzN1XMMkJuBjnN1LIxZoT30PNQVEXpjWnM4gYDMrT_U0T_f03skd2qg-azkzdYtPnSpwZq8mktUV4-aXbPig5Y16nrxvQ1TpKQ1pEK_UvrGcoH4pEa7I4m3my9YscsOdxKCfk3uBDPmWAAIkE5CL-D8sKA2Nj8XMnpaV5n-1hHG54JyBIk~&jobId=043cec34c6fd052a03R42968F1NV&lid=c61b52b4-c532-4677-8c0b-821294aadf8a.f1:common.eyJzZXNzaW9uSWQiOiI4ZjNiMzQwMi1mZDJhLTQzMmUtODgxMi03YzM3MmJmNWEwZDgiLCJyY2RCelR5cGUiOiJmMV9ncmNkIn0.1&_=1754370242456' \\
  -H 'Accept: application/json, text/plain, */*' \\
  -H 'Accept-Language: zh,en;q=0.9,de;q=0.8,is;q=0.7,an;q=0.6,am;q=0.5,ast;q=0.4,ee;q=0.3,ga;q=0.2,et;q=0.1,or;q=0.1,oc;q=0.1,om;q=0.1,eu;q=0.1,bg;q=0.1,be;q=0.1,nso;q=0.1,bs;q=0.1,pl;q=0.1,fa;q=0.1,br;q=0.1,tn;q=0.1,de-AT;q=0.1,de-DE;q=0.1,en-IE;q=0.1,en-AU;q=0.1,en-CA;q=0.1,en-US;q=0.1,en-ZA;q=0.1,en-NZ;q=0.1,en-IN;q=0.1,en-GB-oxendict;q=0.1,en-GB;q=0.1,sq;q=0.1,zh-CN;q=0.1' \\
  -H 'Connection: keep-alive' \\
  -H 'Content-Type: application/x-www-form-urlencoded' \\
  -H 'Origin: https://www.zhipin.com' \\
  -H 'Referer: https://www.zhipin.com/web/geek/jobs' \\
  -H 'Sec-Fetch-Dest: empty' \\
  -H 'Sec-Fetch-Mode: cors' \\
  -H 'Sec-Fetch-Site: same-origin' \\
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36' \\
  -H 'X-Requested-With: XMLHttpRequest' \\
  -H 'sec-ch-ua: "Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"' \\
  -H 'sec-ch-ua-mobile: ?0' \\
  -H 'sec-ch-ua-platform: "macOS"' \\
  -H 'token: xh80ty18jhMwFOJs' \\
  -H 'traceId: F-9d7798UjdGVt0HZ3' \\
  -H 'zp_token: V2RNgvF-X-3F5rVtRuyhgbLiu47DrQxyU~|RNgvF-X-3F5rVtRuyhgbLiu47DrXxCw~' \\
  --data-raw 'sessionId=''''
    
    print(curl_command)
    
    print("\n📝 关键参数说明:")
    print("   - jobId: 职位ID")
    print("   - securityId: 安全ID，用于验证请求")
    print("   - lid: 会话ID")
    print("   - token: 用户认证token")
    print("   - zp_token: Boss直聘token")
    print("   - traceId: 请求追踪ID")


def main():
    """主函数"""
    print("=" * 60)
    print("🤖 Boss直聘自动求职机API测试")
    print("=" * 60)
    
    try:
        # 测试Boss直聘API
        test_boss_zhipin_api()
        
        # 测试求职服务
        test_job_search_service()
        
        # 显示curl命令示例
        test_contact_request_curl()
        
        print("\n" + "=" * 60)
        print("✅ 测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 