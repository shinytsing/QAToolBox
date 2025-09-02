from django.utils.dateparse import postgres_interval_re
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import ToolUsageLog
from .serializers import ToolUsageLogSerializer
from .utils import DeepSeekClient
import tempfile
import os
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from django.conf import settings
from django.core.files import File
import logging
import re
from datetime import datetime
from django.utils.text import slugify
import xmind

# 配置日志
logger = logging.getLogger(__name__)


class GenerateTestCasesAPI(APIView):
    permission_classes = []  # 允许匿名访问
    # 增加批量生成的最大批次限制
    MAX_BATCH_COUNT = 10

    # 优化后的默认提示词模板 - 确保用例数量充足，严禁省略，格式清晰
    DEFAULT_PROMPT = """作为资深测试工程师，请根据以下产品需求生成完整的测试用例：

## 重要要求
⚠️ **绝对禁止使用"此处省略"、"等等"、"..."等任何形式的省略表述**
⚠️ **必须生成足够数量的测试用例，不能因为长度限制而减少**
⚠️ **优先保证完整性和数量，速度其次**
⚠️ **每个用例都必须完整，不能中途截断**
⚠️ **严格按照指定格式输出，不要乱**

## 测试用例要求
1. **功能测试**：核心功能、主要业务流程、数据处理
2. **界面测试**：关键UI交互、用户体验、页面跳转
3. **异常测试**：重要错误处理、边界条件、异常流程
4. **安全测试**：基本数据安全、权限控制、输入验证
5. **性能测试**：基本性能指标、响应时间

## 用例结构（每个用例必须包含）
- **用例ID**：TC-模块-序号（如：TC-登录-001）
- **用例标题**：简洁明确的功能描述
- **测试场景**：具体的业务场景
- **前置条件**：系统状态、数据准备
- **测试步骤**：详细的操作步骤（1.2.3...）
- **预期结果**：具体的验证点
- **优先级**：P0/P1/P2（P0最高）
- **测试类型**：功能/界面/异常/安全/性能

## 数量要求（必须满足）
- **每个功能模块至少8个用例，推荐10-15个**
- **总用例数量至少50个，推荐55-60个**
- **用例分布：正向60% + 异常25% + 边界15%**
- **必须覆盖所有核心功能和关键场景**
- **如果遇到token限制，请生成最重要的用例，确保完整性**

## 输出格式（严格按照此格式）
```
# 测试用例文档

## 模块1：[模块名称]
### TC-001：[用例标题]
**测试场景**：[具体场景]
**前置条件**：[系统状态和数据准备]
**测试步骤**：
1. [步骤1]
2. [步骤2]
3. [步骤3]
**预期结果**：[具体验证点]
**优先级**：P0/P1/P2
**测试类型**：[功能/界面/异常/安全/性能]

### TC-002：[用例标题]
[同上格式]

...（继续该模块的其他用例）

## 模块2：[模块名称]
### TC-XXX：[用例标题]
[同上格式]

...（继续其他模块）

## 总结
- 总用例数量：[数字]个
- 功能模块数量：[数字]个
- 测试覆盖情况：[覆盖的功能点]
- 测试类型分布：[正向/异常/边界测试分布]
```

## 完整性保证
- 每个用例必须包含完整的测试步骤
- 预期结果必须具体可验证
- 不能使用任何省略表述
- 严格按照格式输出，不要乱
- 最后必须有总结部分

产品需求：{requirement}

请严格按照上述格式生成完整、充足的测试用例，确保数量和质量都满足要求。
"""

    def post(self, request):
        try:
            start_time = datetime.now()
            # 1. 获取并验证请求参数
            requirement = request.data.get('requirement', '').strip()
            user_prompt = request.data.get('prompt', '').strip()
            # 批量生成参数处理
            is_batch = request.data.get('is_batch', False)
            batch_id = int(request.data.get('batch_id', 0))
            total_batches = int(request.data.get('total_batches', 1))
            print("请求在此:"+requirement,user_prompt)
            logger.info(
                f"用户 {request.user.username} 发起测试用例生成请求，"
                f"需求长度: {len(requirement)}，批量模式: {is_batch}，"
                f"批次: {batch_id + 1}/{total_batches}，"
                f"时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )

            # 参数验证增强
            if not requirement:
                logger.warning("测试用例生成请求缺少requirement参数")
                return Response(
                    {'error': '请输入产品需求内容'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 批量生成参数验证
            if is_batch:
                if total_batches < 1 or total_batches > self.MAX_BATCH_COUNT:
                    return Response(
                        {'error': f'批量生成最大支持{self.MAX_BATCH_COUNT}个批次'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if batch_id < 0 or batch_id >= total_batches:
                    return Response(
                        {'error': f'批次ID {batch_id} 超出有效范围 (0-{total_batches - 1})'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # 处理文件名（增强安全性和可读性）
            # 1. 截取需求前20个字符作为标识
            truncated_req = requirement[:20].strip() if requirement else "default"

            # 2. 使用slugify清理文件名（更安全的字符处理）
            cleaned_req = slugify(truncated_req) or "untitled"

            # 3. 生成时间戳
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 4. 组合文件名（批量模式添加批次标识）
            if is_batch:
                outfile_name = f"{cleaned_req}_{current_time}_batch_{batch_id + 1}_{total_batches}.mm"
            else:
                outfile_name = f"{cleaned_req}_{current_time}.mm"

            # 处理提示词
            final_prompt = user_prompt if user_prompt else self.DEFAULT_PROMPT.format(requirement=requirement)

            # 验证提示词中是否包含需求占位符（如果是自定义提示词）
            if user_prompt and '{requirement}' not in user_prompt:
                logger.warning(f"用户 {request.user.username} 使用的自定义提示词中未包含{{requirement}}占位符")

            # 2. 调用DeepSeek API生成测试用例（传递批量参数）
            try:
                deepseek = DeepSeekClient()
                raw_response = deepseek.generate_test_cases(
                    requirement,
                    final_prompt,
                    is_batch=is_batch,
                    batch_id=batch_id,
                    total_batches=total_batches
                )
                if not raw_response:
                    raise ValueError("未从API获取到有效响应")
            except Exception as e:
                logger.error(f"DeepSeek API调用失败: {str(e)}", exc_info=True)
                return Response(
                    {'error': f'AI接口调用失败: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            print("deepseek返回"+raw_response)
            # 3. 解析API响应为结构化数据
            test_cases = self._parse_test_cases(raw_response)

            # 4. 确保输出目录存在
            output_dir = os.path.join(settings.MEDIA_ROOT, 'tool_outputs')
            os.makedirs(output_dir, exist_ok=True)

            # 5. 创建多种格式文件（FreeMind和XMind）
            try:
                # 生成FreeMind格式文件
                with tempfile.NamedTemporaryFile(
                        suffix='.mm',
                        delete=False,
                        mode='w',
                        encoding='utf-8'
                ) as tmp:
                    # 生成FreeMind XML内容
                    mindmap_xml = self._generate_freemind(test_cases)
                    tmp.write(mindmap_xml)
                    tmp.flush()
                    os.fsync(tmp.fileno())  # 确保数据写入磁盘

                # 生成XMind格式文件
                xmind_test_cases = {"content": raw_response, "title": "AI生成测试用例"}
                xmind_workbook = self._generate_xmind(xmind_test_cases)
                xmind_filename = outfile_name.replace('.mm', '.xmind')
                xmind_path = os.path.join(output_dir, xmind_filename)
                xmind.save(xmind_workbook, xmind_path)
                
                # 生成飞书导入格式文件（Markdown格式）
                feishu_filename = outfile_name.replace('.mm', '_feishu.md')
                feishu_path = os.path.join(output_dir, feishu_filename)
                feishu_content = self._generate_feishu_format(test_cases, raw_response)
                with open(feishu_path, 'w', encoding='utf-8') as f:
                    f.write(feishu_content)

                # 6. 保存到模型（记录批量信息）
                log = ToolUsageLog.objects.create(
                    user=request.user,
                    tool_type='TEST_CASE',
                    input_data=json.dumps({
                        'requirement': requirement,
                        'prompt': final_prompt,
                        'is_batch': is_batch,
                        'batch_id': batch_id,
                        'total_batches': total_batches
                    }, ensure_ascii=False)  # 确保中文正常序列化
                )

                # 使用Django的File类处理文件保存
                with open(tmp.name, 'rb') as f:
                    log.output_file.save(outfile_name, File(f), save=True)

                # 清理临时文件
                os.unlink(tmp.name)

            except Exception as file_err:
                logger.error(f"文件处理失败: {str(file_err)}", exc_info=True)
                # 尝试清理临时文件
                if 'tmp' in locals() and os.path.exists(tmp.name):
                    os.unlink(tmp.name)
                raise Exception(f"文件生成失败: {str(file_err)}")

            # 验证文件是否成功保存
            saved_file_path = os.path.join(output_dir, outfile_name)
            if os.path.exists(saved_file_path):
                logger.info(f"用户 {request.user.username} 测试用例生成成功，文件: {saved_file_path}")
            else:
                logger.warning(f"用户 {request.user.username} 测试用例生成成功，但文件未找到: {saved_file_path}")

            response_data = {
                'download_url': f'/tools/download/{outfile_name}',
                'xmind_download_url': f'/tools/download/{xmind_filename}',
                'log_id': log.id,
                'raw_response': raw_response,
                'test_cases': raw_response,  # 添加前端期望的字段
                'is_batch': is_batch,
                'batch_id': batch_id,
                'total_batches': total_batches,
                'file_name': outfile_name,
                'xmind_file_name': xmind_filename
            }

            # 如果是最后一批，添加打包下载标识
            if is_batch and (batch_id + 1) == total_batches:
                response_data['is_final_batch'] = True
                # 生成批次相关文件的标识前缀，用于前端后续打包下载
                batch_prefix = f"{cleaned_req}_{current_time}_batch_"
                response_data['batch_prefix'] = batch_prefix

            # 计算处理时间并记录
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"用户 {request.user.username} 测试用例生成完成，"
                f"耗时: {processing_time:.2f}秒，"
                f"批次: {batch_id + 1}/{total_batches}"
            )

            return Response(response_data)

        except Exception as e:
            logger.error(
                f"用户 {request.user.username} 测试用例生成失败，"
                f"耗时: {(datetime.now() - start_time).total_seconds():.2f}秒，"
                f"错误: {str(e)}",
                exc_info=True
            )

            return Response(
                {'error': f'服务器处理失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _parse_test_cases(self, raw_response):
        """解析API响应为层级结构，增强鲁棒性"""
        sections = {}
        current_section = None
        current_case = []
        line_number = 0  # 用于错误定位

        try:
            for line in raw_response.split('\n'):
                line_number += 1
                line = line.strip()

                # 跳过空行
                if not line:
                    continue

                # 处理标题行（# 开头）
                if line.startswith('#'):
                    # 如果有未完成的用例，添加到当前章节
                    if current_case and current_section:
                        sections[current_section].append('\n'.join(current_case))
                        current_case = []
                    # 设置新章节（支持多级标题，但统一处理为一级章节）
                    current_section = line.lstrip('# ').strip()
                    # 处理可能的重复章节名
                    if current_section in sections:
                        # 添加计数器避免覆盖
                        counter = 1
                        original_section = current_section
                        while current_section in sections:
                            current_section = f"{original_section}_{counter}"
                            counter += 1
                    sections[current_section] = []
                # 处理列表项（- 或 * 开头）
                elif line.startswith(('-', '*')) and current_section:
                    # 如果有未完成的用例，添加到当前章节
                    if current_case:
                        sections[current_section].append('\n'.join(current_case))
                        current_case = []
                    # 添加新用例的第一行
                    current_case.append(line.lstrip('-* ').strip())
                # 处理用例的多行内容
                elif current_case and current_section:
                    current_case.append(line)

            # 添加最后一个用例
            if current_case and current_section:
                sections[current_section].append('\n'.join(current_case))

            # 如果没有解析到任何章节，创建一个默认章节
            if not sections:
                sections["默认测试场景"] = [raw_response]

            return {
                "title": "AI生成测试用例",
                "structure": sections
            }

        except Exception as e:
            logger.error(f"解析测试用例失败，行号: {line_number}, 错误: {str(e)}")
            # 解析失败时返回原始内容作为备用
            return {
                "title": "AI生成测试用例（解析可能存在问题）",
                "structure": {"解析异常内容": [raw_response]}
            }

    def _generate_freemind(self, test_cases):
        """生成飞书兼容的FreeMind格式XML，增强兼容性处理"""
        try:
            # 避免XML命名空间问题
            ET.register_namespace('', 'http://freemind.sourceforge.net/wiki/index.php/XML')

            # FreeMind根节点
            map_root = ET.Element("map")
            map_root.set("version", "1.0.1")

            # 根主题（对应测试用例标题）
            root_topic = ET.SubElement(map_root, "node")
            root_topic.set("TEXT", self._escape_xml(test_cases.get("title", "AI生成测试用例")))
            root_topic.set("STYLE", "bubble")
            root_topic.set("COLOR", "#000000")  # 黑色根节点

            # 处理不同的数据结构格式
            structure_data = {}
            if isinstance(test_cases, dict):
                if "structure" in test_cases:
                    # 原有的structure格式
                    structure_data = test_cases["structure"]
                else:
                    # 直接的字典格式
                    structure_data = test_cases
            
            # 构建层级结构：场景（一级节点）-> 测试用例（二级节点）
            for scene, cases in structure_data.items():
                if not scene or not cases:  # 跳过空场景或空用例
                    continue

                # 场景节点
                scene_node = ET.SubElement(root_topic, "node")
                scene_node.set("TEXT", self._escape_xml(scene))
                scene_node.set("COLOR", "#FF7F50")  # 珊瑚色场景节点
                scene_node.set("STYLE", "fork")

                # 测试用例节点
                if isinstance(cases, list):
                    for case in cases:
                        if case:  # 跳过空用例
                            case_node = ET.SubElement(scene_node, "node")
                            case_node.set("TEXT", self._escape_xml(case))
                            case_node.set("COLOR", "#4682B4")  # 钢蓝色用例节点
                            case_node.set("STYLE", "bullet")
                elif isinstance(cases, str):
                    # 如果是字符串，直接作为子节点
                    case_node = ET.SubElement(scene_node, "node")
                    case_node.set("TEXT", self._escape_xml(cases))
                    case_node.set("COLOR", "#4682B4")
                    case_node.set("STYLE", "bullet")

            # 格式化XML - 优化飞书兼容性
            rough_string = ET.tostring(map_root, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            
            # 生成标准FreeMind XML格式，确保飞书兼容
            pretty_xml = reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')
            
            # 确保XML声明正确且包含UTF-8编码
            if not pretty_xml.startswith('<?xml'):
                pretty_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + pretty_xml
            elif 'encoding="UTF-8"' not in pretty_xml:
                # 如果XML声明存在但没有UTF-8编码，替换它
                pretty_xml = pretty_xml.replace('<?xml version="1.0"?>', '<?xml version="1.0" encoding="UTF-8"?>')

            return pretty_xml

        except Exception as e:
            logger.error(f"生成FreeMind XML失败: {str(e)}", exc_info=True)
            # 生成失败时返回基础XML结构
            return """<?xml version="1.0" encoding="UTF-8"?>
<map version="1.0.1">
  <node TEXT="测试用例生成失败" STYLE="bubble" COLOR="#FF0000">
    <node TEXT="无法生成有效的测试用例结构" STYLE="bullet" COLOR="#FF0000"/>
  </node>
</map>"""

    def _escape_xml(self, text):
        """XML特殊字符转义，防止XML生成失败"""
        if not text:
            return ""
        return text.replace("&", "&amp;") \
            .replace("<", "&lt;") \
            .replace(">", "&gt;") \
            .replace("\"", "&quot;") \
            .replace("'", "&apos;")

    def _generate_xmind(self, test_cases):
        """生成XMind格式文件，支持飞书导入"""
        try:
            # 创建XMind工作簿
            workbook = xmind.load("test_cases.xmind")
            sheet = workbook.getPrimarySheet()
            root_topic = sheet.getRootTopic()
            
            # 设置根主题
            root_topic.setTitle("AI生成测试用例")
            
            # 解析测试用例内容，构建层级结构
            content = test_cases.get("content", "")
            lines = content.split('\n')
            
            current_section = None
            current_section_topic = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 检测二级标题（## 模块名称）
                if line.startswith('## '):
                    current_section = line[3:].strip()
                    current_section_topic = root_topic.addSubTopic()
                    current_section_topic.setTitle(current_section)
                    
                # 检测用例（以 - 开头）
                elif line.startswith('- ') and current_section_topic:
                    case_content = line[2:].strip()
                    case_topic = current_section_topic.addSubTopic()
                    case_topic.setTitle(case_content)
                    
                # 检测用例详情（以 * 开头）
                elif line.startswith('* ') and current_section_topic:
                    detail_content = line[2:].strip()
                    if current_section_topic.getSubTopics():
                        last_case = current_section_topic.getSubTopics()[-1]
                        detail_topic = last_case.addSubTopic()
                        detail_topic.setTitle(detail_content)
            
            # 如果没有解析到内容，创建默认结构
            if not root_topic.getSubTopics():
                default_section = root_topic.addSubTopic()
                default_section.setTitle("测试用例")
                default_case = default_section.addSubTopic()
                default_case.setTitle("请查看生成的测试用例内容")
            
            return workbook
            
        except Exception as e:
            logger.error(f"生成XMind文件失败: {str(e)}", exc_info=True)
            # 生成失败时返回基础XMind结构
            workbook = xmind.load("test_cases")
            sheet = workbook.getPrimarySheet()
            root_topic = sheet.getRootTopic()
            root_topic.setTitle("测试用例")
            error_topic = root_topic.addSubTopic()
            error_topic.setTitle("测试用例内容")
            return workbook