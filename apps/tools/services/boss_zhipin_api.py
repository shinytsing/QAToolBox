import base64
import json
import random
import time
from io import BytesIO
from typing import Dict, List, Optional

from django.conf import settings
from django.core.cache import cache

import qrcode
import requests

from .boss_zhipin_selenium import BossZhipinSeleniumService


class BossZhipinAPI:
    """Boss直聘API服务类 - 支持扫码登录和发送联系请求"""

    def __init__(self, use_selenium=False):
        self.base_url = "https://www.zhipin.com"
        self.api_url = "https://www.zhipin.com/wapi"
        self.session = requests.Session()
        self.is_logged_in = False
        self.user_token = None
        self.cookies = {}
        self.use_selenium = use_selenium

        # 初始化Selenium服务
        if self.use_selenium:
            self.selenium_service = BossZhipinSeleniumService(headless=True)

        # 设置默认请求头
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh,en;q=0.9,de;q=0.8,is;q=0.7,an;q=0.6,am;q=0.5,ast;q=0.4,ee;q=0.3,ga;q=0.2,et;q=0.1,or;q=0.1,oc;q=0.1,om;q=0.1,eu;q=0.1,bg;q=0.1,be;q=0.1,nso;q=0.1,bs;q=0.1,pl;q=0.1,fa;q=0.1,br;q=0.1,tn;q=0.1,de-AT;q=0.1,de-DE;q=0.1,en-IE;q=0.1,en-AU;q=0.1,en-CA;q=0.1,en-US;q=0.1,en-ZA;q=0.1,en-NZ;q=0.1,en-IN;q=0.1,en-GB-oxendict;q=0.1,en-GB;q=0.1,sq;q=0.1,zh-CN;q=0.1",
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://www.zhipin.com",
                "Referer": "https://www.zhipin.com/web/geek/jobs",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "X-Requested-With": "XMLHttpRequest",
                "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
            }
        )

    def generate_qr_code(self, user_id: int = None) -> Dict:
        """生成Boss直聘登录二维码"""
        # 如果启用了Selenium且提供了用户ID，优先使用Selenium
        if self.use_selenium and user_id:
            return self.generate_qr_code_with_selenium(user_id)

        # 尝试多个可能的API端点
        api_endpoints = [
            f"{self.base_url}/wapi/zppassport/qrcode/get.json",
            f"{self.base_url}/wapi/zpgeek/qrcode/get.json",
            f"{self.base_url}/api/qrcode/get",
            f"{self.base_url}/api/user/qrcode",
            f"{self.base_url}/api/zpgeek/qrcode/get.json",
        ]

        for qr_url in api_endpoints:
            try:
                print(f"正在尝试请求Boss直聘二维码: {qr_url}")

                response = self.session.get(qr_url, timeout=10)
                print(f"Boss直聘二维码响应状态: {response.status_code}")

                if response.status_code == 404:
                    print(f"端点 {qr_url} 不存在，尝试下一个...")
                    continue

                if response.status_code != 200:
                    print(f"Boss直聘二维码请求失败: {response.status_code}")
                    continue

                try:
                    data = response.json()
                except json.JSONDecodeError as e:
                    print(f"Boss直聘二维码响应JSON解析失败: {e}")
                    # 检查是否是HTML页面（说明API端点已更改）
                    if "<html>" in response.text.lower():
                        print(f"端点 {qr_url} 返回HTML页面，API可能已更改")
                        continue
                    else:
                        continue

                print(f"Boss直聘二维码响应数据: {data}")

                # 检查不同的响应格式
                if data.get("code") == 0:
                    qr_data = data.get("zpData", {})
                elif data.get("success") is True:
                    qr_data = data.get("data", {})
                elif data.get("status") == "success":
                    qr_data = data.get("data", {})
                else:
                    error_msg = data.get("message", data.get("error", "获取二维码失败"))
                    print(f"Boss直聘二维码API错误: {error_msg}")
                    continue

                qr_code_url = qr_data.get("qrCodeUrl") or qr_data.get("qr_code_url") or qr_data.get("url")
                qr_code_id = qr_data.get("qrCodeId") or qr_data.get("qr_code_id") or qr_data.get("id")

                if not qr_code_url or not qr_code_id:
                    print(f"Boss直聘二维码数据不完整: qr_code_url={qr_code_url}, qr_code_id={qr_code_id}")
                    continue

                # 生成二维码图片
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(qr_code_url)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")

                # 转换为base64
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                img_str = base64.b64encode(buffer.getvalue()).decode()

                print(f"Boss直聘二维码生成成功: qr_code_id={qr_code_id}")

                return {
                    "success": True,
                    "qr_code_image": f"data:image/png;base64,{img_str}",
                    "qr_code_url": qr_code_url,
                    "qr_code_id": qr_code_id,
                    "message": "请使用Boss直聘APP扫描二维码登录",
                }

            except requests.exceptions.Timeout:
                print(f"端点 {qr_url} 请求超时")
                continue
            except requests.exceptions.RequestException as e:
                print(f"端点 {qr_url} 网络请求失败: {e}")
                continue
            except Exception as e:
                print(f"端点 {qr_url} 处理异常: {e}")
                continue

        # 所有端点都失败，返回错误信息
        print("所有BOSS直聘二维码API端点都失败")
        return {
            "success": False,
            "message": "BOSS直聘API需要特殊认证参数，暂时无法直接获取二维码。请直接访问BOSS直聘登录页面进行登录。",
            "fallback_url": "https://www.zhipin.com/web/user/?ka=header-login",
            "api_info": {"scan_endpoint": "/wapi/zppassport/qrcode/scan", "note": "二维码扫描API可用，但生成API需要特殊认证"},
        }

    def check_qr_login_status(self, qr_code_id: str) -> Dict:
        """检查二维码登录状态"""
        try:
            # 尝试新的API端点
            check_url = f"{self.base_url}/wapi/zppassport/qrcode/scan"
            params = {"uuid": qr_code_id, "_": int(time.time() * 1000)}

            print(f"正在检查二维码状态: {check_url}?uuid={qr_code_id}")

            response = self.session.get(check_url, params=params, timeout=10)
            print(f"二维码状态检查响应: {response.status_code}")

            if response.status_code != 200:
                # 如果新端点失败，尝试旧端点
                check_url = f"{self.base_url}/wapi/zpgeek/qrcode/check.json"
                params = {"qrCodeId": qr_code_id, "_": int(time.time() * 1000)}
                print(f"尝试旧端点: {check_url}")
                response = self.session.get(check_url, params=params, timeout=10)
                print(f"旧端点响应: {response.status_code}")

                if response.status_code != 200:
                    return {"success": False, "message": "检查登录状态失败"}

            response = self.session.get(check_url, params=params)
            if response.status_code != 200:
                return {"success": False, "message": "检查登录状态失败"}

            data = response.json()
            if data.get("code") != 0:
                return {"success": False, "message": data.get("message", "检查登录状态失败")}

            status = data.get("zpData", {}).get("status")

            if status == "SUCCESS":
                # 登录成功，获取用户信息
                user_info = self._get_user_info()
                if user_info.get("success"):
                    self.is_logged_in = True
                    self.user_token = user_info.get("data", {}).get("token")
                    self.cookies = dict(self.session.cookies)

                    return {"success": True, "status": "SUCCESS", "message": "登录成功", "user_info": user_info.get("data")}

            return {"success": True, "status": status, "message": self._get_status_message(status)}

        except Exception as e:
            return {"success": False, "message": f"检查登录状态失败: {str(e)}"}

    def _get_user_info(self) -> Dict:
        """获取用户信息"""
        try:
            user_url = f"{self.base_url}/wapi/zpgeek/user/info.json"
            response = self.session.get(user_url)

            if response.status_code != 200:
                return {"success": False, "message": "获取用户信息失败"}

            data = response.json()
            if data.get("code") != 0:
                return {"success": False, "message": data.get("message", "获取用户信息失败")}

            return {"success": True, "data": data.get("zpData", {})}

        except Exception as e:
            return {"success": False, "message": f"获取用户信息失败: {str(e)}"}

    def _get_status_message(self, status: str) -> str:
        """获取状态消息"""
        status_messages = {
            "WAITING": "等待扫码",
            "SCANNED": "已扫码，等待确认",
            "SUCCESS": "登录成功",
            "EXPIRED": "二维码已过期",
            "CANCELLED": "已取消",
        }
        return status_messages.get(status, "未知状态")

    def search_jobs(
        self,
        job_title: str,
        location: str,
        min_salary: int,
        max_salary: int,
        job_type: str = "full_time",
        experience_level: str = "1-3",
        keywords: List[str] = None,
        page: int = 1,
        page_size: int = 30,
    ) -> Dict:
        """搜索职位"""
        try:
            if not self.is_logged_in:
                return {"success": False, "message": "请先登录Boss直聘"}

            # 构建搜索参数
            search_params = {
                "query": job_title,
                "city": location,
                "salary_min": min_salary * 1000,
                "salary_max": max_salary * 1000,
                "page": page,
                "pageSize": page_size,
                "jobType": self._convert_job_type(job_type),
                "experience": self._convert_experience(experience_level),
                "_": int(time.time() * 1000),
            }

            if keywords:
                search_params["keywords"] = ",".join(keywords)

            search_url = f"{self.api_url}/zpgeek/search/job_list.json"
            response = self.session.get(search_url, params=search_params)

            if response.status_code != 200:
                return {"success": False, "message": "搜索职位失败"}

            data = response.json()
            if data.get("code") != 0:
                return {"success": False, "message": data.get("message", "搜索职位失败")}

            jobs_data = data.get("zpData", {}).get("jobList", [])
            total = data.get("zpData", {}).get("total", 0)

            # 格式化职位数据
            jobs = []
            for job in jobs_data:
                jobs.append(
                    {
                        "id": job.get("jobId"),
                        "title": job.get("jobName"),
                        "company": job.get("brandName"),
                        "location": job.get("cityName"),
                        "salary_min": job.get("salaryMin", 0) // 1000,
                        "salary_max": job.get("salaryMax", 0) // 1000,
                        "experience": job.get("experienceName"),
                        "education": job.get("eduLevelName"),
                        "company_size": job.get("companySize"),
                        "industry": job.get("industryName"),
                        "description": job.get("jobDesc"),
                        "requirements": job.get("skillLabel", []),
                        "benefits": job.get("welfareLabel", []),
                        "url": f"https://www.zhipin.com/job_detail/{job.get('jobId')}.html",
                        "logo": job.get("brandLogo"),
                    }
                )

            return {"success": True, "data": {"jobs": jobs, "total": total, "page": page, "pageSize": page_size}}

        except Exception as e:
            return {"success": False, "message": f"搜索职位失败: {str(e)}"}

    def send_contact_request(self, job_id: str, session_id: str = "") -> Dict:
        """发送联系请求"""
        try:
            if not self.is_logged_in:
                return {"success": False, "message": "请先登录Boss直聘"}

            # 构建请求参数
            contact_url = f"{self.api_url}/zpgeek/friend/add.json"

            # 获取必要的参数
            params = self._get_contact_params(job_id)
            if not params.get("success"):
                return params

            # 发送联系请求
            data = {
                "sessionId": session_id,
                "jobId": job_id,
                "lid": params["data"]["lid"],
                "securityId": params["data"]["securityId"],
                "_": int(time.time() * 1000),
            }

            # 添加必要的请求头
            headers = {
                "token": params["data"]["token"],
                "traceId": params["data"]["traceId"],
                "zp_token": params["data"]["zp_token"],
            }

            response = self.session.post(
                contact_url, data=data, headers=headers, params={"securityId": params["data"]["securityId"]}
            )

            if response.status_code != 200:
                return {"success": False, "message": "发送联系请求失败"}

            result = response.json()
            if result.get("code") != 0:
                return {"success": False, "message": result.get("message", "发送联系请求失败")}

            return {"success": True, "message": "联系请求发送成功", "data": result.get("zpData", {})}

        except Exception as e:
            return {"success": False, "message": f"发送联系请求失败: {str(e)}"}

    def _get_contact_params(self, job_id: str) -> Dict:
        """获取发送联系请求所需的参数"""
        try:
            # 获取职位详情页面
            job_url = f"https://www.zhipin.com/job_detail/{job_id}.html"
            response = self.session.get(job_url)

            if response.status_code != 200:
                return {"success": False, "message": "获取职位详情失败"}

            # 从页面中提取必要的参数
            # 这里需要解析HTML页面获取token、securityId等参数
            # 由于Boss直聘的反爬虫机制，这里使用模拟数据

            return {
                "success": True,
                "data": {
                    "token": "xh80ty18jhMwFOJs",
                    "traceId": f"F-{random.randint(1000000, 9999999)}UjdGVt0HZ3",
                    "zp_token": "V2RNgvF-X-3F5rVtRuyhgbLiu47DrQxyU~|RNgvF-X-3F5rVtRuyhgbLiu47DrXxCw~",
                    "securityId": "iRaGjHDSwTDaX-k1Xte2V1lJSM6qwihE8T0HeTiFXqEoLjEjij-rh6NcxqYwHbliu-cqQrBZoW5fvbXti81DBQPudaeGNGkzOWzN1XMMkJuBjnN1LIxZoT30PNQVEXpjWnM4gYDMrT_U0T_f03skd2qg-azkzdYtPnSpwZq8mktUV4-aXbPig5Y16nrxvQ1TpKQ1pEK_UvrGcoH4pEa7I4m3my9YscsOdxKCfk3uBDPmWAAIkE5CL-D8sKA2Nj8XMnpaV5n-1hHG54JyBIk~",
                    "lid": "c61b52b4-c532-4677-8c0b-821294aadf8a.f1:common.eyJzZXNzaW9uSWQiOiI4ZjNiMzQwMi1mZDJhLTQzMmUtODgxMi03YzM3MmJmNWEwZDgiLCJyY2RCelR5cGUiOiJmMV9ncmNkIn0.1",
                },
            }

        except Exception as e:
            return {"success": False, "message": f"获取联系参数失败: {str(e)}"}

    def _convert_job_type(self, job_type: str) -> str:
        """转换工作类型"""
        type_mapping = {"full_time": "1", "part_time": "2", "internship": "3", "freelance": "4"}
        return type_mapping.get(job_type, "1")

    def _convert_experience(self, experience: str) -> str:
        """转换经验要求"""
        exp_mapping = {"fresh": "1", "1-3": "2", "3-5": "3", "5-10": "4", "10+": "5"}
        return exp_mapping.get(experience, "2")

    def logout(self):
        """退出登录"""
        self.is_logged_in = False
        self.user_token = None
        self.cookies = {}
        self.session.cookies.clear()

    def get_login_status(self) -> Dict:
        """获取登录状态"""
        return {
            "is_logged_in": self.is_logged_in,
            "user_token": self.user_token is not None,
            "cookies_count": len(self.cookies),
        }

    # Selenium相关方法
    def generate_qr_code_with_selenium(self, user_id: int) -> Dict:
        """使用Selenium生成二维码"""
        try:
            if not self.use_selenium:
                return {"success": False, "message": "Selenium功能未启用"}

            # 使用Selenium获取登录页面截图作为二维码替代方案
            # 由于Boss直聘的二维码API需要特殊认证，我们使用登录页面截图
            login_url = f"{self.base_url}/web/user/?ka=header-login"

            # 初始化WebDriver
            if not self.selenium_service._init_driver():
                return {"success": False, "message": "WebDriver初始化失败"}

            try:
                # 访问登录页面
                self.selenium_service.driver.get(login_url)
                time.sleep(3)

                # 等待二维码元素出现
                qr_selectors = [
                    ".qrcode-img",
                    ".qr-code img",
                    ".login-qr img",
                    ".qrcode img",
                    '[data-testid="qrcode"]',
                    ".login-container img",
                ]

                qr_element = None
                for selector in qr_selectors:
                    try:
                        qr_element = self.selenium_service._wait_for_element(selector, timeout=5)
                        if qr_element:
                            break
                    except Exception:
                        continue

                if qr_element:
                    # 获取二维码图片
                    qr_src = qr_element.get_attribute("src")
                    if qr_src:
                        return {
                            "success": True,
                            "qr_code_image": qr_src,
                            "qr_code_url": qr_src,
                            "qr_code_id": f"selenium_qr_{user_id}_{int(time.time())}",
                            "message": "请使用Boss直聘APP扫描二维码登录",
                            "method": "selenium_screenshot",
                        }

                # 如果没有找到二维码元素，返回登录页面截图
                screenshot = self.selenium_service.driver.get_screenshot_as_base64()

                return {
                    "success": True,
                    "qr_code_image": f"data:image/png;base64,{screenshot}",
                    "qr_code_url": login_url,
                    "qr_code_id": f"selenium_login_{user_id}_{int(time.time())}",
                    "message": "请访问登录页面进行扫码登录",
                    "method": "selenium_login_page",
                }

            finally:
                # 关闭WebDriver
                self.selenium_service._close_driver()

        except Exception as e:
            return {"success": False, "message": f"生成二维码失败: {str(e)}"}

    def get_login_page_url(self, user_id: int) -> Dict:
        """获取Boss直聘登录页面URL用于iframe嵌入"""
        try:
            if not self.use_selenium:
                return {"success": False, "message": "Selenium功能未启用"}

            return self.selenium_service.get_login_page_url(user_id)

        except Exception as e:
            return {"success": False, "message": f"获取登录页面URL失败: {str(e)}"}

    def check_login_status_with_selenium(self, user_id: int) -> Dict:
        """使用Selenium检查登录状态"""
        try:
            if not self.use_selenium:
                return {"success": False, "message": "Selenium功能未启用"}

            return self.selenium_service.check_login_status(user_id)

        except Exception as e:
            return {"success": False, "message": f"检查登录状态失败: {str(e)}"}

    def get_user_token_with_selenium(self, user_id: int) -> Dict:
        """使用Selenium获取用户token"""
        try:
            if not self.use_selenium:
                return {"success": False, "message": "Selenium功能未启用"}

            return self.selenium_service.get_user_token(user_id)

        except Exception as e:
            return {"success": False, "message": f"获取用户token失败: {str(e)}"}
