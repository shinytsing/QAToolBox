#!/usr/bin/env python3
"""
部署验证脚本
验证生产环境的API和功能完整性
"""
import json
import sys
import time
from urllib.parse import urljoin

import requests


class DeploymentVerifier:
    """部署验证器"""

    def __init__(self, base_url="http://shenyiqing.xin"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "QAToolBox-Deployment-Verifier/1.0"})
        self.results = []

    def log_result(self, test_name, success, message="", response_time=0):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append({"test": test_name, "success": success, "message": message, "response_time": response_time})
        print(f"{status} {test_name}: {message}")
        if response_time > 0:
            print(f"    响应时间: {response_time:.2f}秒")

    def test_health_check(self):
        """测试健康检查端点"""
        try:
            start_time = time.time()
            response = self.session.get(urljoin(self.base_url, "/health/"), timeout=10)
            response_time = time.time() - start_time

            if response.status_code == 200:
                self.log_result("健康检查", True, f"状态码: {response.status_code}", response_time)
                return True
            else:
                self.log_result("健康检查", False, f"状态码: {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_result("健康检查", False, f"连接失败: {str(e)}")
            return False

    def test_home_page(self):
        """测试首页"""
        try:
            start_time = time.time()
            response = self.session.get(self.base_url, timeout=10)
            response_time = time.time() - start_time

            if response.status_code == 200:
                # 检查页面内容
                content = response.text.lower()
                if "qatoolbox" in content or "工具" in content:
                    self.log_result("首页访问", True, f"状态码: {response.status_code}", response_time)
                    return True
                else:
                    self.log_result("首页访问", False, "页面内容异常", response_time)
                    return False
            else:
                self.log_result("首页访问", False, f"状态码: {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_result("首页访问", False, f"连接失败: {str(e)}")
            return False

    def test_tools_api(self):
        """测试工具API"""
        try:
            start_time = time.time()
            response = self.session.get(urljoin(self.base_url, "/tools/"), timeout=10)
            response_time = time.time() - start_time

            if response.status_code == 200:
                self.log_result("工具页面", True, f"状态码: {response.status_code}", response_time)
                return True
            else:
                self.log_result("工具页面", False, f"状态码: {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_result("工具页面", False, f"连接失败: {str(e)}")
            return False

    def test_content_api(self):
        """测试内容API"""
        try:
            start_time = time.time()
            response = self.session.get(urljoin(self.base_url, "/content/"), timeout=10)
            response_time = time.time() - start_time

            if response.status_code == 200:
                self.log_result("内容页面", True, f"状态码: {response.status_code}", response_time)
                return True
            else:
                self.log_result("内容页面", False, f"状态码: {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_result("内容页面", False, f"连接失败: {str(e)}")
            return False

    def test_users_api(self):
        """测试用户API"""
        try:
            start_time = time.time()
            response = self.session.get(urljoin(self.base_url, "/users/"), timeout=10)
            response_time = time.time() - start_time

            if response.status_code == 200:
                self.log_result("用户页面", True, f"状态码: {response.status_code}", response_time)
                return True
            else:
                self.log_result("用户页面", False, f"状态码: {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_result("用户页面", False, f"连接失败: {str(e)}")
            return False

    def test_share_api(self):
        """测试分享API"""
        try:
            start_time = time.time()
            response = self.session.get(urljoin(self.base_url, "/share/"), timeout=10)
            response_time = time.time() - start_time

            if response.status_code == 200:
                self.log_result("分享页面", True, f"状态码: {response.status_code}", response_time)
                return True
            else:
                self.log_result("分享页面", False, f"状态码: {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_result("分享页面", False, f"连接失败: {str(e)}")
            return False

    def test_static_files(self):
        """测试静态文件"""
        try:
            start_time = time.time()
            response = self.session.get(urljoin(self.base_url, "/static/css/responsive.css"), timeout=10)
            response_time = time.time() - start_time

            if response.status_code == 200:
                self.log_result("静态文件", True, f"状态码: {response.status_code}", response_time)
                return True
            else:
                self.log_result("静态文件", False, f"状态码: {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_result("静态文件", False, f"连接失败: {str(e)}")
            return False

    def test_database_connection(self):
        """测试数据库连接（通过API）"""
        try:
            # 尝试访问需要数据库的页面
            start_time = time.time()
            response = self.session.get(urljoin(self.base_url, "/api/"), timeout=10)
            response_time = time.time() - start_time

            # API可能返回200或404，但不应该返回500
            if response.status_code != 500:
                self.log_result("数据库连接", True, f"状态码: {response.status_code}", response_time)
                return True
            else:
                self.log_result("数据库连接", False, f"数据库错误: {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_result("数据库连接", False, f"连接失败: {str(e)}")
            return False

    def test_performance(self):
        """测试性能"""
        try:
            start_time = time.time()
            response = self.session.get(self.base_url, timeout=30)
            response_time = time.time() - start_time

            if response.status_code == 200 and response_time < 5.0:
                self.log_result("性能测试", True, f"响应时间: {response_time:.2f}秒", response_time)
                return True
            elif response.status_code == 200:
                self.log_result("性能测试", False, f"响应时间过长: {response_time:.2f}秒", response_time)
                return False
            else:
                self.log_result("性能测试", False, f"状态码: {response.status_code}", response_time)
                return False
        except Exception as e:
            self.log_result("性能测试", False, f"连接失败: {str(e)}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始部署验证")
        print("=" * 60)
        print(f"目标URL: {self.base_url}")
        print("=" * 60)

        tests = [
            self.test_health_check,
            self.test_home_page,
            self.test_tools_api,
            self.test_content_api,
            self.test_users_api,
            self.test_share_api,
            self.test_static_files,
            self.test_database_connection,
            self.test_performance,
        ]

        passed = 0
        total = len(tests)

        for test in tests:
            if test():
                passed += 1
            time.sleep(1)  # 避免请求过于频繁

        print("\n" + "=" * 60)
        print(f"📊 验证结果: {passed}/{total} 测试通过")

        if passed == total:
            print("🎉 所有验证测试都通过了！部署成功。")
            return True
        else:
            print("⚠️ 部分测试失败，请检查部署状态。")
            return False

    def generate_report(self):
        """生成验证报告"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": self.base_url,
            "total_tests": len(self.results),
            "passed_tests": sum(1 for r in self.results if r["success"]),
            "failed_tests": sum(1 for r in self.results if not r["success"]),
            "results": self.results,
        }

        # 保存报告到文件
        with open("deployment_verification_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n📄 验证报告已保存到: deployment_verification_report.json")
        return report


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="QAToolBox部署验证工具")
    parser.add_argument("--url", default="http://shenyiqing.xin", help="目标URL")
    parser.add_argument("--report", action="store_true", help="生成详细报告")

    args = parser.parse_args()

    verifier = DeploymentVerifier(args.url)
    success = verifier.run_all_tests()

    if args.report:
        verifier.generate_report()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
