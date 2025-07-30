from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .utils import DeepSeekClient  # 复用已有的DeepSeek客户端
import base64
import requests  # 用于调用小红书发布接口（如果需要）




# API接口视图
class GenerateRedBookAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1. 验证图片上传
        if 'image' not in request.FILES:
            return Response({'error': '请上传图片'}, status=status.HTTP_400_BAD_REQUEST)

        # 2. 读取图片并转为Base64（用于DeepSeek图像识别）
        image_file = request.FILES['image']
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

        try:
            # 3. 调用DeepSeek接口进行图像识别和文案生成
            deepseek = DeepSeekClient()
            # 注意：DeepSeek的图像识别可能需要特定模型，需确认API参数
            prompt = f"识别图片内容并生成小红书风格的标题和文案，标题要吸引人，文案活泼亲切，带相关话题标签。图片Base64: {image_base64}"
            response = deepseek.generate_redbook_content(prompt)

            # 4. 解析生成结果（假设返回格式为{"title": "...", "content": "..."}）
            # 实际需根据DeepSeek返回格式调整解析逻辑
            result = self.parse_redbook_response(response)

            # 5. 自动发布到小红书（如果有开放API）
            # 这里仅为示例，实际需对接小红书开放平台
            publish_status = "模拟发布成功"  # 替换为真实发布逻辑

            return Response({
                'title': result['title'],
                'content': result['content'],
                'status': publish_status
            })

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def parse_redbook_response(self, raw_response):
        """解析DeepSeek返回的文案，提取标题和内容"""
        # 示例解析逻辑，需根据实际返回格式调整
        lines = [line.strip() for line in raw_response.split('\n') if line.strip()]
        title = lines[0] if lines else "默认标题"
        content = '\n'.join(lines[1:]) if len(lines) > 1 else "默认文案"
        return {'title': title, 'content': content}