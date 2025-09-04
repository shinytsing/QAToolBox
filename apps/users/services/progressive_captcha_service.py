"""
渐进式验证码服务 - 简化版
"""

import json
import random
import time
import uuid
from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone


class ProgressiveCaptchaService:
    """渐进式验证码服务类"""

    def __init__(self):
        self.max_failures = 3
        self.reset_time = 180
        self.lock_duration = 180

    def get_user_failure_info(self, session_key):
        """获取用户验证失败信息"""
        cache_key = f"captcha_failures_{session_key}"
        failure_info = cache.get(cache_key, {"count": 0, "level": 0, "last_failure": None, "locked_until": None})
        return failure_info

    def record_failure(self, session_key):
        """记录验证失败"""
        failure_info = self.get_user_failure_info(session_key)
        failure_info["count"] += 1
        failure_info["last_failure"] = timezone.now().isoformat()

        # 如果失败次数达到阈值，锁定用户
        if failure_info["count"] >= self.max_failures:
            locked_until = timezone.now() + timedelta(seconds=self.lock_duration)
            failure_info["locked_until"] = locked_until.isoformat()

        cache_key = f"captcha_failures_{session_key}"
        cache.set(cache_key, failure_info, timeout=self.reset_time)

        return failure_info

    def record_success(self, session_key):
        """记录验证成功"""
        failure_info = self.get_user_failure_info(session_key)
        failure_info["count"] = 0
        failure_info["level"] = 0
        failure_info["last_failure"] = None
        failure_info["locked_until"] = None

        cache_key = f"captcha_failures_{session_key}"
        cache.set(cache_key, failure_info, timeout=self.reset_time)

        return failure_info

    def is_locked(self, session_key):
        """检查用户是否被锁定"""
        failure_info = self.get_user_failure_info(session_key)

        if failure_info.get("locked_until"):
            locked_until = timezone.datetime.fromisoformat(failure_info["locked_until"])
            if timezone.now() < locked_until:
                return True, locked_until
            else:
                # 锁定时间已过，清除锁定状态
                failure_info["locked_until"] = None
                cache_key = f"captcha_failures_{session_key}"
                cache.set(cache_key, failure_info, timeout=self.reset_time)

        return False, None

    def generate_captcha(self, session_key):
        """生成简单数学验证码"""
        # 检查是否被锁定
        is_locked, locked_until = self.is_locked(session_key)
        if is_locked:
            return {
                "success": False,
                "message": f'验证失败过多，请在 {locked_until.strftime("%H:%M:%S")} 后再试',
                "locked_until": locked_until.isoformat(),
            }

        failure_info = self.get_user_failure_info(session_key)
        captcha_id = str(uuid.uuid4())

        # 生成简单数学题
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operation = random.choice(["+", "-", "*"])

        if operation == "+":
            answer = num1 + num2
            question = f"{num1} + {num2} = ?"
        elif operation == "-":
            answer = num1 - num2
            question = f"{num1} - {num2} = ?"
        else:  # *
            answer = num1 * num2
            question = f"{num1} × {num2} = ?"

        # 存储答案到缓存
        cache_key = f"captcha_answer_{captcha_id}"
        cache.set(cache_key, str(answer), timeout=300)  # 5分钟过期

        captcha_data = {
            "captcha_id": captcha_id,
            "type": "simple_math",
            "question": question,
            "answer": str(answer),
            "level": failure_info.get("level", 0),
            "failure_count": failure_info.get("count", 0),
            "max_failures": self.max_failures,
        }

        return {"success": True, "data": captcha_data}

    def verify_captcha(self, session_key, captcha_id, captcha_type, user_input):
        """验证验证码"""
        try:
            cache_key = f"captcha_answer_{captcha_id}"
            correct_answer = cache.get(cache_key)

            if not correct_answer:
                return {"success": False, "message": "验证码已过期，请重新获取"}

            if str(user_input).strip() == str(correct_answer).strip():
                # 验证成功
                self.record_success(session_key)
                cache.delete(cache_key)  # 删除已使用的验证码
                return {"success": True, "message": "验证成功"}
            else:
                # 验证失败
                self.record_failure(session_key)
                return {"success": False, "message": "答案错误，请重试"}

        except Exception as e:
            return {"success": False, "message": f"验证失败: {str(e)}"}
