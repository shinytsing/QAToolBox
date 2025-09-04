import json
import random
import time
from typing import Dict, List, Optional

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

import requests

from ..models import JobApplication, JobSearchProfile, JobSearchRequest
from .boss_zhipin_api import BossZhipinAPI


class JobSearchService:
    """求职服务主类"""

    def __init__(self, use_selenium=True):
        self.boss_api = BossZhipinAPI(use_selenium=use_selenium)

    def generate_qr_code(self, user_id: int) -> Dict:
        """生成Boss直聘登录二维码"""
        try:
            # 检查是否已有有效的二维码
            cache_key = f"boss_qr_code_{user_id}"
            existing_qr = cache.get(cache_key)

            if existing_qr:
                # 检查二维码是否还在有效期内（5分钟内）
                if time.time() - existing_qr.get("created_at", 0) < 300:
                    return {
                        "success": True,
                        "qr_code_image": existing_qr.get("qr_code_image"),
                        "qr_code_url": existing_qr.get("qr_code_url"),
                        "qr_code_id": existing_qr.get("qr_code_id"),
                        "message": "使用现有二维码",
                        "is_cached": True,
                    }

            # 生成新的二维码
            result = self.boss_api.generate_qr_code(user_id)
            if result.get("success"):
                # 将二维码信息缓存到Redis，设置过期时间为5分钟
                cache_data = {
                    "qr_code_id": result["qr_code_id"],
                    "qr_code_url": result["qr_code_url"],
                    "qr_code_image": result["qr_code_image"],
                    "created_at": time.time(),
                }
                cache.set(cache_key, cache_data, 300)  # 5分钟过期

                # 添加缓存标识
                result["is_cached"] = False

            return result
        except Exception as e:
            return {"success": False, "message": f"生成二维码失败: {str(e)}"}

    def check_qr_login_status(self, user_id: int) -> Dict:
        """检查二维码登录状态"""
        try:
            # 从缓存获取二维码信息
            cache_key = f"boss_qr_code_{user_id}"
            qr_info = cache.get(cache_key)

            if not qr_info:
                return {"success": False, "message": "二维码已过期，请重新生成"}

            result = self.boss_api.check_qr_login_status(qr_info["qr_code_id"])

            if result.get("success") and result.get("status") == "SUCCESS":
                # 登录成功，清除缓存
                cache.delete(cache_key)

                # 保存登录状态到用户缓存
                login_cache_key = f"boss_login_{user_id}"
                cache.set(
                    login_cache_key,
                    {"is_logged_in": True, "login_time": time.time(), "user_info": result.get("user_info", {})},
                    3600,
                )  # 1小时过期

            return result
        except Exception as e:
            return {"success": False, "message": f"检查登录状态失败: {str(e)}"}

    def get_login_status(self, user_id: int) -> Dict:
        """获取登录状态"""
        try:
            # 检查缓存中的登录状态
            cache_key = f"boss_login_{user_id}"
            login_info = cache.get(cache_key)

            if login_info and login_info.get("is_logged_in"):
                return {
                    "success": True,
                    "is_logged_in": True,
                    "login_time": login_info.get("login_time"),
                    "user_info": login_info.get("user_info", {}),
                }

            return {"success": True, "is_logged_in": False}
        except Exception as e:
            return {"success": False, "message": f"获取登录状态失败: {str(e)}"}

    def logout(self, user_id: int) -> Dict:
        """退出登录"""
        try:
            self.boss_api.logout()

            # 清除缓存
            cache.delete(f"boss_qr_code_{user_id}")
            cache.delete(f"boss_login_{user_id}")

            return {"success": True, "message": "退出登录成功"}
        except Exception as e:
            return {"success": False, "message": f"退出登录失败: {str(e)}"}

    # Selenium相关方法
    def get_login_page_url(self, user_id: int) -> Dict:
        """获取Boss直聘登录页面URL用于iframe嵌入"""
        try:
            return self.boss_api.get_login_page_url(user_id)
        except Exception as e:
            return {"success": False, "message": f"获取登录页面URL失败: {str(e)}"}

    def check_login_status_with_selenium(self, user_id: int) -> Dict:
        """使用Selenium检查登录状态"""
        try:
            result = self.boss_api.check_login_status_with_selenium(user_id)

            if result.get("success") and result.get("is_logged_in"):
                # 登录成功，保存登录状态到用户缓存
                login_cache_key = f"boss_login_{user_id}"
                cache.set(
                    login_cache_key, {"is_logged_in": True, "login_time": time.time(), "login_method": "selenium"}, 3600
                )  # 1小时过期

            return result
        except Exception as e:
            return {"success": False, "message": f"检查登录状态失败: {str(e)}"}

    def get_user_token_with_selenium(self, user_id: int) -> Dict:
        """获取用户token"""
        try:
            return self.boss_api.get_user_token_with_selenium(user_id)
        except Exception as e:
            return {"success": False, "message": f"获取用户token失败: {str(e)}"}

    def create_job_search_request(self, user, **kwargs) -> JobSearchRequest:
        """创建求职请求"""
        try:
            job_request = JobSearchRequest.objects.create(user=user, **kwargs)
            return job_request
        except Exception as e:
            raise Exception(f"创建求职请求失败: {str(e)}")

    def start_auto_job_search(self, job_request: JobSearchRequest) -> Dict:
        """开始自动求职"""
        try:
            # 更新状态为处理中
            job_request.status = "processing"
            job_request.save()

            # 获取用户资料
            try:
                user_profile = JobSearchProfile.objects.get(user=job_request.user)
            except JobSearchProfile.DoesNotExist:
                job_request.status = "failed"
                job_request.error_message = "请先完善求职者资料"
                job_request.save()
                return {"success": False, "message": "请先完善求职者资料"}

            # 开始搜索和投递
            total_found = 0
            total_applied = 0

            for page in range(1, 6):  # 搜索前5页
                # 搜索职位
                search_result = self.boss_api.search_jobs(
                    job_title=job_request.job_title,
                    location=job_request.location,
                    min_salary=job_request.min_salary,
                    max_salary=job_request.max_salary,
                    job_type=job_request.job_type,
                    experience_level=job_request.experience_level,
                    keywords=job_request.keywords,
                    page=page,
                )

                if not search_result.get("success"):
                    continue

                jobs = search_result["data"]["jobs"]
                total_found += len(jobs)

                # 筛选和投递
                for job in jobs:
                    if total_applied >= job_request.max_applications:
                        break

                    # 计算匹配度
                    match_score = self._calculate_match_score(job, job_request, user_profile)

                    # 如果匹配度达到60%以上，进行投递
                    if match_score >= 60:
                        # 发送联系请求
                        contact_result = self.boss_api.send_contact_request(job["id"])

                        if contact_result.get("success"):
                            # 创建申请记录
                            JobApplication.objects.create(
                                job_search_request=job_request,
                                job_id=job["id"],
                                job_title=job["title"],
                                company_name=job["company"],
                                company_logo=job.get("logo", ""),
                                location=job["location"],
                                salary_range=f"{job['salary_min']}K-{job['salary_max']}K",
                                job_description=job.get("description", ""),
                                requirements=job.get("requirements", []),
                                benefits=job.get("benefits", []),
                                status="contacted",
                                platform="boss",
                                job_url=job["url"],
                                match_score=match_score,
                                match_reasons=self._get_match_reasons(job, job_request, user_profile),
                            )

                            total_applied += 1

                            # 更新用户统计
                            user_profile.total_applications += 1
                            user_profile.save()

                            # 等待间隔时间
                            time.sleep(job_request.application_interval)

                if total_applied >= job_request.max_applications:
                    break

            # 更新请求状态
            job_request.status = "completed"
            job_request.total_jobs_found = total_found
            job_request.total_applications_sent = total_applied
            job_request.success_rate = (total_applied / max(total_found, 1)) * 100
            job_request.completed_at = timezone.now()
            job_request.save()

            return {
                "success": True,
                "message": f"自动求职完成！找到{total_found}个职位，成功投递{total_applied}份简历",
                "total_found": total_found,
                "total_applied": total_applied,
            }

        except Exception as e:
            job_request.status = "failed"
            job_request.error_message = str(e)
            job_request.save()
            return {"success": False, "message": f"自动求职失败: {str(e)}"}

    def _calculate_match_score(self, job: Dict, job_request: JobSearchRequest, user_profile: JobSearchProfile) -> float:
        """计算职位匹配度"""
        score = 0

        # 薪资匹配度 (30%)
        job_salary_avg = (job["salary_min"] + job["salary_max"]) / 2
        request_salary_avg = (job_request.min_salary + job_request.max_salary) / 2

        if job_salary_avg >= job_request.min_salary and job_salary_avg <= job_request.max_salary:
            score += 30
        elif job_salary_avg >= job_request.min_salary * 0.8:
            score += 20
        elif job_salary_avg >= job_request.min_salary * 0.6:
            score += 10

        # 地点匹配度 (25%)
        if job["location"] in job_request.location:
            score += 25
        elif any(city in job["location"] for city in user_profile.preferred_locations):
            score += 15

        # 经验匹配度 (20%)
        experience_match = {
            "fresh": ["应届生", "无经验"],
            "1-3": ["1-3年", "初级"],
            "3-5": ["3-5年", "中级"],
            "5-10": ["5-10年", "高级"],
            "10+": ["10年以上", "专家"],
        }

        if job_request.experience_level in experience_match:
            if any(exp in str(job.get("experience", "")) for exp in experience_match[job_request.experience_level]):
                score += 20

        # 技能匹配度 (15%)
        user_skills = set(user_profile.skills)
        job_requirements = set(job.get("requirements", []))
        if user_skills and job_requirements:
            skill_match = len(user_skills.intersection(job_requirements)) / len(job_requirements)
            score += skill_match * 15

        # 公司规模匹配度 (10%)
        if job.get("company_size") in ["1000-9999人", "10000人以上"]:
            score += 10

        return min(100, score)

    def _get_match_reasons(self, job: Dict, job_request: JobSearchRequest, user_profile: JobSearchProfile) -> List[str]:
        """获取匹配原因"""
        reasons = []

        # 薪资匹配
        job_salary_avg = (job["salary_min"] + job["salary_max"]) / 2
        if job_salary_avg >= job_request.min_salary:
            reasons.append("薪资符合期望")

        # 地点匹配
        if job["location"] in job_request.location:
            reasons.append("工作地点符合")

        # 技能匹配
        user_skills = set(user_profile.skills)
        job_requirements = set(job.get("requirements", []))
        if user_skills and job_requirements:
            common_skills = user_skills.intersection(job_requirements)
            if common_skills:
                reasons.append(f'技能匹配: {", ".join(list(common_skills)[:3])}')

        return reasons

    def get_job_search_statistics(self, user) -> Dict:
        """获取求职统计信息"""
        try:
            # 获取最近的求职请求
            recent_requests = JobSearchRequest.objects.filter(user=user).order_by("-created_at")[:10]

            # 获取最近的申请记录
            recent_applications = JobApplication.objects.filter(job_search_request__user=user).order_by("-application_time")[
                :20
            ]

            # 计算统计数据
            total_requests = JobSearchRequest.objects.filter(user=user).count()
            total_applications = JobApplication.objects.filter(job_search_request__user=user).count()
            total_interviews = JobApplication.objects.filter(
                job_search_request__user=user, status__in=["contacted", "interview"]
            ).count()
            total_offers = JobApplication.objects.filter(job_search_request__user=user, status="accepted").count()

            # 成功率计算
            response_rate = (total_interviews / max(total_applications, 1)) * 100
            offer_rate = (total_offers / max(total_applications, 1)) * 100

            return {
                "total_requests": total_requests,
                "total_applications": total_applications,
                "total_interviews": total_interviews,
                "total_offers": total_offers,
                "response_rate": round(response_rate, 2),
                "offer_rate": round(offer_rate, 2),
                "recent_requests": recent_requests,
                "recent_applications": recent_applications,
            }

        except Exception as e:
            return {
                "error": str(e),
                "total_requests": 0,
                "total_applications": 0,
                "total_interviews": 0,
                "total_offers": 0,
                "response_rate": 0,
                "offer_rate": 0,
                "recent_requests": [],
                "recent_applications": [],
            }
