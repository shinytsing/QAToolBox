import os
import requests
from ratelimit import limits, sleep_and_retry
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from django_ratelimit.decorators import ratelimit
import json # Added for json.dumps

# 从环境变量获取配置
# 确保在模块导入时加载环境变量
from dotenv import load_dotenv
import os

# 尝试加载 .env 文件
env_paths = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),
    os.path.join(os.path.dirname(__file__), '.env'),
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

API_RATE_LIMIT = os.getenv('API_RATE_LIMIT', '10/minute')

# 解析速率限制配置
try:
    RATE_LIMIT_CALLS, RATE_LIMIT_PERIOD = API_RATE_LIMIT.split('/')
    RATE_LIMIT_PERIOD = {'minute': 60, 'hour': 3600}[RATE_LIMIT_PERIOD.lower()]
except (ValueError, KeyError):
    RATE_LIMIT_CALLS = 10
    RATE_LIMIT_PERIOD = 60


class DeepSeekClient:
    API_BASE_URL = "https://api.deepseek.com/v1/chat/completions"
    TIMEOUT = 120  # 减少超时时间到2分钟，提高响应速度
    MAX_RETRY_ATTEMPTS = 1  # 减少重试次数到1次，提高速度

    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        if not self.api_key:
            raise ValueError("""
DEEPSEEK_API_KEY 未在环境变量中设置！

解决方案：
1. 在项目根目录创建 .env 文件
2. 在 .env 文件中添加：DEEPSEEK_API_KEY=your_actual_api_key_here
3. 或者直接在系统环境变量中设置 DEEPSEEK_API_KEY

示例 .env 文件内容：
DEEPSEEK_API_KEY=sk-your-actual-api-key-here
API_RATE_LIMIT=10/minute
            """.strip())

    @sleep_and_retry
    @limits(calls=int(RATE_LIMIT_CALLS), period=int(RATE_LIMIT_PERIOD))
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError))
    )
    def generate_test_cases(self, requirement: str, user_prompt: str, is_batch: bool = False,
                            batch_id: int = 0, total_batches: int = 1) -> str:
        """
        生成测试用例，支持智能批量生成
        
        :param requirement: 产品需求
        :param user_prompt: 用户提示词模板
        :param is_batch: 是否为批量生成模式
        :param batch_id: 当前批次ID（从0开始）
        :param total_batches: 总批次数
        :return: 生成的测试用例内容
        """
        if not requirement or not user_prompt:
            raise ValueError("需求内容和提示词模板不能为空")

        # 验证API密钥
        if not self.api_key or not self.api_key.startswith('sk-'):
            raise ValueError("API密钥未配置或格式不正确")

        # 优化提示词，提高生成效率
        full_prompt = user_prompt.format(
            requirement=requirement,
            format="使用Markdown格式，按模块分类"
        )

        # 智能批次说明
        if is_batch:
            batch_note = f"""
## 批次信息
当前批次：{batch_id + 1}/{total_batches}
请专注生成当前批次的完整内容，确保每个用例都完整可执行。
"""
        else:
            batch_note = ""

        # 添加生成优化指令
        optimization_note = """
        ## 生成优化要求
        1. 优先生成核心功能用例（P0优先级）
        2. 用例步骤要具体可执行
        3. 预期结果要量化可验证
        4. 避免重复和冗余内容
        5. 每个模块生成8-12个用例
        6. 总用例数量20-30个
        7. 绝对禁止使用省略号、等等、此处省略等表述
        8. 优先保证质量，适度控制数量
        """
        
        full_prompt += batch_note + optimization_note

        # 构建消息列表
        messages = [
            {"role": "system", "content": "专业测试工程师，生成完整测试用例。格式：Markdown，结构清晰。"},
            {"role": "user", "content": full_prompt}
        ]

        # 验证消息格式
        for msg in messages:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                raise ValueError("消息格式不正确")
            if msg['role'] not in ['system', 'user', 'assistant']:
                raise ValueError(f"不支持的消息角色: {msg['role']}")
            if not isinstance(msg['content'], str) or not msg['content'].strip():
                raise ValueError("消息内容不能为空")

        # 优化模型参数，提高响应速度
        payload = {
            "model": "deepseek-chat",  # 使用更快的模型
            "messages": messages,
            "temperature": 0.1,  # 进一步降低温度，提高生成速度
            "max_tokens": 8192,  # 减少token数量，提高速度
            "top_p": 0.8,  # 降低多样性，提高速度
            "frequency_penalty": 0.0,  # 移除惩罚，提高速度
            "presence_penalty": 0.0,  # 移除惩罚，提高速度
            "stream": False
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 添加调试日志
        print(f"测试用例生成API请求URL: {self.API_BASE_URL}")
        print(f"测试用例生成API密钥: {self.api_key[:10]}...")
        print(f"测试用例生成请求体: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        try:
            response = requests.post(
                self.API_BASE_URL,
                headers=headers,
                json=payload,
                timeout=self.TIMEOUT
            )
            
            print(f"测试用例生成响应状态码: {response.status_code}")
            print(f"测试用例生成响应头: {dict(response.headers)}")
            
            response.raise_for_status()
            
            result = response.json()
            print(f"测试用例生成响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if 'choices' not in result or not result['choices']:
                raise Exception("API响应格式错误：缺少choices字段")
            
            content = result['choices'][0]['message']['content']
            
            # 简化内容完整性检查，只在明显不完整时才继续生成
            if self._is_content_obviously_incomplete(content):
                # 只在内容明显不完整时才继续生成
                content = self._continue_generation(content, full_prompt, is_batch, batch_id, total_batches, 0)
            
            return content
            
        except requests.exceptions.HTTPError as e:
            # 详细错误信息
            error_detail = f'HTTP {e.response.status_code}'
            try:
                error_response = e.response.json()
                if 'error' in error_response:
                    error_detail += f": {error_response['error'].get('message', '未知错误')}"
                elif 'message' in error_response:
                    error_detail += f": {error_response['message']}"
            except:
                error_detail += f": {e.response.text[:200]}"
            raise Exception(f"API请求失败: {error_detail}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {str(e)}")
        except KeyError as e:
            raise Exception(f"API响应格式错误: {str(e)}")
        except Exception as e:
            raise Exception(f"生成测试用例时发生错误: {str(e)}")

    def _continue_generation(self, initial_result, prompt, is_batch: bool, batch_id: int,
                            total_batches: int, retry_count: int) -> str:
        """
        继续生成内容，确保完整性（优化版本）
        """
        if retry_count >= self.MAX_RETRY_ATTEMPTS:
            return initial_result
            
        continuation_prompt = self._generate_continuation_prompt(initial_result, prompt)
        
        payload = {
            "model": "deepseek-chat",  # 使用更快的模型
            "messages": [
                {"role": "system", "content": "继续生成测试用例，确保内容完整。"},
                {"role": "user", "content": continuation_prompt}
            ],
            "temperature": 0.05,  # 进一步降低温度
            "max_tokens": 8192,  # 减少token数量
            "top_p": 0.8,
            "stream": False
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = requests.post(
                self.API_BASE_URL,
                headers=headers,
                json=payload,
                timeout=self.TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            continuation = result['choices'][0]['message']['content']
            
            # 合并内容
            full_content = initial_result + "\n\n" + continuation
            
            # 递归检查完整性
            if not self._is_content_complete(full_content) and retry_count < self.MAX_RETRY_ATTEMPTS:
                return self._continue_generation(full_content, prompt, is_batch, batch_id, total_batches, retry_count + 1)
            
            return full_content
            
        except Exception as e:
            # 如果继续生成失败，返回原始内容
            return initial_result

    def _generate_continuation_prompt(self, current_content: str, original_prompt: str) -> str:
        """
        生成继续生成的提示词
        """
        return f"""
请继续生成测试用例，确保内容完整。

当前已生成的内容：
{current_content}

请继续生成剩余的测试用例，确保：
1. 覆盖所有功能模块
2. 包含正向、异常、边界测试
3. 用例步骤详细可执行
4. 预期结果具体可验证
5. 总用例数量充足

继续生成：
"""

    def _is_content_obviously_incomplete(self, content: str) -> bool:
        """
        检查内容是否明显不完整（更宽松的检查）
        """
        if not content or len(content.strip()) < 100:
            return True
            
        # 只检查是否有明显的未完成标记
        incomplete_marks = ["...", "等等", "此处省略", "待补充", "未完待续", "待完善"]
        has_incomplete_marks = any(mark in content for mark in incomplete_marks)
        
        # 检查是否在句子中间突然结束
        lines = content.split('\n')
        last_line = lines[-1].strip() if lines else ""
        ends_abruptly = last_line and not last_line.endswith(('.', '。', ':', '：', '!', '！', '?', '？'))
        
        return has_incomplete_marks or ends_abruptly

    def _is_content_complete(self, content: str) -> bool:
        """
        检查内容是否完整（保留原方法以兼容）
        """
        return not self._is_content_obviously_incomplete(content)

    def _analyze_content(self, content: str) -> dict:
        """
        分析生成的内容
        """
        analysis = {
            "total_length": len(content),
            "has_test_cases": "TC-" in content,
            "has_modules": "## " in content,
            "has_steps": "测试步骤" in content,
            "has_expected_results": "预期结果" in content,
            "has_priority": "优先级" in content,
            "incomplete_marks": []
        }
        
        incomplete_marks = ["...", "等等", "此处省略", "待补充"]
        for mark in incomplete_marks:
            if mark in content:
                analysis["incomplete_marks"].append(mark)
                
        return analysis

    def generate_redbook_content(self, prompt: str) -> str:
        """
        生成小红书内容
        """
        if not prompt or not prompt.strip():
            raise ValueError("提示词不能为空")

        # 验证API密钥
        if not self.api_key or not self.api_key.startswith('sk-'):
            raise ValueError("API密钥未配置或格式不正确")

        # 构建消息列表
        messages = [
            {"role": "system", "content": "专业的小红书内容创作者，生成高质量、有吸引力的内容。"},
            {"role": "user", "content": prompt}
        ]

        # 验证消息格式
        for msg in messages:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                raise ValueError("消息格式不正确")
            if msg['role'] not in ['system', 'user', 'assistant']:
                raise ValueError(f"不支持的消息角色: {msg['role']}")
            if not isinstance(msg['content'], str) or not msg['content'].strip():
                raise ValueError("消息内容不能为空")

        payload = {
            "model": "deepseek-reasoner",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4096,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stream": False
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 添加调试日志
        print(f"小红书内容生成API请求URL: {self.API_BASE_URL}")
        print(f"小红书内容生成API密钥: {self.api_key[:10]}...")
        print(f"小红书内容生成请求体: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        try:
            response = requests.post(
                self.API_BASE_URL,
                headers=headers,
                json=payload,
                timeout=self.TIMEOUT
            )
            
            print(f"小红书内容生成响应状态码: {response.status_code}")
            
            response.raise_for_status()
            
            result = response.json()
            print(f"小红书内容生成响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if 'choices' not in result or not result['choices']:
                raise Exception("API响应格式错误：缺少choices字段")
            
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.HTTPError as e:
            # 详细错误信息
            error_detail = f'HTTP {e.response.status_code}'
            try:
                error_response = e.response.json()
                if 'error' in error_response:
                    error_detail += f": {error_response['error'].get('message', '未知错误')}"
                elif 'message' in error_response:
                    error_detail += f": {error_response['message']}"
            except:
                error_detail += f": {e.response.text[:200]}"
            raise Exception(f"API请求失败: {error_detail}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {str(e)}")
        except KeyError as e:
            raise Exception(f"API响应格式错误: {str(e)}")
        except Exception as e:
            raise Exception(f"生成小红书内容时发生错误: {str(e)}")

    def _generate_text_only_content(self, prompt: str) -> str:
        """
        生成纯文本内容（备用方法）
        """
        payload = {
            "model": "deepseek-reasoner",
            "messages": [
                {"role": "system", "content": "生成简洁、实用的文本内容。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5,
            "max_tokens": 2048,
            "top_p": 0.9,
            "stream": False
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = requests.post(
                self.API_BASE_URL,
                headers=headers,
                json=payload,
                timeout=self.TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            raise Exception(f"生成文本内容时发生错误: {str(e)}")


def user_ratelimit(view_func):
    """
    用户级别的速率限制装饰器
    """
    @ratelimit(key='user', rate='3/m', method='POST', block=True)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper 