"""
性能测试 - Locust配置文件
用于模拟大量用户并发访问，测试系统性能
"""

from locust import HttpUser, task, between
import random
import json


class WebsiteUser(HttpUser):
    """网站用户行为模拟"""
    wait_time = between(1, 3)  # 用户操作间隔1-3秒
    
    def on_start(self):
        """用户开始时的初始化操作"""
        self.client.verify = False  # 忽略SSL证书验证（测试环境）
        
        # 获取CSRF令牌
        response = self.client.get("/users/login/")
        if response.status_code == 200:
            # 从响应中提取CSRF令牌
            import re
            match = re.search(r'name="csrfmiddlewaretoken" value="([^"]*)"', response.text)
            if match:
                self.csrf_token = match.group(1)
            else:
                self.csrf_token = ""
        
        # 可选：模拟用户登录
        if hasattr(self, 'csrf_token'):
            self.login()
    
    def login(self):
        """用户登录"""
        login_data = {
            "username": "testuser",
            "password": "testpass123",
            "csrfmiddlewaretoken": self.csrf_token
        }
        
        with self.client.post("/users/login/", data=login_data, catch_response=True) as response:
            if response.status_code == 302:  # 登录成功重定向
                response.success()
            else:
                response.failure("登录失败")
    
    @task(10)
    def view_homepage(self):
        """访问首页 - 最高权重"""
        self.client.get("/")
    
    @task(8)
    def view_tools_page(self):
        """访问工具页面"""
        self.client.get("/tools/")
    
    @task(5)
    def view_chat_tool(self):
        """访问聊天工具"""
        self.client.get("/tools/chat/")
    
    @task(5)
    def view_fitness_tools(self):
        """访问健身工具"""
        self.client.get("/tools/fitness/")
    
    @task(3)
    def view_pdf_converter(self):
        """访问PDF转换工具"""
        self.client.get("/tools/pdf-converter/")
    
    @task(2)
    def api_tools_list(self):
        """API - 获取工具列表"""
        self.client.get("/api/tools/")
    
    @task(2)
    def search_tools(self):
        """搜索工具"""
        search_terms = ["chat", "pdf", "fitness", "音乐", "图片"]
        term = random.choice(search_terms)
        self.client.get(f"/tools/search/?q={term}")
    
    @task(1)
    def user_profile(self):
        """访问用户配置页面"""
        self.client.get("/users/profile/")
    
    @task(1)
    def view_admin_page(self):
        """访问管理页面"""
        self.client.get("/admin/")


class APIUser(HttpUser):
    """API用户行为模拟"""
    wait_time = between(0.5, 2)
    
    @task(5)
    def api_health_check(self):
        """API健康检查"""
        self.client.get("/api/health/")
    
    @task(10)
    def api_tools_list(self):
        """获取工具列表"""
        self.client.get("/api/tools/")
    
    @task(3)
    def api_user_profile(self):
        """获取用户配置"""
        with self.client.get("/api/users/profile/", catch_response=True) as response:
            if response.status_code == 401:  # 未授权是预期的
                response.success()
    
    @task(2)
    def api_tool_usage_log(self):
        """工具使用日志"""
        data = {
            "tool_name": random.choice(["chat", "pdf", "fitness"]),
            "action": "view"
        }
        self.client.post("/api/tools/usage/", json=data)


class HeavyUser(HttpUser):
    """重度用户行为模拟（模拟复杂操作）"""
    wait_time = between(2, 5)
    
    @task(3)
    def upload_file(self):
        """模拟文件上传"""
        # 创建模拟文件内容
        files = {
            'file': ('test.txt', 'This is test file content', 'text/plain')
        }
        
        with self.client.post("/tools/file-upload/", files=files, catch_response=True) as response:
            if response.status_code in [200, 302, 404]:  # 404表示端点不存在，也是正常的
                response.success()
            else:
                response.failure(f"文件上传失败: {response.status_code}")
    
    @task(2)
    def long_running_task(self):
        """模拟长时间运行的任务"""
        data = {
            "task_type": "heavy_computation",
            "parameters": {"iterations": 1000}
        }
        
        with self.client.post("/api/tasks/", json=data, catch_response=True) as response:
            if response.status_code in [200, 201, 404]:
                response.success()
    
    @task(1)
    def batch_operations(self):
        """批量操作"""
        data = {
            "operations": [
                {"type": "create", "data": {"name": f"item_{i}"}}
                for i in range(10)
            ]
        }
        
        with self.client.post("/api/batch/", json=data, catch_response=True) as response:
            if response.status_code in [200, 201, 404]:
                response.success()


class MobileUser(HttpUser):
    """移动端用户行为模拟"""
    wait_time = between(1, 4)  # 移动端用户操作较慢
    
    def on_start(self):
        """设置移动端请求头"""
        self.client.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15'
        })
    
    @task(8)
    def mobile_homepage(self):
        """移动端首页"""
        self.client.get("/")
    
    @task(5)
    def mobile_tools(self):
        """移动端工具页面"""
        self.client.get("/tools/")
    
    @task(3)
    def mobile_search(self):
        """移动端搜索"""
        terms = ["聊天", "健身", "PDF"]
        term = random.choice(terms)
        self.client.get(f"/search/?q={term}")
    
    @task(1)
    def mobile_profile(self):
        """移动端个人资料"""
        self.client.get("/users/profile/")


# 自定义用户类权重配置
class WebsiteUserClass(WebsiteUser):
    weight = 70  # 70%的用户是普通网站用户


class APIUserClass(APIUser):
    weight = 20  # 20%的用户是API用户


class HeavyUserClass(HeavyUser):
    weight = 5   # 5%的用户是重度用户


class MobileUserClass(MobileUser):
    weight = 5   # 5%的用户是移动端用户


# 性能测试场景
def run_performance_test():
    """运行性能测试的命令行示例
    
    基础测试：
    locust -f locustfile.py --host=http://localhost:8000
    
    指定用户数和增长率：
    locust -f locustfile.py --host=http://localhost:8000 -u 100 -r 10
    
    无界面模式（自动化）：
    locust -f locustfile.py --host=http://localhost:8000 -u 100 -r 10 --headless -t 300s
    
    生成报告：
    locust -f locustfile.py --host=http://localhost:8000 -u 100 -r 10 --headless -t 300s --html=report.html
    """
    pass


if __name__ == "__main__":
    print("Locust性能测试配置文件")
    print("使用方法：")
    print("1. 启动应用服务器: python manage.py runserver")
    print("2. 运行性能测试: locust -f locustfile.py --host=http://localhost:8000")
    print("3. 打开浏览器访问: http://localhost:8089")
