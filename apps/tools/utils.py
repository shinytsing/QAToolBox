import os
import requests
from ratelimit import limits, sleep_and_retry
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from django_ratelimit.decorators import ratelimit

# 从环境变量获取配置
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
    TIMEOUT = 600  # 延长超时时间（秒），适应长内容生成
    MAX_RETRY_ATTEMPTS = 3  # 最大续生成次数 - 修复类属性定义位置

    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY 未在环境变量中设置，请检查 .env.py 文件")

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
        生成测试用例，支持批量生成标识

        :param is_batch: 是否为批量生成模式
        :param batch_id: 当前批次ID（从0开始）
        :param total_batches: 总批次数
        """
        if not requirement or not user_prompt:
            raise ValueError("需求内容和提示词模板不能为空")

        # 构建完整提示词，增加批量生成标识
        full_prompt = user_prompt.format(
            requirement=requirement,
            format="请使用Markdown格式输出：# 场景名称 作为一级标题，- 测试用例 作为列表项"
        )

        # 追加详细度要求，批量模式下增加批次说明
        batch_note = f"\n注意：这是批量生成的第 {batch_id + 1}/{total_batches} 部分，请专注当前片段生成完整内容。" if is_batch else ""

        full_prompt += f"""
        请严格按照以下要求生成测试用例：
        1. 每个功能模块至少包含10个测试用例，禁止使用"此处省略"等任何形式的省略表述
        2. 必须覆盖正常场景、边界场景和异常场景，复杂功能需提供更全面覆盖
        3. 每个用例需包含清晰的步骤和具体的预期结果，确保可执行性
        4. 输出内容需完整无遗漏，不要担心内容长度
        {batch_note}
        """

        payload = {
            "model": "deepseek-reasoner",  # 可替换为更大容量模型
            "messages": [
                {"role": "system",
                 "content": "你是专业测试工程师，必须生成完整测试用例集，禁止省略任何内容。每个用例需详细描述测试场景、前置条件、操作步骤和预期结果，使用Markdown格式输出。"},
                {"role": "user", "content": full_prompt}
            ],
            "temperature": 0.4,
            "max_tokens": 65536,  # 根据模型支持的最大值调整
            "stream": False
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = requests.post(
                self.API_BASE_URL,
                json=payload,
                headers=headers,
                timeout=self.TIMEOUT
            )
            response.raise_for_status()
            result = response.json()

            # 检查是否达到令牌限制，如果是则请求继续生成
            if result.get('choices', [{}])[0].get('finish_reason') == 'length':
                # 传递批量参数进行续生成
                return self._continue_generation(
                    result,
                    full_prompt,
                    is_batch=is_batch,
                    batch_id=batch_id,
                    total_batches=total_batches,
                    retry_count=0
                )

            return result['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            error_detail = f"状态码: {response.status_code}" if 'response' in locals() else "无状态码"
            raise Exception(f"API请求失败: {str(e)} ({error_detail})")

    def _continue_generation(self, initial_result, prompt, is_batch: bool, batch_id: int,
                             total_batches: int, retry_count: int) -> str:
        """处理内容被截断的情况，增加重试次数限制"""
        # 超过最大重试次数则返回已生成内容
        if retry_count >= self.MAX_RETRY_ATTEMPTS:
            return initial_result['choices'][0]['message']['content']

        # 获取已生成的内容
        current_content = initial_result['choices'][0]['message']['content']
        # 构建对话历史
        message_history = [
            {"role": "system", "content": "你是专业测试工程师，生成测试用例时需包含场景和具体用例，用Markdown格式输出，禁止省略任何内容"},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": current_content}
        ]

        # 继续生成 payload
        payload = {
            "model": "deepseek-reasoner",
            "messages": message_history,
            "temperature": 0.4,
            "max_tokens": 65536,
            "stream": False
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = requests.post(
                self.API_BASE_URL,
                json=payload,
                headers=headers,
                timeout=self.TIMEOUT
            )
            response.raise_for_status()
            result = response.json()
            additional_content = result['choices'][0]['message']['content']

            # 递归检查是否还需要继续生成（增加重试计数）
            if result.get('choices', [{}])[0].get('finish_reason') == 'length':
                return self._continue_generation(
                    result,
                    prompt,
                    is_batch=is_batch,
                    batch_id=batch_id,
                    total_batches=total_batches,
                    retry_count=retry_count + 1
                )

            return current_content + additional_content
        except Exception as e:
            # 续生成失败时返回已生成内容
            return current_content


# 针对视图的用户级限频装饰器（1分钟最多3次请求）
def user_ratelimit(view_func):
    @ratelimit(key='user', rate='3/m', method='POST', block=True)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    return wrapper