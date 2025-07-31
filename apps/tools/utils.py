import os
import requests
from ratelimit import limits, sleep_and_retry
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from django_ratelimit.decorators import ratelimit

# 从环境变量获取配置
# 确保在模块导入时加载环境变量
from dotenv import load_dotenv
import os

# 尝试加载 .env 文件
env_paths = [
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
    TIMEOUT = 300  # 减少超时时间（秒），提高响应速度
    MAX_RETRY_ATTEMPTS = 2  # 减少重试次数，提高速度

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
        5. 确保用例覆盖全面
        6. 每个模块生成10-15个用例
        7. 总用例数量不少于30个
        8. 绝对禁止使用省略号、等等、此处省略等表述
        """
        
        full_prompt += batch_note + optimization_note

        # 优化模型参数，平衡速度和质量
        payload = {
            "model": "deepseek-reasoner",  # 使用支持更大输出的模型
            "messages": [
                {"role": "system",
                 "content": "专业测试工程师，生成完整测试用例。格式：Markdown，结构清晰。"},
                {"role": "user", "content": full_prompt}
            ],
            "temperature": 0.2,  # 降低温度，提高生成速度
            "max_tokens": 32768,  # 使用32K token，平衡速度和完整性
            "top_p": 0.9,  # 降低多样性，提高速度
            "frequency_penalty": 0.0,  # 移除惩罚，提高速度
            "presence_penalty": 0.0,  # 移除惩罚，提高速度
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

            # 获取生成的内容
            generated_content = result['choices'][0]['message']['content']
            
            # 检查内容是否完整
            if not self._is_content_complete(generated_content):
                # 内容不完整，进行续生成
                return self._continue_generation(
                    result,
                    full_prompt,
                    is_batch=is_batch,
                    batch_id=batch_id,
                    total_batches=total_batches,
                    retry_count=0
                )
            
            # 检查是否达到令牌限制
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

            return generated_content
        except requests.exceptions.RequestException as e:
            error_detail = f"状态码: {response.status_code}" if 'response' in locals() else "无状态码"
            raise Exception(f"API请求失败: {str(e)} ({error_detail})")

    def _continue_generation(self, initial_result, prompt, is_batch: bool, batch_id: int,
                             total_batches: int, retry_count: int) -> str:
        """智能续生成，确保内容完整性"""
        # 超过最大重试次数则返回已生成内容
        if retry_count >= self.MAX_RETRY_ATTEMPTS:
            return initial_result['choices'][0]['message']['content']

        # 获取已生成的内容
        current_content = initial_result['choices'][0]['message']['content']
        
        # 智能续生成提示词
        continuation_prompt = self._generate_continuation_prompt(current_content, prompt)
        
        # 构建对话历史
        message_history = [
            {"role": "system", "content": "专业测试工程师，继续生成测试用例，保持格式一致。"},
            {"role": "user", "content": continuation_prompt}
        ]

        # 优化续生成参数，平衡速度和质量
        payload = {
            "model": "deepseek-reasoner",
            "messages": message_history,
            "temperature": 0.2,
            "max_tokens": 32768,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
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

            # 合并内容
            combined_content = current_content + "\n\n" + additional_content

            # 检查内容是否完整
            if not self._is_content_complete(combined_content) and retry_count < self.MAX_RETRY_ATTEMPTS:
                return self._continue_generation(
                    result,
                    prompt,
                    is_batch=is_batch,
                    batch_id=batch_id,
                    total_batches=total_batches,
                    retry_count=retry_count + 1
                )

            # 检查是否达到令牌限制
            if result.get('choices', [{}])[0].get('finish_reason') == 'length' and retry_count < self.MAX_RETRY_ATTEMPTS:
                return self._continue_generation(
                    result,
                    prompt,
                    is_batch=is_batch,
                    batch_id=batch_id,
                    total_batches=total_batches,
                    retry_count=retry_count + 1
                )

            return combined_content
        except Exception as e:
            # 续生成失败时返回已生成内容
            return current_content

    def _generate_continuation_prompt(self, current_content: str, original_prompt: str) -> str:
        """生成智能续生成提示词"""
        # 智能分析当前内容
        analysis = self._analyze_content(current_content)
        
        # 提取关键上下文
        context_lines = current_content.strip().split('\n')
        context = '\n'.join(context_lines[-5:])  # 取最后5行，进一步减少token占用
        
        continuation_prompt = f"""
继续生成测试用例，保持格式一致。

⚠️ **重要要求：绝对禁止省略，必须生成完整内容**

当前状态：{analysis['current_status']}
已完成用例：{analysis['completed_cases']}个
当前模块：{analysis['current_module']}
优先级分布：{analysis['priority_distribution']}

要求：
1. 继续完成当前模块的用例，确保每个用例都完整
2. 保持用例ID格式：TC-模块-序号
3. 步骤要具体可执行，不能省略任何步骤
4. 预期结果要量化验证，不能使用"等等"等表述
5. 优先生成P0优先级用例
6. 每个用例都要详细描述，不能有任何省略
7. 确保生成足够数量的用例（每个模块10-15个）

上下文：{context[-200:] if len(context) > 200 else context}

原始需求：{original_prompt}
        """
        
        return continuation_prompt.strip()

    def _is_content_complete(self, content: str) -> bool:
        """检查生成内容是否完整"""
        if not content:
            return False
        
        # 检查是否以省略号结尾
        if content.strip().endswith('...') or content.strip().endswith('等等'):
            return False
        
        # 检查是否包含省略提示
        omit_indicators = ['此处省略', '省略', '未完待续', '待续', '等等', '...']
        for indicator in omit_indicators:
            if indicator in content:
                return False
        
        # 检查用例数量是否足够
        lines = content.split('\n')
        case_count = sum(1 for line in lines if line.strip().startswith('-') and 'TC-' in line)
        
        # 如果用例数量少于20个，认为不完整
        if case_count < 20:
            return False
        
        # 检查是否有完整的模块结构
        section_count = sum(1 for line in lines if line.strip().startswith('## '))
        if section_count < 1:
            return False
        
        return True

    def _analyze_content(self, content: str) -> dict:
        """智能分析生成内容的状态"""
        lines = content.strip().split('\n')
        
        # 统计信息
        total_lines = len(lines)
        case_count = sum(1 for line in lines if line.strip().startswith('-') and 'TC-' in line)
        
        # 分析模块
        sections = []
        current_section = None
        for line in lines:
            if line.startswith('##'):
                current_section = line.lstrip('# ').strip()
                sections.append(current_section)
        
        # 分析优先级分布
        p0_count = sum(1 for line in lines if 'P0' in line)
        p1_count = sum(1 for line in lines if 'P1' in line)
        p2_count = sum(1 for line in lines if 'P2' in line)
        
        return {
            'current_status': f'已生成{total_lines}行，{case_count}个用例',
            'completed_cases': case_count,
            'current_module': sections[-1] if sections else '未知',
            'priority_distribution': f'P0:{p0_count} P1:{p1_count} P2:{p2_count}'
        }

    def generate_redbook_content(self, prompt: str) -> str:
        """调用DeepSeek接口生成小红书文案（支持图像识别）"""
        # 检查是否包含图像数据
        if "Base64" in prompt:
            # 使用支持图像的模型
            model = "deepseek-vl"
        else:
            # 使用文本模型
            model = "deepseek-chat"  # 使用正确的模型名称
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "你是小红书内容专家，擅长根据图片生成吸引人的标题和文案。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2048,  # 文案不需要太长的token
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
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
                timeout=60  # 文案生成不需要太长时间
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            # 如果图像识别失败，尝试使用纯文本模型
            if "Base64" in prompt:
                # logger.warning(f"图像识别失败，尝试使用纯文本模型: {str(e)}") # logger is not defined in this file
                return self._generate_text_only_content(prompt)
            else:
                raise Exception(f"小红书文案生成失败: {str(e)}")

    def _generate_text_only_content(self, prompt: str) -> str:
        """使用纯文本模型生成内容（当图像识别失败时）"""
        # 移除图像相关的提示词，只保留文本部分
        text_prompt = prompt.replace("Base64", "").replace("image", "图片")
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是小红书内容专家，擅长生成吸引人的标题和文案。"},
                {"role": "user", "content": text_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2048,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
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
                timeout=60
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            raise Exception(f"纯文本生成也失败: {str(e)}")


# 针对视图的用户级限频装饰器（1分钟最多3次请求）
def user_ratelimit(view_func):
    @ratelimit(key='user', rate='3/m', method='POST', block=True)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    return wrapper 