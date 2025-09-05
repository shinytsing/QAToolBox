import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class SimpleTestAPI(APIView):
    permission_classes = []  # 允许匿名访问

    def post(self, request):
        try:
            requirement = request.data.get("requirement", "test")

            # 直接调用 DeepSeek API
            api_key = "sk-c4a84c8bbff341cbb3006ecaf84030fe"
            url = "https://api.deepseek.com/v1/chat/completions"

            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": f"为'{requirement}'生成5个简单测试用例"}],
                "max_tokens": 1000,
                "temperature": 0.1,
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return Response({"success": True, "content": content, "requirement": requirement})
            else:
                return Response(
                    {"success": False, "error": f"API调用失败: {response.status_code}", "response": response.text},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        except Exception as e:

            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
