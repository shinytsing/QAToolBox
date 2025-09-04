import os
import requests
from ratelimit import limits, sleep_and_retry
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from django_ratelimit.decorators import ratelimit
import json  # Added for json.dumps

# 从环境变量获取配置
# 确保在模块导入时加载环境变量
from dotenv import load_dotenv
import os

# 尝试加载 .env 文件
env_paths = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
    os.path.join(os.path.dirname(__file__), ".env"),
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

API_RATE_LIMIT = os.getenv("API_RATE_LIMIT", "10/minute")

# 解析速率限制配置
try:
    RATE_LIMIT_CALLS, RATE_LIMIT_PERIOD = API_RATE_LIMIT.split("/")
    RATE_LIMIT_PERIOD = {"minute": 60, "hour": 3600}[RATE_LIMIT_PERIOD.lower()]
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
            raise ValueError(
                """
DEEPSEEK_API_KEY 未在环境变量中设置！

解决方案：
1. 在项目根目录创建 .env 文件
2. 在 .env 文件中添加：DEEPSEEK_API_KEY=your_actual_api_key_here
3. 或者直接在系统环境变量中设置 DEEPSEEK_API_KEY

获取DeepSeek API密钥：
1. 访问 https://platform.deepseek.com/
2. 注册并登录账户
3. 在控制台中创建API密钥
4. 复制API密钥（格式：sk-xxxxxxxxxxxxxxxxxxxxxxxx）

示例 .env 文件内容：
DEEPSEEK_API_KEY=sk-your-actual-api-key-here
API_RATE_LIMIT=10/minute
            """.strip()
            )

    @sleep_and_retry
    @limits(calls=int(RATE_LIMIT_CALLS), period=int(RATE_LIMIT_PERIOD))
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)),
    )
    def generate_test_cases(
        self, requirement: str, user_prompt: str, is_batch: bool = False, batch_id: int = 0, total_batches: int = 1
    ) -> str:
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
        if not self.api_key or not self.api_key.startswith("sk-"):
            raise ValueError("API密钥未配置或格式不正确")

        # 优化提示词，提高生成效率
        full_prompt = user_prompt.format(requirement=requirement, format="使用Markdown格式，按模块分类")

        # 智能批次说明
        if is_batch:
            batch_note = f"""
## 批次信息
当前批次：{batch_id + 1}/{total_batches}
请专注生成当前批次的完整内容，确保每个用例都完整可执行。
"""
        else:
            batch_note = ""

        # 添加生成优化指令 - 确保完整性和成功率
        optimization_note = """
        ## 生成优化要求 - 严禁省略，确保完整
        1. 优先生成核心功能用例（P0优先级）
        2. 用例步骤要具体可执行，每个步骤都要详细描述
        3. 预期结果要量化可验证，不能模糊表述
        4. 避免重复和冗余内容，但必须完整
        5. 每个模块生成8-12个用例，不能少于8个
        6. 总用例数量50-60个，确保覆盖全面
        7. 绝对禁止使用省略号、等等、此处省略、待补充等任何省略表述
        8. 每个用例必须完整，不能中途截断
        9. 如果内容较长，请分批次生成，确保每批次都完整
        10. 优先保证完整性和质量，速度其次
        11. 如果遇到token限制，请生成最重要的用例，确保完整性
        12. 严禁生成不完整的内容，宁可少生成也要保证完整
        13. 必须以"# 测试用例文档"开头
        """

        full_prompt += batch_note + optimization_note

        # 构建消息列表
        messages = [
            {"role": "system", "content": "专业测试工程师，生成完整测试用例。格式：Markdown，结构清晰。"},
            {"role": "user", "content": full_prompt},
        ]

        # 验证消息格式
        for msg in messages:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                raise ValueError("消息格式不正确")
            if msg["role"] not in ["system", "user", "assistant"]:
                raise ValueError(f"不支持的消息角色: {msg['role']}")
            if not isinstance(msg["content"], str) or not msg["content"].strip():
                raise ValueError("消息内容不能为空")

        # 优化模型参数，使用deepseek-reasoner模型，确保完整性和成功率
        payload = {
            "model": "deepseek-reasoner",  # 使用deepseek-reasoner模型
            "messages": messages,
            "temperature": 0.05,  # 降低温度，提高一致性和完整性
            "max_tokens": 8192,  # 使用最大允许值，确保不超出API限制
            "top_p": 0.9,  # 提高多样性，确保内容完整
            "frequency_penalty": 0.1,  # 轻微惩罚重复内容
            "presence_penalty": 0.1,  # 轻微惩罚重复主题
            "stream": False,
        }

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}

        # 添加调试日志
        print(f"测试用例生成API请求URL: {self.API_BASE_URL}")
        print(f"测试用例生成API密钥: {self.api_key[:10]}...")
        print(f"测试用例生成请求体: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        try:
            response = requests.post(self.API_BASE_URL, headers=headers, json=payload, timeout=self.TIMEOUT)

            print(f"测试用例生成响应状态码: {response.status_code}")
            print(f"测试用例生成响应头: {dict(response.headers)}")

            response.raise_for_status()

            result = response.json()
            print(f"测试用例生成响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")

            if "choices" not in result or not result["choices"]:
                raise Exception("API响应格式错误：缺少choices字段")

            content = result["choices"][0]["message"]["content"]

            # 多次接续生成，确保用例数量充足
            max_continuations = 3  # 最多接续3次
            continuation_count = 0

            while (
                self._is_content_obviously_incomplete(content) or self._needs_more_test_cases(content)
            ) and continuation_count < max_continuations:

                continuation_count += 1
                print(f"正在进行第{continuation_count}次接续生成...")

                # 尝试继续生成
                continuation_content = self._continue_generation(
                    content, full_prompt, is_batch, batch_id, total_batches, continuation_count
                )
                if continuation_content:
                    content += "\n\n" + continuation_content
                else:
                    break

            return content

        except requests.exceptions.HTTPError as e:
            # 详细错误信息
            error_detail = f"HTTP {e.response.status_code}"
            try:
                error_response = e.response.json()
                if "error" in error_response:
                    error_detail += f": {error_response['error'].get('message', '未知错误')}"
                elif "message" in error_response:
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

    def _continue_generation(
        self, initial_result, prompt, is_batch: bool, batch_id: int, total_batches: int, retry_count: int
    ) -> str:
        """
        继续生成内容，确保完整性（优化版本，支持多次重试）
        """
        max_retries = 3  # 最多重试3次

        for attempt in range(max_retries):
            try:
                continuation_prompt = self._generate_continuation_prompt(initial_result, prompt)

                # 根据重试次数调整参数
                temperature = 0.05 + (attempt * 0.02)  # 逐渐增加温度

                payload = {
                    "model": "deepseek-reasoner",  # 使用deepseek-reasoner模型
                    "messages": [
                        {"role": "system", "content": "继续生成测试用例，确保内容完整。"},
                        {"role": "user", "content": continuation_prompt},
                    ],
                    "temperature": temperature,  # 根据重试次数调整
                    "max_tokens": 8192,  # 使用最大允许值
                    "top_p": 0.9,
                    "frequency_penalty": 0.1,  # 轻微惩罚重复
                    "presence_penalty": 0.1,  # 轻微惩罚重复主题
                    "stream": False,
                }

                headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}

                print(f"第{attempt + 1}次尝试继续生成...")

                response = requests.post(self.API_BASE_URL, headers=headers, json=payload, timeout=self.TIMEOUT)
                response.raise_for_status()

                result = response.json()
                continuation = result["choices"][0]["message"]["content"]

                # 检查继续生成的内容是否有效
                if not continuation or len(continuation.strip()) < 100:
                    print(f"第{attempt + 1}次尝试失败：生成内容过短")
                    continue

                # 检查是否包含新的测试用例
                new_test_cases = continuation.count("TC-")
                if new_test_cases < 3:  # 至少要有3个新的测试用例
                    print(f"第{attempt + 1}次尝试失败：新测试用例数量不足({new_test_cases}个)")
                    continue

                print(f"第{attempt + 1}次尝试成功：生成了{new_test_cases}个新测试用例")
                return continuation

            except Exception as e:
                print(f"第{attempt + 1}次尝试失败: {str(e)}")
                if attempt < max_retries - 1:
                    import time

                    time.sleep(2)  # 等待2秒后重试
                    continue
                else:
                    print("所有重试都失败了")
                    return ""

        return ""

    def _generate_continuation_prompt(self, current_content: str, original_prompt: str) -> str:
        """
        生成继续生成的提示词 - 确保完整性和连续性，用例数量充足，格式一致
        """
        # 分析当前内容
        test_case_count = current_content.count("TC-")
        module_count = current_content.count("## ")

        return f"""
请继续生成测试用例，确保内容完整且连续，用例数量充足，格式一致。

当前已生成的内容统计：
- 测试用例数量：{test_case_count}个
- 功能模块数量：{module_count}个
- 平均每个模块用例数：{test_case_count/max(module_count, 1):.1f}个

当前已生成的内容：
{current_content}

请继续生成剩余的测试用例，严格按照以下格式：

```
### TC-XXX：[用例标题]
**测试场景**：[具体场景]
**前置条件**：[系统状态和数据准备]
**测试步骤**：
1. [步骤1]
2. [步骤2]
3. [步骤3]
**预期结果**：[具体验证点]
**优先级**：P0/P1/P2
**测试类型**：[功能/界面/异常/安全/性能]
```

确保：
1. 覆盖所有功能模块，不能遗漏任何重要功能
2. 包含正向、异常、边界测试，比例合理（正向60%，异常25%，边界15%）
3. 用例步骤详细可执行，每个步骤都要具体描述
4. 预期结果具体可验证，不能模糊表述
5. 总用例数量达到50-60个，每个模块至少8个用例
6. 绝对禁止使用省略号、等等、此处省略等任何省略表述
7. 每个用例必须完整，不能中途截断
8. 与前面内容保持连贯性，不能重复已有用例
9. 如果遇到token限制，请生成最重要的用例，确保完整性
10. 严格按照格式输出，不要乱
11. 确保用例编号连续（TC-001, TC-002, ...）
12. 每个用例都要有明确的测试目标
13. 如果是最后一个模块，请添加总结部分

继续生成（确保完整，用例数量充足，格式一致）：
"""

    def _is_content_obviously_incomplete(self, content: str) -> bool:
        """
        检查内容是否明显不完整（严格检查，确保完整性和格式）
        """
        if not content or len(content.strip()) < 500:
            return True

        # 检查是否有明显的未完成标记
        incomplete_marks = ["...", "等等", "此处省略", "待补充", "未完待续", "待完善", "待续", "未完", "待完成"]
        has_incomplete_marks = any(mark in content for mark in incomplete_marks)

        # 检查是否在句子中间突然结束
        lines = content.split("\n")
        last_line = lines[-1].strip() if lines else ""
        ends_abruptly = last_line and not last_line.endswith((".", "。", ":", "：", "!", "！", "?", "？"))

        # 检查是否有足够的测试用例
        test_case_count = content.count("TC-")
        if test_case_count < 20:  # 至少要有20个测试用例
            return True

        # 检查是否有完整的模块结构
        has_modules = "## " in content
        if not has_modules:
            return True

        # 检查是否有完整的用例结构
        has_steps = "测试步骤" in content
        has_expected = "预期结果" in content
        has_scenario = "测试场景" in content
        has_priority = "优先级" in content
        if not (has_steps and has_expected and has_scenario and has_priority):
            return True

        # 检查是否有总结部分
        has_summary = "总结" in content or "## 总结" in content
        if not has_summary:
            return True

        # 检查格式是否正确
        has_proper_format = "### TC-" in content and "**测试场景**" in content
        has_title = "# 测试用例文档" in content
        if not (has_proper_format and has_title):
            return True

        return has_incomplete_marks or ends_abruptly

    def _needs_more_test_cases(self, content: str) -> bool:
        """
        检查是否需要更多测试用例（确保用例数量充足）
        """
        if not content:
            return True

        # 统计测试用例数量
        test_case_count = content.count("TC-")

        # 统计功能模块数量
        module_count = content.count("## ")

        # 检查用例数量是否充足
        if test_case_count < 50:  # 总用例数量少于50个
            return True

        # 检查每个模块是否有足够的用例
        if module_count > 0:
            avg_cases_per_module = test_case_count / module_count
            if avg_cases_per_module < 8:  # 每个模块平均少于8个用例
                return True

        # 检查是否有足够的测试类型覆盖
        has_positive = "正向测试" in content or "正常流程" in content
        has_negative = "异常测试" in content or "异常流程" in content
        has_boundary = "边界测试" in content or "边界值" in content

        if not (has_positive and has_negative and has_boundary):
            return True

        # 检查是否有完整的测试场景
        has_login = "登录" in content or "认证" in content
        has_data = "数据" in content or "CRUD" in content
        has_ui = "界面" in content or "UI" in content or "页面" in content

        # 至少要有两种主要场景
        scenario_count = sum([has_login, has_data, has_ui])
        if scenario_count < 2:
            return True

        # 检查是否有总结部分
        has_summary = "总结" in content or "## 总结" in content
        if not has_summary:
            return True

        return False

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
            "incomplete_marks": [],
        }

        incomplete_marks = ["...", "等等", "此处省略", "待补充"]
        for mark in incomplete_marks:
            if mark in content:
                analysis["incomplete_marks"].append(mark)

        return analysis

    def generate_redbook_content(self, prompt: str) -> str:
        """
        生成小红书内容

        :param prompt: 提示词
        :return: 生成的内容
        """
        if not prompt:
            raise ValueError("提示词不能为空")

        # 验证API密钥
        if not self.api_key or not self.api_key.startswith("sk-"):
            raise ValueError("API密钥未配置或格式不正确")

        # 构建消息列表
        messages = [
            {"role": "system", "content": "专业的小红书内容创作者，擅长创作吸引人的旅游、美食、生活分享内容。"},
            {"role": "user", "content": prompt},
        ]

        # 构建请求载荷
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.8,
            "max_tokens": 4000,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1,
            "stream": False,
        }

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.post(self.API_BASE_URL, headers=headers, json=payload, timeout=self.TIMEOUT)

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return content
            else:
                raise Exception(f"API调用失败: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"生成小红书内容失败: {e}")
            raise

    def generate_content(self, prompt: str) -> str:
        """
        通用内容生成方法

        :param prompt: 提示词
        :return: 生成的内容
        """
        if not prompt:
            raise ValueError("提示词不能为空")

        # 验证API密钥
        if not self.api_key or not self.api_key.startswith("sk-"):
            raise ValueError("API密钥未配置或格式不正确")

        # 构建消息列表
        messages = [
            {"role": "system", "content": "专业的AI助手，擅长生成详细、真实、实用的内容。"},
            {"role": "user", "content": prompt},
        ]

        # 构建请求载荷
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 6000,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1,
            "stream": False,
        }

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.post(self.API_BASE_URL, headers=headers, json=payload, timeout=self.TIMEOUT)

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return content
            else:
                raise Exception(f"API调用失败: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"生成内容失败: {e}")
            raise


def user_ratelimit(view_func):
    """
    用户级别的速率限制装饰器
    """

    @ratelimit(key="user", rate="3/m", method="POST", block=True)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    return wrapper
