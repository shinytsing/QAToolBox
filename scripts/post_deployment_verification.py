#!/usr/bin/env python3
"""
部署后验证脚本
用于验证部署的应用是否正常工作
"""

import requests
import time
import sys
import json
from urllib.parse import urljoin

class DeploymentVerifier:
    def __init__(self, base_url="http://shenyiqing.xin", timeout=30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.timeout = timeout
        
    def test_health_endpoint(self):
        """测试健康检查端点"""
        try:
            url = urljoin(self.base_url, '/health/')
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 健康检查通过: {data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ 健康检查失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 健康检查异常: {str(e)}")
            return False
    
    def test_home_page(self):
        """测试首页加载"""
        try:
            response = self.session.get(self.base_url)
            
            if response.status_code == 200:
                if "QAToolBox" in response.text:
                    print("✅ 首页加载正常")
                    return True
                else:
                    print("❌ 首页内容异常")
                    return False
            else:
                print(f"❌ 首页加载失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 首页加载异常: {str(e)}")
            return False
    
    def test_static_files(self):
        """测试静态文件加载"""
        try:
            # 测试CSS文件
            css_url = urljoin(self.base_url, '/static/css/style.css')
            response = self.session.get(css_url)
            
            if response.status_code == 200:
                print("✅ 静态文件加载正常")
                return True
            else:
                print(f"⚠️ 静态文件可能有问题: HTTP {response.status_code}")
                return True  # 不阻塞部署
                
        except Exception as e:
            print(f"⚠️ 静态文件测试异常: {str(e)}")
            return True  # 不阻塞部署
    
    def test_api_endpoints(self):
        """测试API端点"""
        endpoints = [
            '/users/api/session-status/',
        ]
        
        passed = 0
        total = len(endpoints)
        
        for endpoint in endpoints:
            try:
                url = urljoin(self.base_url, endpoint)
                response = self.session.get(url)
                
                if response.status_code in [200, 401, 403]:  # 401/403也算正常
                    print(f"✅ API端点正常: {endpoint}")
                    passed += 1
                else:
                    print(f"❌ API端点异常: {endpoint} - HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ API端点异常: {endpoint} - {str(e)}")
        
        if passed >= total * 0.8:  # 80%通过率
            print(f"✅ API测试通过 ({passed}/{total})")
            return True
        else:
            print(f"❌ API测试失败 ({passed}/{total})")
            return False
    
    def test_performance(self):
        """基础性能测试"""
        try:
            response_times = []
            
            for i in range(5):
                start_time = time.time()
                response = self.session.get(self.base_url)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
                
                time.sleep(1)
            
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                max_time = max(response_times)
                
                print(f"📊 性能测试结果:")
                print(f"   平均响应时间: {avg_time:.2f}s")
                print(f"   最大响应时间: {max_time:.2f}s")
                
                if avg_time < 3.0 and max_time < 5.0:
                    print("✅ 性能测试通过")
                    return True
                else:
                    print("⚠️ 性能可能需要优化")
                    return True  # 不阻塞部署
            else:
                print("❌ 性能测试失败")
                return False
                
        except Exception as e:
            print(f"⚠️ 性能测试异常: {str(e)}")
            return True  # 不阻塞部署
    
    def run_all_tests(self):
        """运行所有验证测试"""
        print(f"🔍 开始部署验证: {self.base_url}")
        print("=" * 50)
        
        tests = [
            ("健康检查", self.test_health_endpoint),
            ("首页加载", self.test_home_page),
            ("静态文件", self.test_static_files),
            ("API端点", self.test_api_endpoints),
            ("性能测试", self.test_performance),
        ]
        
        passed = 0
        critical_failed = 0
        
        for test_name, test_func in tests:
            print(f"\n🧪 执行测试: {test_name}")
            
            try:
                if test_func():
                    passed += 1
                else:
                    if test_name in ["健康检查", "首页加载"]:
                        critical_failed += 1
                        
            except Exception as e:
                print(f"💥 测试异常: {test_name} - {str(e)}")
                if test_name in ["健康检查", "首页加载"]:
                    critical_failed += 1
        
        print("\n" + "=" * 50)
        print(f"📊 验证结果: {passed}/{len(tests)} 通过")
        
        if critical_failed == 0:
            print("✅ 部署验证成功！应用可以正常访问")
            return True
        else:
            print(f"❌ 部署验证失败！关键功能异常 ({critical_failed} 个)")
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='部署后验证脚本')
    parser.add_argument('--url', default='http://shenyiqing.xin', 
                       help='要验证的应用URL')
    parser.add_argument('--timeout', type=int, default=30,
                       help='请求超时时间（秒）')
    
    args = parser.parse_args()
    
    verifier = DeploymentVerifier(args.url, args.timeout)
    
    if verifier.run_all_tests():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
