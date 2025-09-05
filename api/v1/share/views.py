"""
分享模块视图
"""
import uuid
import hashlib
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from api.response import APIResponse, APIErrorCodes
from api.permissions import IsAuthenticated
from .serializers import (
    ShareRecordSerializer, ShareLinkSerializer,
    ShareAnalyticsSerializer, PWAManifestSerializer
)
from apps.share.models import ShareRecord, ShareLink


class ShareRecordViewSet(viewsets.ModelViewSet):
    """分享记录管理"""
    serializer_class = ShareRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ShareRecord.objects.filter(user=self.request.user).order_by('-share_time')
    
    def create(self, request, *args, **kwargs):
        """记录分享行为"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="分享记录已保存"
            )
        return APIResponse.error(
            message="记录失败",
            errors=serializer.errors,
            code=APIErrorCodes.VALIDATION_ERROR
        )
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """获取分享分析数据"""
        user = request.user
        days = int(request.query_params.get('days', 30))
        
        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 获取分享记录
        shares = ShareRecord.objects.filter(
            user=user,
            share_time__range=[start_date, end_date]
        )
        
        # 平台统计
        platform_stats = {}
        for share in shares:
            platform = share.platform
            platform_stats[platform] = platform_stats.get(platform, 0) + 1
        
        # 每日分享统计
        daily_shares = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            count = shares.filter(share_time__date=date).count()
            daily_shares.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        
        # 热门页面
        top_pages = shares.values('page_title', 'page_url').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        analytics_data = {
            'total_shares': shares.count(),
            'platform_stats': platform_stats,
            'daily_shares': daily_shares,
            'top_pages': list(top_pages),
            'click_through_rate': 0.15  # 模拟数据
        }
        
        serializer = ShareAnalyticsSerializer(analytics_data)
        return APIResponse.success(data=serializer.data)


class ShareLinkViewSet(viewsets.ModelViewSet):
    """分享链接管理"""
    serializer_class = ShareLinkSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ShareLink.objects.filter(creator=self.request.user).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """创建分享链接"""
        original_url = request.data.get('original_url')
        
        if not original_url:
            return APIResponse.error(
                message="请提供原始URL",
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        # 生成短码
        short_code = self.generate_short_code(original_url)
        
        # 检查短码是否已存在
        while ShareLink.objects.filter(short_code=short_code).exists():
            short_code = self.generate_short_code(original_url)
        
        # 创建分享链接
        share_link = ShareLink.objects.create(
            creator=request.user,
            original_url=original_url,
            short_code=short_code,
            title=request.data.get('title', ''),
            description=request.data.get('description', ''),
            expires_at=request.data.get('expires_at')
        )
        
        serializer = self.get_serializer(share_link)
        return APIResponse.success(
            data=serializer.data,
            message="分享链接创建成功"
        )
    
    def generate_short_code(self, url):
        """生成短码"""
        # 使用URL和当前时间戳生成短码
        content = f"{url}{datetime.now().timestamp()}"
        hash_object = hashlib.md5(content.encode())
        return hash_object.hexdigest()[:8]
    
    @action(detail=True, methods=['get'])
    def redirect(self, request, pk=None):
        """重定向到原始URL"""
        share_link = self.get_object()
        
        # 检查链接是否有效
        if not share_link.is_active:
            return APIResponse.error(
                message="分享链接已失效",
                code=APIErrorCodes.NOT_FOUND
            )
        
        if share_link.expires_at and share_link.expires_at < datetime.now():
            return APIResponse.error(
                message="分享链接已过期",
                code=APIErrorCodes.NOT_FOUND
            )
        
        # 增加点击次数
        share_link.click_count += 1
        share_link.save()
        
        return APIResponse.success(
            data={'redirect_url': share_link.original_url},
            message="重定向成功"
        )
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """切换链接激活状态"""
        share_link = self.get_object()
        share_link.is_active = not share_link.is_active
        share_link.save()
        
        status_text = "激活" if share_link.is_active else "禁用"
        return APIResponse.success(
            message=f"分享链接已{status_text}"
        )


class PWAViewSet(viewsets.ViewSet):
    """PWA支持"""
    permission_classes = []
    
    @action(detail=False, methods=['get'])
    def manifest(self, request):
        """获取PWA清单文件"""
        manifest_data = {
            'name': 'QAToolBox',
            'short_name': 'QAToolBox',
            'description': '一个综合性的工具集合平台',
            'start_url': '/',
            'display': 'standalone',
            'background_color': '#ffffff',
            'theme_color': '#007bff',
            'icons': [
                {
                    'src': '/static/img/icon-192x192.png',
                    'sizes': '192x192',
                    'type': 'image/png'
                },
                {
                    'src': '/static/img/icon-512x512.png',
                    'sizes': '512x512',
                    'type': 'image/png'
                }
            ]
        }
        
        return JsonResponse(manifest_data)
    
    @action(detail=False, methods=['get'])
    def service_worker(self, request):
        """获取Service Worker文件"""
        service_worker_js = """
const CACHE_NAME = 'qatoolbox-v1';
const urlsToCache = [
    '/',
    '/static/css/main.css',
    '/static/js/main.js',
    '/static/img/icon-192x192.png',
    '/static/img/icon-512x512.png'
];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                if (response) {
                    return response;
                }
                return fetch(event.request);
            }
        )
    );
});
"""
        return HttpResponse(service_worker_js, content_type='application/javascript')


class ShareWidgetViewSet(viewsets.ViewSet):
    """分享组件"""
    permission_classes = []
    
    @action(detail=False, methods=['get'])
    def platforms(self, request):
        """获取支持的分享平台"""
        platforms = [
            {
                'key': 'wechat',
                'name': '微信',
                'icon': 'fab fa-weixin',
                'color': '#07C160'
            },
            {
                'key': 'weibo',
                'name': '微博',
                'icon': 'fab fa-weibo',
                'color': '#E6162D'
            },
            {
                'key': 'douyin',
                'name': '抖音',
                'icon': 'fab fa-tiktok',
                'color': '#000000'
            },
            {
                'key': 'xiaohongshu',
                'name': '小红书',
                'icon': 'fas fa-book',
                'color': '#FF2442'
            },
            {
                'key': 'qq',
                'name': 'QQ',
                'icon': 'fab fa-qq',
                'color': '#12B7F5'
            },
            {
                'key': 'linkedin',
                'name': 'LinkedIn',
                'icon': 'fab fa-linkedin',
                'color': '#0077B5'
            },
            {
                'key': 'twitter',
                'name': 'Twitter',
                'icon': 'fab fa-twitter',
                'color': '#1DA1F2'
            },
            {
                'key': 'facebook',
                'name': 'Facebook',
                'icon': 'fab fa-facebook',
                'color': '#1877F2'
            }
        ]
        
        return APIResponse.success(data=platforms)
    
    @action(detail=False, methods=['post'])
    def generate_urls(self, request):
        """生成分享URL"""
        url = request.data.get('url')
        title = request.data.get('title', '')
        description = request.data.get('description', '')
        
        if not url:
            return APIResponse.error(
                message="请提供要分享的URL",
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        # 生成各平台的分享URL
        share_urls = {}
        
        # 微信二维码
        share_urls['wechat'] = {
            'name': '微信',
            'icon': 'fab fa-weixin',
            'color': '#07C160',
            'url': f'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={url}',
            'type': 'qrcode'
        }
        
        # 微博
        share_urls['weibo'] = {
            'name': '微博',
            'icon': 'fab fa-weibo',
            'color': '#E6162D',
            'url': f'https://service.weibo.com/share/share.php?url={url}&title={title}',
            'type': 'popup'
        }
        
        # 抖音
        share_urls['douyin'] = {
            'name': '抖音',
            'icon': 'fab fa-tiktok',
            'color': '#000000',
            'url': f'https://www.douyin.com/share?url={url}&title={title}',
            'type': 'popup'
        }
        
        # 小红书
        share_urls['xiaohongshu'] = {
            'name': '小红书',
            'icon': 'fas fa-book',
            'color': '#FF2442',
            'url': f'https://www.xiaohongshu.com/share?url={url}&title={title}',
            'type': 'popup'
        }
        
        # QQ
        share_urls['qq'] = {
            'name': 'QQ',
            'icon': 'fab fa-qq',
            'color': '#12B7F5',
            'url': f'https://connect.qq.com/widget/shareqq/index.html?url={url}&title={title}&desc={description}',
            'type': 'popup'
        }
        
        # LinkedIn
        share_urls['linkedin'] = {
            'name': 'LinkedIn',
            'icon': 'fab fa-linkedin',
            'color': '#0077B5',
            'url': f'https://www.linkedin.com/sharing/share-offsite/?url={url}',
            'type': 'popup'
        }
        
        # Twitter
        share_urls['twitter'] = {
            'name': 'Twitter',
            'icon': 'fab fa-twitter',
            'color': '#1DA1F2',
            'url': f'https://twitter.com/intent/tweet?url={url}&text={title}',
            'type': 'popup'
        }
        
        # Facebook
        share_urls['facebook'] = {
            'name': 'Facebook',
            'icon': 'fab fa-facebook',
            'color': '#1877F2',
            'url': f'https://www.facebook.com/sharer/sharer.php?u={url}',
            'type': 'popup'
        }
        
        return APIResponse.success(data=share_urls)
