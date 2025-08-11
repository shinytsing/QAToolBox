"""
渐进式验证码服务
根据用户验证失败次数，提供不同难度和类型的验证码
"""
import random
import json
import time
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import uuid


class ProgressiveCaptchaService:
    """渐进式验证码服务类"""
    
    # 验证码类型配置 - 简化版
    CAPTCHA_LEVELS = {
        0: {
            'type': 'simple_math',
            'name': '数学验证码',
            'difficulty': 'easy',
            'description': '数学验证码'
        }
    }
    
    def __init__(self):
        self.max_failures = 3  # 最大失败次数
        self.reset_time = 180  # 3分钟后重置失败计数
        self.lock_duration = 180  # 锁定3分钟
    
    def get_user_failure_info(self, session_key):
        """获取用户验证失败信息"""
        cache_key = f'captcha_failures_{session_key}'
        failure_info = cache.get(cache_key, {
            'count': 0,
            'level': 0,
            'last_failure': None,
            'locked_until': None
        })
        return failure_info
    
    def record_failure(self, session_key):
        """记录验证失败 - 简化版"""
        failure_info = self.get_user_failure_info(session_key)
        current_time = timezone.now()
        
        # 如果距离上次失败超过重置时间，重置计数
        if failure_info.get('last_failure'):
            last_failure = timezone.datetime.fromisoformat(failure_info['last_failure'])
            if current_time - last_failure > timedelta(seconds=self.reset_time):
                failure_info = {'count': 0, 'level': 0, 'last_failure': None, 'locked_until': None}
        
        failure_info['count'] += 1
        failure_info['last_failure'] = current_time.isoformat()
        
        # 检查是否需要锁定（3次失败后锁定3分钟）
        if failure_info['count'] >= self.max_failures:
            failure_info['locked_until'] = (current_time + timedelta(seconds=self.lock_duration)).isoformat()
        
        # 保存到缓存
        cache_key = f'captcha_failures_{session_key}'
        cache.set(cache_key, failure_info, timeout=self.reset_time)
        
        return failure_info
    
    def record_success(self, session_key):
        """记录验证成功"""
        failure_info = self.get_user_failure_info(session_key)
        
        # 成功后降低验证码级别
        if failure_info['level'] > 0:
            failure_info['level'] = max(0, failure_info['level'] - 1)
        
        failure_info['count'] = 0
        failure_info['locked_until'] = None
        
        # 保存到缓存
        cache_key = f'captcha_failures_{session_key}'
        cache.set(cache_key, failure_info, timeout=self.reset_time)
        
        return failure_info
    
    def is_locked(self, session_key):
        """检查用户是否被锁定"""
        failure_info = self.get_user_failure_info(session_key)
        
        if failure_info.get('locked_until'):
            locked_until = timezone.datetime.fromisoformat(failure_info['locked_until'])
            if timezone.now() < locked_until:
                return True, locked_until
            else:
                # 锁定时间已过，清除锁定状态
                failure_info['locked_until'] = None
                cache_key = f'captcha_failures_{session_key}'
                cache.set(cache_key, failure_info, timeout=self.reset_time)
        
        return False, None
    
    def generate_captcha(self, session_key):
        """根据用户失败级别生成相应的验证码"""
        # 检查是否被锁定
        is_locked, locked_until = self.is_locked(session_key)
        if is_locked:
            return {
                'success': False,
                'message': f'验证失败过多，请在 {locked_until.strftime("%H:%M:%S")} 后再试',
                'locked_until': locked_until.isoformat()
            }
        
        failure_info = self.get_user_failure_info(session_key)
        current_level = failure_info.get('level', 0)
        captcha_config = self.CAPTCHA_LEVELS[current_level]
        
        captcha_id = str(uuid.uuid4())
        
        # 只生成数学验证码
        captcha_data = self._generate_math_captcha(captcha_id)
        
        # 添加级别信息
        captcha_data.update({
            'level': current_level,
            'level_name': captcha_config['name'],
            'level_description': captcha_config['description'],
            'failure_count': failure_info.get('count', 0),
            'max_failures': self.max_failures
        })
        
        return {
            'success': True,
            'data': captcha_data
        }
    
    def _generate_math_captcha(self, captcha_id):
        """生成简单算术验证码"""
        # 生成简单的加减法
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operation = random.choice(['+', '-'])
        
        if operation == '+':
            question = f"{num1} + {num2} = ?"
            answer = num1 + num2
        else:
            # 确保减法结果为正数
            if num1 < num2:
                num1, num2 = num2, num1
            question = f"{num1} - {num2} = ?"
            answer = num1 - num2
        
        # 缓存答案
        cache.set(f'math_captcha_{captcha_id}', str(answer), timeout=600)
        
        return {
            'captcha_id': captcha_id,
            'type': 'simple_math',
            'question': question,
            'instruction': '请计算结果并输入答案'
        }
    

    
    # 移除滑动验证码和文字验证码生成方法
    
    def verify_captcha(self, session_key, captcha_id, captcha_type, user_input):
        """验证用户输入"""
        # 检查是否被锁定
        is_locked, locked_until = self.is_locked(session_key)
        if is_locked:
            return {
                'success': False,
                'message': f'验证失败过多，请在 {locked_until.strftime("%H:%M:%S")} 后再试'
            }
        
        # 只验证数学验证码
        result = self._verify_math_captcha(captcha_id, user_input)
        
        # 记录验证结果
        if result['success']:
            self.record_success(session_key)
        else:
            failure_info = self.record_failure(session_key)
            result['failure_info'] = failure_info
        
        return result
    
    def _verify_math_captcha(self, captcha_id, user_input):
        """验证算术验证码 - 增强版自动判别"""
        correct_answer = cache.get(f'math_captcha_{captcha_id}')
        if not correct_answer:
            return {'success': False, 'message': '验证码已过期，请重新获取'}
        
        # 清理用户输入
        user_input = user_input.strip()
        
        # 检查是否为空
        if not user_input:
            return {'success': False, 'message': '请输入答案'}
        
        try:
            # 尝试直接转换为整数
            user_answer = int(user_input)
            correct_answer_int = int(correct_answer)
            
            if user_answer == correct_answer_int:
                cache.delete(f'math_captcha_{captcha_id}')
                return {'success': True, 'message': '验证成功！答案正确'}
            else:
                # 智能错误提示
                if user_answer > correct_answer_int:
                    hint = '答案偏大了，请重新计算'
                elif user_answer < correct_answer_int:
                    hint = '答案偏小了，请重新计算'
                else:
                    hint = '答案错误，请重新输入'
                
                return {
                    'success': False, 
                    'message': hint,
                    'hint': f'正确答案是 {correct_answer_int}',
                    'user_answer': user_answer,
                    'correct_answer': correct_answer_int
                }
                
        except ValueError:
            # 尝试解析数学表达式
            try:
                # 支持简单的数学表达式，如 "3+5", "10-2" 等
                import re
                
                # 移除所有空格
                clean_input = re.sub(r'\s+', '', user_input)
                
                # 检查是否包含数学运算符
                if re.search(r'[\+\-\*\/]', clean_input):
                    # 安全地计算表达式
                    allowed_chars = set('0123456789+-*/().')
                    if not all(c in allowed_chars for c in clean_input):
                        return {'success': False, 'message': '输入包含非法字符，请输入纯数字答案'}
                    
                    # 计算表达式
                    try:
                        calculated_answer = eval(clean_input)
                        if calculated_answer == int(correct_answer):
                            cache.delete(f'math_captcha_{captcha_id}')
                            return {'success': True, 'message': '验证成功！计算正确'}
                        else:
                            return {
                                'success': False, 
                                'message': f'计算结果 {calculated_answer} 不正确',
                                'hint': f'正确答案是 {correct_answer}'
                            }
                    except:
                        return {'success': False, 'message': '数学表达式无效，请输入纯数字答案'}
                else:
                    return {'success': False, 'message': '请输入有效的数字答案'}
                    
            except:
                return {'success': False, 'message': '请输入有效的数字答案'}
        
        except Exception as e:
            return {'success': False, 'message': f'输入格式错误: {str(e)}'}
    

    
    # 移除滑动验证码和文字验证码验证方法
