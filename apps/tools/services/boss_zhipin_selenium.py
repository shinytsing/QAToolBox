import time
import base64
import logging
from typing import Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from django.core.cache import cache

logger = logging.getLogger(__name__)


class BossZhipinSeleniumService:
    """Boss直聘Selenium服务 - 嵌入式登录"""

    def __init__(self, headless=True, proxy=None):
        self.headless = headless
        self.proxy = proxy
        self.base_url = "https://www.zhipin.com"
        self.driver = None
        self.wait_timeout = 10

    def _init_driver(self) -> bool:
        """初始化WebDriver"""
        try:
            chrome_options = Options()

            if self.headless:
                chrome_options.add_argument("--headless")

            # 设置用户代理
            chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            # 设置窗口大小
            chrome_options.add_argument("--window-size=1200,800")

            # 禁用图片加载以提高性能
            chrome_options.add_argument("--blink-settings=imagesEnabled=false")

            # 禁用GPU加速
            chrome_options.add_argument("--disable-gpu")

            # 禁用沙盒模式
            chrome_options.add_argument("--no-sandbox")

            # 禁用开发者工具
            chrome_options.add_argument("--disable-dev-shm-usage")

            # 设置代理（如果提供）
            if self.proxy:
                chrome_options.add_argument(f"--proxy-server={self.proxy}")

            # 自动下载并设置ChromeDriver
            from selenium.webdriver.chrome.service import Service

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # 设置隐式等待时间
            self.driver.implicitly_wait(5)

            logger.info("WebDriver初始化成功")
            return True

        except Exception as e:
            logger.error(f"WebDriver初始化失败: {str(e)}")
            return False

    def _close_driver(self):
        """关闭WebDriver"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("WebDriver已关闭")
        except Exception as e:
            logger.error(f"关闭WebDriver失败: {str(e)}")

    def _wait_for_element(self, selector: str, timeout: int = None) -> Optional[object]:
        """等待元素出现"""
        if timeout is None:
            timeout = self.wait_timeout

        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            return element
        except TimeoutException:
            logger.warning(f"等待元素超时: {selector}")
            return None
        except Exception as e:
            logger.error(f"等待元素失败: {selector}, 错误: {str(e)}")
            return None

    def _safe_get_text(self, selector: str) -> str:
        """安全获取元素文本"""
        try:
            element = self._wait_for_element(selector, timeout=2)
            return element.text if element else ""
        except Exception:
            return ""

    def get_login_page_url(self, user_id: int) -> Dict:
        """获取Boss直聘登录页面URL，用于iframe嵌入"""
        try:
            # 检查缓存
            cache_key = f"boss_login_url_{user_id}"
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info("使用缓存的登录页面URL")
                return cached_result

            login_url = f"{self.base_url}/web/user/?ka=header-login"

            result = {"success": True, "login_url": login_url, "message": "登录页面URL获取成功"}

            # 缓存结果（10分钟）
            cache.set(cache_key, result, 600)

            return result

        except Exception as e:
            logger.error(f"获取登录页面URL失败: {str(e)}")
            return {"success": False, "message": f"获取登录页面URL失败: {str(e)}"}

    def check_login_status(self, user_id: int) -> Dict:
        """检查登录状态 - 通过检查用户相关元素"""
        try:
            # 初始化WebDriver
            if not self._init_driver():
                return {"success": False, "message": "WebDriver初始化失败"}

            try:
                # 访问Boss直聘主页
                main_url = f"{self.base_url}/web/geek/jobs"
                logger.info(f"正在访问Boss直聘主页: {main_url}")

                self.driver.get(main_url)
                time.sleep(3)

                # 检查登录状态
                login_indicators = [".user-info", ".user-avatar", ".user-name", ".header-user", ".user-menu"]

                is_logged_in = False
                for indicator in login_indicators:
                    try:
                        element = self._wait_for_element(indicator, timeout=2)
                        if element:
                            logger.info(f"找到登录指示器: {indicator}")
                            is_logged_in = True
                            break
                    except Exception:
                        continue

                # 获取页面信息
                page_title = self.driver.title
                current_url = self.driver.current_url

                # 尝试获取用户信息
                user_info = {}
                if is_logged_in:
                    try:
                        # 尝试获取用户名
                        username_element = self._wait_for_element(".user-name", timeout=2)
                        if username_element:
                            user_info["username"] = username_element.text

                        # 尝试获取头像
                        avatar_element = self._wait_for_element(".user-avatar img", timeout=2)
                        if avatar_element:
                            user_info["avatar"] = avatar_element.get_attribute("src")

                    except Exception as e:
                        logger.warning(f"获取用户信息失败: {str(e)}")

                result = {
                    "success": True,
                    "status": "SUCCESS" if is_logged_in else "NOT_LOGGED_IN",
                    "is_logged_in": is_logged_in,
                    "page_title": page_title,
                    "current_url": current_url,
                    "user_info": user_info,
                    "message": "已登录" if is_logged_in else "未登录",
                }

                return result

            finally:
                # 关闭WebDriver
                self._close_driver()

        except Exception as e:
            logger.error(f"检查登录状态失败: {str(e)}")
            return {"success": False, "message": f"检查登录状态失败: {str(e)}"}

    def get_user_token(self, user_id: int) -> Dict:
        """获取用户登录后的token/cookie信息"""
        try:
            # 初始化WebDriver
            if not self._init_driver():
                return {"success": False, "message": "WebDriver初始化失败"}

            try:
                # 访问Boss直聘主页
                main_url = f"{self.base_url}/web/geek/jobs"
                logger.info(f"正在访问Boss直聘主页获取token: {main_url}")

                self.driver.get(main_url)
                time.sleep(3)

                # 检查是否已登录
                login_indicators = [".user-info", ".user-avatar", ".user-name"]
                is_logged_in = False

                for indicator in login_indicators:
                    try:
                        element = self._wait_for_element(indicator, timeout=2)
                        if element:
                            is_logged_in = True
                            break
                    except Exception:
                        continue

                if not is_logged_in:
                    return {"success": False, "message": "用户未登录，无法获取token"}

                # 获取所有cookies
                cookies = self.driver.get_cookies()

                # 获取localStorage和sessionStorage
                local_storage = self.driver.execute_script("return window.localStorage;")
                session_storage = self.driver.execute_script("return window.sessionStorage;")

                # 尝试获取特定的token字段
                token_info = {}
                for cookie in cookies:
                    if cookie["name"] in ["__zp_stoken__", "acw_tc", "lastCity", "uid"]:
                        token_info[cookie["name"]] = cookie["value"]

                # 从localStorage获取token
                for key in ["token", "access_token", "auth_token", "__zp_stoken__"]:
                    value = local_storage.get(key)
                    if value:
                        token_info[key] = value

                result = {
                    "success": True,
                    "is_logged_in": True,
                    "cookies": cookies,
                    "local_storage": local_storage,
                    "session_storage": session_storage,
                    "token_info": token_info,
                    "message": "Token获取成功",
                }

                # 缓存token信息（30分钟）
                cache_key = f"boss_user_token_{user_id}"
                cache.set(cache_key, result, 1800)

                return result

            finally:
                # 关闭WebDriver
                self._close_driver()

        except Exception as e:
            logger.error(f"获取用户token失败: {str(e)}")
            return {"success": False, "message": f"获取用户token失败: {str(e)}"}
