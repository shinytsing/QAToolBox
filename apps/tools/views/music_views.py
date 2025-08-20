"""
音乐相关视图
包含音乐API、音乐搜索、音乐播放等功能
"""

import json
import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings


@login_required
def music_healing(request):
    """音乐疗愈页面"""
    return render(request, 'tools/music_healing.html')


@csrf_exempt
@require_http_methods(["GET"])
def music_api(request):
    """音乐API接口"""
    try:
        # 获取音乐列表
        music_list = [
            {
                'id': 1,
                'title': 'Eternxlkz - SLAY!',
                'artist': 'Eternxlkz',
                'url': '/static/audio/Eternxlkz - SLAY!.flac',
                'duration': '3:45',
                'genre': 'Electronic',
                'mood': 'Energetic'
            },
            {
                'id': 2,
                'title': 'friday',
                'artist': 'Unknown',
                'url': '/static/audio/friday.mp3',
                'duration': '4:20',
                'genre': 'Pop',
                'mood': 'Happy'
            },
            {
                'id': 3,
                'title': 'keshi - 2 soon',
                'artist': 'keshi',
                'url': '/static/audio/keshi - 2 soon.flac',
                'duration': '3:15',
                'genre': 'Indie',
                'mood': 'Melancholic'
            },
            {
                'id': 4,
                'title': 'sunday',
                'artist': 'Unknown',
                'url': '/static/video/sunday.mp4',
                'duration': '5:30',
                'genre': 'Ambient',
                'mood': 'Relaxing'
            }
        ]
        
        return JsonResponse({
            'success': True,
            'music_list': music_list,
            'total_count': len(music_list)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def search_netease_music(keyword):
    """搜索网易云音乐"""
    try:
        # 这里应该调用网易云音乐API
        # 暂时返回模拟数据
        search_results = [
            {
                'id': f'netease_{keyword}_1',
                'title': f'{keyword} - 搜索结果1',
                'artist': '艺术家1',
                'album': '专辑1',
                'duration': '3:30',
                'url': '#'
            },
            {
                'id': f'netease_{keyword}_2',
                'title': f'{keyword} - 搜索结果2',
                'artist': '艺术家2',
                'album': '专辑2',
                'duration': '4:15',
                'url': '#'
            }
        ]
        
        return {
            'success': True,
            'results': search_results,
            'keyword': keyword
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def format_duration(ms):
    """格式化时长"""
    if not ms:
        return "0:00"
    
    seconds = int(ms / 1000)
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    return f"{minutes}:{remaining_seconds:02d}"


@csrf_exempt
@require_http_methods(["GET"])
def next_song_api(request):
    """下一首歌曲API"""
    try:
        # 获取当前播放列表
        current_song_id = request.GET.get('current_id', 1)
        
        # 模拟播放列表
        playlist = [
            {
                'id': 1,
                'title': 'Eternxlkz - SLAY!',
                'artist': 'Eternxlkz',
                'url': '/static/audio/Eternxlkz - SLAY!.flac',
                'duration': '3:45',
                'genre': 'Electronic',
                'mood': 'Energetic'
            },
            {
                'id': 2,
                'title': 'friday',
                'artist': 'Unknown',
                'url': '/static/audio/friday.mp3',
                'duration': '4:20',
                'genre': 'Pop',
                'mood': 'Happy'
            },
            {
                'id': 3,
                'title': 'keshi - 2 soon',
                'artist': 'keshi',
                'url': '/static/audio/keshi - 2 soon.flac',
                'duration': '3:15',
                'genre': 'Indie',
                'mood': 'Melancholic'
            }
        ]
        
        # 找到下一首歌曲
        current_index = None
        for i, song in enumerate(playlist):
            if song['id'] == int(current_song_id):
                current_index = i
                break
        
        if current_index is not None:
            next_index = (current_index + 1) % len(playlist)
            next_song = playlist[next_index]
        else:
            next_song = playlist[0]
        
        return JsonResponse({
            'success': True,
            'next_song': next_song,
            'playlist_info': {
                'total_songs': len(playlist),
                'current_position': current_index + 1 if current_index is not None else 1
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


# 冥想相关视图  
@login_required
def meditation_guide(request):
    """冥想引导师页面"""
    return render(request, 'tools/meditation_guide.html')


@login_required  
def peace_meditation_view(request):
    """和平冥想页面"""
    return render(request, 'tools/peace_meditation.html')
