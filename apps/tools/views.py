from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from rest_framework.views import APIView
from rest_framework.response import Response
import os
from django.conf import settings
import random
import requests


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

def home_view(request):
    quotes = [
        "Stay hungry, stay foolish. —— Steve Jobs",
        "The only way to do great work is to love what you do. —— Steve Jobs",
        "人生如逆旅，我亦是行人。——苏轼",
        "知之者不如好之者，好之者不如乐之者。——孔子",
        "The best way to predict the future is to invent it. —— Alan Kay",
        "君子生非异也，善假于物也。"
    ]
    quote = random.choice(quotes)
    if not quote:
        quote = "君子生非异也，善假于物也。"
    if request.user.is_authenticated:
        return render(request, 'tool.html', {"quote": quote})
    return render(request, 'home.html', {"quote": quote})

def get_music(request):
    # 示例：返回一个免费mp3直链
    music_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    return JsonResponse({"music_url": music_url})

def tool_view(request):
    """工具主页面"""
    return render(request, 'tool.html')





