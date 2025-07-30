from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
import os
from django.conf import settings


def test_case_generator(request):
    """工具首页"""
    return render(request, 'tools/test_case_generator.html')

def download_file(request, filename):
    """文件下载视图"""
    file_path = os.path.join(settings.MEDIA_ROOT, 'tool_outputs', filename)
    return FileResponse(open(file_path, 'rb'), as_attachment=True)

def redbook_generator(request):
    """工具首页"""
    return render(request, 'tools/redbook_generator.html')





