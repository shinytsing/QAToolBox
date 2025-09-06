import json
import time
from django.test import TestCase, LiveServerTestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from unittest.mock import patch, MagicMock

User = get_user_model()

class E2EWorkflowTestCase(LiveServerTestCase):
    """端到端工作流程测试"""
    
    def setUp(self):
        """测试前准备"""
        # 设置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # 创建WebDriver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
        # 创建测试用户
        self.user = User.objects.create_user(
            username='e2etest',
            email='e2etest@example.com',
            password='e2etest123'
        )
        
        # 获取认证令牌
        refresh_token = RefreshToken.for_user(self.user)
        self.access_token = str(refresh_token.access_token)
    
    def tearDown(self):
        """测试后清理"""
        self.driver.quit()
    
    def test_complete_user_journey(self):
        """测试完整用户旅程"""
        # 1. 用户注册
        self._test_user_registration()
        
        # 2. 用户登录
        self._test_user_login()
        
        # 3. 创建健身资料
        self._test_create_fitness_profile()
        
        # 4. 记录训练
        self._test_record_workout()
        
        # 5. 创建生活日记
        self._test_create_diary()
        
        # 6. 使用极客工具
        self._test_use_geek_tool()
        
        # 7. 社交互动
        self._test_social_interaction()
        
        # 8. 数据同步
        self._test_data_sync()
        
        # 9. 查看统计报告
        self._test_view_statistics()
    
    def _test_user_registration(self):
        """测试用户注册"""
        # 访问注册页面
        self.driver.get(f'{self.live_server_url}/frontend/user-interface/#/login')
        
        # 点击注册链接
        register_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "注册"))
        )
        register_link.click()
        
        # 填写注册表单
        username_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_input.send_keys('e2euser')
        
        email_input = self.driver.find_element(By.NAME, "email")
        email_input.send_keys('e2euser@example.com')
        
        password_input = self.driver.find_element(By.NAME, "password")
        password_input.send_keys('e2epass123')
        
        confirm_password_input = self.driver.find_element(By.NAME, "confirm_password")
        confirm_password_input.send_keys('e2epass123')
        
        # 提交表单
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # 验证注册成功
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
    
    def _test_user_login(self):
        """测试用户登录"""
        # 访问登录页面
        self.driver.get(f'{self.live_server_url}/frontend/user-interface/#/login')
        
        # 填写登录表单
        username_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_input.send_keys('e2etest')
        
        password_input = self.driver.find_element(By.NAME, "password")
        password_input.send_keys('e2etest123')
        
        # 提交表单
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # 验证登录成功
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dashboard"))
        )
    
    def _test_create_fitness_profile(self):
        """测试创建健身资料"""
        # 导航到健身页面
        fitness_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "健身"))
        )
        fitness_link.click()
        
        # 点击创建资料按钮
        create_profile_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "create-profile-btn"))
        )
        create_profile_button.click()
        
        # 填写健身资料表单
        height_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "height"))
        )
        height_input.send_keys('175')
        
        weight_input = self.driver.find_element(By.NAME, "weight")
        weight_input.send_keys('70')
        
        age_input = self.driver.find_element(By.NAME, "age")
        age_input.send_keys('25')
        
        gender_select = self.driver.find_element(By.NAME, "gender")
        gender_select.send_keys('male')
        
        activity_select = self.driver.find_element(By.NAME, "activity_level")
        activity_select.send_keys('moderate')
        
        # 提交表单
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # 验证创建成功
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "profile-created"))
        )
    
    def _test_record_workout(self):
        """测试记录训练"""
        # 点击记录训练按钮
        record_workout_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "record-workout-btn"))
        )
        record_workout_button.click()
        
        # 填写训练表单
        workout_name_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "workout_name"))
        )
        workout_name_input.send_keys('E2E测试训练')
        
        workout_type_select = self.driver.find_element(By.NAME, "workout_type")
        workout_type_select.send_keys('strength')
        
        duration_input = self.driver.find_element(By.NAME, "duration")
        duration_input.send_keys('60')
        
        calories_input = self.driver.find_element(By.NAME, "calories_burned")
        calories_input.send_keys('300')
        
        notes_textarea = self.driver.find_element(By.NAME, "notes")
        notes_textarea.send_keys('E2E测试训练记录')
        
        # 提交表单
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # 验证记录成功
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "workout-recorded"))
        )
    
    def _test_create_diary(self):
        """测试创建生活日记"""
        # 导航到生活页面
        life_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "生活"))
        )
        life_link.click()
        
        # 点击创建日记按钮
        create_diary_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "create-diary-btn"))
        )
        create_diary_button.click()
        
        # 填写日记表单
        title_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "title"))
        )
        title_input.send_keys('E2E测试日记')
        
        content_textarea = self.driver.find_element(By.NAME, "content")
        content_textarea.send_keys('今天进行了E2E测试，一切都很顺利！')
        
        mood_select = self.driver.find_element(By.NAME, "mood")
        mood_select.send_keys('happy')
        
        weather_select = self.driver.find_element(By.NAME, "weather")
        weather_select.send_keys('sunny')
        
        # 提交表单
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # 验证创建成功
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "diary-created"))
        )
    
    def _test_use_geek_tool(self):
        """测试使用极客工具"""
        # 导航到极客工具页面
        geek_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "极客"))
        )
        geek_link.click()
        
        # 点击PDF转换工具
        pdf_tool_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "pdf-tool-btn"))
        )
        pdf_tool_button.click()
        
        # 上传文件
        file_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "file"))
        )
        # 这里需要准备一个测试文件
        # file_input.send_keys('/path/to/test.pdf')
        
        # 选择输出格式
        output_format_select = self.driver.find_element(By.NAME, "output_format")
        output_format_select.send_keys('docx')
        
        # 提交转换
        convert_button = self.driver.find_element(By.CLASS_NAME, "convert-btn")
        convert_button.click()
        
        # 验证转换成功
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "conversion-success"))
        )
    
    def _test_social_interaction(self):
        """测试社交互动"""
        # 导航到社交页面
        social_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "社交"))
        )
        social_link.click()
        
        # 点击创建心链按钮
        create_heart_link_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "create-heart-link-btn"))
        )
        create_heart_link_button.click()
        
        # 填写心链表单
        title_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "title"))
        )
        title_input.send_keys('E2E测试心链')
        
        description_textarea = self.driver.find_element(By.NAME, "description")
        description_textarea.send_keys('这是一个E2E测试心链')
        
        tags_input = self.driver.find_element(By.NAME, "tags")
        tags_input.send_keys('E2E,测试,心链')
        
        # 提交表单
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # 验证创建成功
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "heart-link-created"))
        )
    
    def _test_data_sync(self):
        """测试数据同步"""
        # 导航到设置页面
        settings_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "设置"))
        )
        settings_link.click()
        
        # 点击数据同步按钮
        sync_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "sync-data-btn"))
        )
        sync_button.click()
        
        # 验证同步成功
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sync-success"))
        )
    
    def _test_view_statistics(self):
        """测试查看统计报告"""
        # 导航到仪表板
        dashboard_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "仪表板"))
        )
        dashboard_link.click()
        
        # 验证统计图表显示
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "stats-chart"))
        )
        
        # 验证数据统计
        stats_elements = self.driver.find_elements(By.CLASS_NAME, "stat-item")
        self.assertGreater(len(stats_elements), 0)
    
    def test_mobile_responsiveness(self):
        """测试移动端响应式"""
        # 设置移动端视口
        self.driver.set_window_size(375, 667)
        
        # 访问首页
        self.driver.get(f'{self.live_server_url}/frontend/user-interface/#/')
        
        # 验证移动端布局
        mobile_menu = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "mobile-menu"))
        )
        self.assertTrue(mobile_menu.is_displayed())
    
    def test_error_handling(self):
        """测试错误处理"""
        # 访问不存在的页面
        self.driver.get(f'{self.live_server_url}/frontend/user-interface/#/nonexistent')
        
        # 验证404页面显示
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "error-404"))
        )
    
    def test_performance(self):
        """测试性能"""
        start_time = time.time()
        
        # 访问首页
        self.driver.get(f'{self.live_server_url}/frontend/user-interface/#/')
        
        # 等待页面加载完成
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dashboard"))
        )
        
        load_time = time.time() - start_time
        
        # 验证加载时间在合理范围内
        self.assertLess(load_time, 5.0)  # 5秒内加载完成
    
    def test_accessibility(self):
        """测试可访问性"""
        # 访问首页
        self.driver.get(f'{self.live_server_url}/frontend/user-interface/#/')
        
        # 验证关键元素有适当的标签
        main_content = self.driver.find_element(By.TAG_NAME, "main")
        self.assertTrue(main_content.is_displayed())
        
        # 验证表单元素有标签
        form_elements = self.driver.find_elements(By.TAG_NAME, "input")
        for element in form_elements:
            if element.get_attribute("type") not in ["hidden", "submit"]:
                self.assertTrue(element.get_attribute("aria-label") or element.get_attribute("placeholder"))
    
    def test_cross_browser_compatibility(self):
        """测试跨浏览器兼容性"""
        # 这里可以添加其他浏览器的测试
        # 例如Firefox, Safari等
        pass
    
    def test_offline_functionality(self):
        """测试离线功能"""
        # 模拟离线状态
        self.driver.execute_script("window.navigator.onLine = false")
        
        # 访问页面
        self.driver.get(f'{self.live_server_url}/frontend/user-interface/#/')
        
        # 验证离线提示显示
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "offline-indicator"))
        )
    
    def test_data_persistence(self):
        """测试数据持久性"""
        # 创建数据
        self._test_create_fitness_profile()
        
        # 刷新页面
        self.driver.refresh()
        
        # 验证数据仍然存在
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "profile-data"))
        )
    
    def test_user_session_management(self):
        """测试用户会话管理"""
        # 登录
        self._test_user_login()
        
        # 验证用户信息显示
        user_info = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "user-info"))
        )
        self.assertTrue(user_info.is_displayed())
        
        # 登出
        logout_button = self.driver.find_element(By.CLASS_NAME, "logout-btn")
        logout_button.click()
        
        # 验证重定向到登录页面
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "login-form"))
        )
