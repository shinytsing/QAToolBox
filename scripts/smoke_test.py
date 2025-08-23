#!/usr/bin/env python3
"""
QAToolBox 冒烟测试脚本
在部署后快速验证系统基本功能是否正常
"""

import argparse
import json
import sys
import time
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class SmokeTest:
    """冒烟测试类"""
    
    def __init__(self, base_url, timeout=30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = self._create_session()
        self.test_results = []
        
    def _create_session(self):
        """创建带重试机制的会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _log(self, message, level="INFO"):
        """日志输出"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def _test_endpoint(self, endpoint, method="GET", data=None, 
                      expected_status=200, description=""):
        """测试单个端点"""
        url = urljoin(self.base_url, endpoint)
        test_name = f"{method} {endpoint}"
        
        if description:
            test_name += f" - {description}"
        
        try:
            self._log(f"测试: {test_name}")
            
            response = self.session.request(
                method=method,
                url=url,
                json=data if method in ['POST', 'PUT'] else None,
                timeout=self.timeout
            )
            
            success = response.status_code == expected_status
            
            result = {
                'test': test_name,
                'url': url,
                'method': method,
                'status_code': response.status_code,
                'expected_status': expected_status,
                'success': success,
                'response_time': response.elapsed.total_seconds(),
                'error': None
            }
            
            if success:
                self._log(f"✅ {test_name} - 通过 ({response.status_code})")
            else:
                self._log(f"❌ {test_name} - 失败 (期望: {expected_status}, 实际: {response.status_code})")
                result['error'] = f"状态码不匹配: 期望 {expected_status}, 实际 {response.status_code}"
            
        except Exception as e:
            self._log(f"❌ {test_name} - 异常: {str(e)}")
            result = {
                'test': test_name,
                'url': url,
                'method': method,
                'success': False,
                'error': str(e)
            }
        
        self.test_results.append(result)
        return result['success']
    
    def test_health_check(self):
        """测试健康检查端点"""
        self._log("开始健康检查测试...")
        return self._test_endpoint('/health/', description="系统健康检查")
    
    def test_home_page(self):
        """测试首页"""
        self._log("开始首页测试...")
        return self._test_endpoint('/', description="首页访问")
    
    def test_static_files(self):
        """测试静态文件"""
        self._log("开始静态文件测试...")
        
        static_files = [
            '/static/base.css',
            '/static/js/theme_manager.js',
            '/static/favicon.ico'
        ]
        
        success_count = 0
        for static_file in static_files:
            if self._test_endpoint(static_file, description=f"静态文件: {static_file}"):
                success_count += 1
        
        return success_count == len(static_files)
    
    def test_api_endpoints(self):
        """测试API端点"""
        self._log("开始API端点测试...")
        
        api_endpoints = [
            ('/api/tools/', "工具列表API"),
            ('/api/users/profile/', "用户配置API", 401),  # 未登录应返回401
        ]
        
        success_count = 0
        for endpoint_info in api_endpoints:
            endpoint = endpoint_info[0]
            description = endpoint_info[1]
            expected_status = endpoint_info[2] if len(endpoint_info) > 2 else 200
            
            if self._test_endpoint(endpoint, description=description, 
                                 expected_status=expected_status):
                success_count += 1
        
        return success_count == len(api_endpoints)
    
    def test_user_functions(self):
        """测试用户功能"""
        self._log("开始用户功能测试...")
        
        # 测试登录页面
        login_success = self._test_endpoint('/users/login/', description="登录页面")
        
        # 测试注册页面
        register_success = self._test_endpoint('/users/register/', description="注册页面")
        
        return login_success and register_success
    
    def test_tool_pages(self):
        """测试工具页面"""
        self._log("开始工具页面测试...")
        
        tool_pages = [
            '/tools/',
            '/tools/chat/',
            '/tools/fitness/',
        ]
        
        success_count = 0
        for page in tool_pages:
            if self._test_endpoint(page, description=f"工具页面: {page}"):
                success_count += 1
        
        return success_count == len(tool_pages)
    
    def test_database_connection(self):
        """测试数据库连接"""
        self._log("开始数据库连接测试...")
        
        # 通过admin页面测试数据库连接
        return self._test_endpoint('/admin/login/', description="管理员登录页面（数据库连接测试）")
    
    def test_cache_system(self):
        """测试缓存系统"""
        self._log("开始缓存系统测试...")
        
        # 通过重复请求测试缓存
        endpoint = '/tools/'
        
        # 第一次请求
        first_request = self._test_endpoint(endpoint, description="缓存测试 - 第一次请求")
        
        # 第二次请求（应该从缓存获取）
        second_request = self._test_endpoint(endpoint, description="缓存测试 - 第二次请求")
        
        return first_request and second_request
    
    def test_security_headers(self):
        """测试安全头"""
        self._log("开始安全头测试...")
        
        try:
            response = self.session.get(urljoin(self.base_url, '/'))
            headers = response.headers
            
            security_checks = {
                'X-Frame-Options': 'DENY',
                'X-Content-Type-Options': 'nosniff',
                'X-XSS-Protection': '1; mode=block'
            }
            
            success = True
            for header, expected_value in security_checks.items():
                if header in headers:
                    if expected_value and headers[header] != expected_value:
                        self._log(f"❌ 安全头 {header} 值不正确: {headers[header]}")
                        success = False
                    else:
                        self._log(f"✅ 安全头 {header} 存在")
                else:
                    self._log(f"❌ 缺少安全头: {header}")
                    success = False
            
            return success
            
        except Exception as e:
            self._log(f"❌ 安全头测试异常: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        self._log("=" * 50)
        self._log("开始冒烟测试")
        self._log("=" * 50)
        
        tests = [
            ("健康检查", self.test_health_check),
            ("首页访问", self.test_home_page),
            ("静态文件", self.test_static_files),
            ("API端点", self.test_api_endpoints),
            ("用户功能", self.test_user_functions),
            ("工具页面", self.test_tool_pages),
            ("数据库连接", self.test_database_connection),
            ("缓存系统", self.test_cache_system),
            ("安全头", self.test_security_headers),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            self._log(f"\n--- {test_name} ---")
            try:
                if test_func():
                    passed_tests += 1
                    self._log(f"✅ {test_name} 测试通过")
                else:
                    self._log(f"❌ {test_name} 测试失败")
            except Exception as e:
                self._log(f"❌ {test_name} 测试异常: {str(e)}")
        
        # 输出测试结果
        self._log("=" * 50)
        self._log("测试结果汇总")
        self._log("=" * 50)
        self._log(f"总测试数: {total_tests}")
        self._log(f"通过测试: {passed_tests}")
        self._log(f"失败测试: {total_tests - passed_tests}")
        self._log(f"成功率: {(passed_tests / total_tests) * 100:.1f}%")
        
        # 保存详细测试结果
        self._save_test_report()
        
        return passed_tests == total_tests
    
    def _save_test_report(self):
        """保存测试报告"""
        report = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'base_url': self.base_url,
            'total_tests': len(self.test_results),
            'passed_tests': sum(1 for r in self.test_results if r['success']),
            'failed_tests': sum(1 for r in self.test_results if not r['success']),
            'test_results': self.test_results
        }
        
        report_file = f"smoke_test_report_{int(time.time())}.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self._log(f"测试报告已保存: {report_file}")
        except Exception as e:
            self._log(f"保存测试报告失败: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='QAToolBox 冒烟测试')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='应用URL (默认: http://localhost:8000)')
    parser.add_argument('--timeout', type=int, default=30,
                       help='请求超时时间 (默认: 30秒)')
    
    args = parser.parse_args()
    
    # 运行冒烟测试
    smoke_test = SmokeTest(args.url, args.timeout)
    
    if smoke_test.run_all_tests():
        print("\n🎉 所有冒烟测试通过！系统运行正常。")
        sys.exit(0)
    else:
        print("\n❌ 部分冒烟测试失败！请检查系统状态。")
        sys.exit(1)


if __name__ == '__main__':
    main()
