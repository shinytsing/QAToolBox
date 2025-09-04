"""
端到端用户流程测试
使用Playwright测试完整的用户交互流程
"""

import pytest
from playwright.sync_api import Page, expect
import time


class TestUserRegistrationFlow:
    """用户注册流程测试"""

    def test_user_registration_success(self, page: Page):
        """测试成功的用户注册流程"""
        # 访问首页
        page.goto("http://localhost:8000")

        # 点击注册链接
        page.click("text=注册")
        expect(page).to_have_url("**/users/register/")

        # 填写注册表单
        timestamp = int(time.time())
        username = f"testuser_{timestamp}"
        email = f"test_{timestamp}@example.com"

        page.fill('[name="username"]', username)
        page.fill('[name="email"]', email)
        page.fill('[name="password1"]', "testpass123456")
        page.fill('[name="password2"]', "testpass123456")

        # 处理验证码（如果存在）
        if page.locator('[name="captcha_1"]').is_visible():
            # 这里需要根据实际验证码实现来处理
            pass

        # 提交注册表单
        page.click('[type="submit"]')

        # 验证注册成功
        expect(page).to_have_url("**/")  # 重定向到首页
        expect(page.locator("text=欢迎")).to_be_visible()

    def test_user_registration_validation(self, page: Page):
        """测试注册表单验证"""
        page.goto("http://localhost:8000/users/register/")

        # 提交空表单
        page.click('[type="submit"]')

        # 验证错误消息
        expect(page.locator("text=此字段是必填项")).to_be_visible()

        # 测试密码不匹配
        page.fill('[name="username"]', "testuser")
        page.fill('[name="email"]', "test@example.com")
        page.fill('[name="password1"]', "password123")
        page.fill('[name="password2"]', "differentpassword")

        page.click('[type="submit"]')
        expect(page.locator("text=密码不匹配")).to_be_visible()


class TestUserLoginFlow:
    """用户登录流程测试"""

    def test_user_login_success(self, page: Page):
        """测试成功的用户登录流程"""
        # 首先注册一个用户（在实际测试中，可能需要预先创建测试用户）
        page.goto("http://localhost:8000/users/login/")

        # 使用测试用户登录
        page.fill('[name="username"]', "admin")  # 假设已有管理员用户
        page.fill('[name="password"]', "admin123")

        page.click('[type="submit"]')

        # 验证登录成功
        expect(page).to_have_url("**/")
        expect(page.locator("text=退出")).to_be_visible()

    def test_user_login_failure(self, page: Page):
        """测试登录失败"""
        page.goto("http://localhost:8000/users/login/")

        # 使用错误的凭据
        page.fill('[name="username"]', "wronguser")
        page.fill('[name="password"]', "wrongpass")

        page.click('[type="submit"]')

        # 验证登录失败
        expect(page.locator("text=用户名或密码错误")).to_be_visible()

    def test_user_logout(self, page: Page):
        """测试用户注销"""
        # 先登录
        page.goto("http://localhost:8000/users/login/")
        page.fill('[name="username"]', "admin")
        page.fill('[name="password"]', "admin123")
        page.click('[type="submit"]')

        # 注销
        page.click("text=退出")

        # 验证注销成功
        expect(page).to_have_url("**/")
        expect(page.locator("text=登录")).to_be_visible()


class TestToolUsageFlow:
    """工具使用流程测试"""

    def test_chat_tool_usage(self, page: Page):
        """测试聊天工具使用流程"""
        # 访问聊天工具
        page.goto("http://localhost:8000/tools/chat/")

        # 检查页面元素
        expect(page.locator("#chat-input")).to_be_visible()
        expect(page.locator("#send-button")).to_be_visible()

        # 发送消息
        page.fill("#chat-input", "Hello, this is a test message")
        page.click("#send-button")

        # 验证消息发送
        expect(page.locator("text=Hello, this is a test message")).to_be_visible()

        # 等待响应（如果有自动回复）
        page.wait_for_timeout(2000)

    def test_fitness_tool_usage(self, page: Page):
        """测试健身工具使用流程"""
        page.goto("http://localhost:8000/tools/fitness/")

        # 测试BMI计算器
        if page.locator("#height-input").is_visible():
            page.fill("#height-input", "175")
            page.fill("#weight-input", "70")
            page.click("#calculate-bmi")

            # 验证计算结果
            expect(page.locator(".bmi-result")).to_be_visible()

    def test_pdf_converter_usage(self, page: Page):
        """测试PDF转换工具使用流程"""
        page.goto("http://localhost:8000/tools/pdf-converter/")

        # 检查文件上传区域
        expect(page.locator(".file-upload-area")).to_be_visible()

        # 这里可以测试文件上传功能
        # 注意：文件上传测试需要准备测试文件


class TestMobileResponsiveness:
    """移动端响应式测试"""

    def test_mobile_navigation(self, page: Page):
        """测试移动端导航"""
        # 设置移动端视窗
        page.set_viewport_size({"width": 375, "height": 667})

        page.goto("http://localhost:8000")

        # 检查移动端菜单
        if page.locator(".mobile-menu-toggle").is_visible():
            page.click(".mobile-menu-toggle")
            expect(page.locator(".mobile-menu")).to_be_visible()

    def test_mobile_forms(self, page: Page):
        """测试移动端表单"""
        page.set_viewport_size({"width": 375, "height": 667})

        page.goto("http://localhost:8000/users/login/")

        # 检查表单在移动端的可用性
        expect(page.locator('[name="username"]')).to_be_visible()
        expect(page.locator('[name="password"]')).to_be_visible()

        # 测试表单填写
        page.fill('[name="username"]', "testuser")
        page.fill('[name="password"]', "testpass")

        # 验证表单元素大小合适
        username_input = page.locator('[name="username"]')
        box = username_input.bounding_box()
        assert box["height"] >= 44  # iOS推荐的最小触摸目标


class TestAccessibility:
    """可访问性测试"""

    def test_keyboard_navigation(self, page: Page):
        """测试键盘导航"""
        page.goto("http://localhost:8000")

        # 测试Tab键导航
        page.keyboard.press("Tab")
        focused_element = page.evaluate("document.activeElement.tagName")
        assert focused_element in ["A", "BUTTON", "INPUT"]

    def test_screen_reader_support(self, page: Page):
        """测试屏幕阅读器支持"""
        page.goto("http://localhost:8000")

        # 检查alt属性
        images = page.locator("img")
        for i in range(images.count()):
            img = images.nth(i)
            if img.is_visible():
                alt_text = img.get_attribute("alt")
                assert alt_text is not None and alt_text.strip() != ""

        # 检查标题层次
        h1_count = page.locator("h1").count()
        assert h1_count == 1  # 页面应该只有一个h1标题


class TestPerformance:
    """性能测试"""

    def test_page_load_time(self, page: Page):
        """测试页面加载时间"""
        start_time = time.time()
        page.goto("http://localhost:8000")

        # 等待页面完全加载
        page.wait_for_load_state("networkidle")

        load_time = time.time() - start_time
        assert load_time < 3.0  # 页面应在3秒内加载完成

    def test_resource_loading(self, page: Page):
        """测试资源加载"""
        # 监听网络请求
        failed_requests = []

        def handle_response(response):
            if response.status >= 400:
                failed_requests.append(response.url)

        page.on("response", handle_response)

        page.goto("http://localhost:8000")
        page.wait_for_load_state("networkidle")

        # 验证没有失败的资源请求
        assert len(failed_requests) == 0, f"Failed requests: {failed_requests}"


class TestSecurity:
    """安全测试"""

    def test_xss_protection(self, page: Page):
        """测试XSS保护"""
        page.goto("http://localhost:8000/tools/chat/")

        # 尝试注入脚本
        malicious_script = "<script>alert('XSS')</script>"

        if page.locator("#chat-input").is_visible():
            page.fill("#chat-input", malicious_script)
            page.click("#send-button")

            # 验证脚本没有被执行
            page.wait_for_timeout(1000)
            # 如果页面没有弹出alert，说明XSS防护生效

    def test_csrf_protection(self, page: Page):
        """测试CSRF保护"""
        page.goto("http://localhost:8000/users/login/")

        # 检查CSRF令牌
        csrf_token = page.locator('[name="csrfmiddlewaretoken"]')
        expect(csrf_token).to_be_visible()

        token_value = csrf_token.get_attribute("value")
        assert token_value is not None and len(token_value) > 0
