import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import ShareAnalytics, ShareLink, ShareRecord
from .utils import generate_short_code, get_client_ip, get_share_urls


def share_page(request, short_code):
    """分享页面重定向"""
    share_link = get_object_or_404(ShareLink, short_code=short_code, is_active=True)

    # 增加点击次数
    share_link.click_count += 1
    share_link.save()

    # 记录访问统计
    today = timezone.now().date()
    analytics, created = ShareAnalytics.objects.get_or_create(
        date=today, platform="link", defaults={"share_count": 0, "click_count": 0}
    )
    analytics.click_count += 1
    analytics.save()

    return redirect(share_link.original_url)


@login_required
def share_dashboard(request):
    """分享数据看板"""
    user = request.user

    # 获取用户的分享记录
    share_records = ShareRecord.objects.filter(user=user).order_by("-share_time")

    # 分页
    paginator = Paginator(share_records, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # 统计信息
    total_shares = share_records.count()
    platform_stats = share_records.values("platform").annotate(count=Count("platform")).order_by("-count")

    # 最近7天的分享趋势
    from datetime import timedelta

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)

    daily_shares = []
    for i in range(7):
        date = start_date + timedelta(days=i)
        count = share_records.filter(share_time__date=date).count()
        daily_shares.append({"date": date.strftime("%m-%d"), "count": count})

    context = {
        "page_obj": page_obj,
        "total_shares": total_shares,
        "platform_stats": platform_stats,
        "daily_shares": daily_shares,
    }

    return render(request, "share/dashboard.html", context)


@csrf_exempt
@require_http_methods(["POST"])
def record_share(request):
    """记录分享行为"""
    try:
        data = json.loads(request.body)
        platform = data.get("platform")
        page_url = data.get("page_url")
        page_title = data.get("page_title", "")

        if not platform or not page_url:
            return JsonResponse({"error": "缺少必要参数"}, status=400)

        # 获取用户信息
        user = request.user if request.user.is_authenticated else None

        # 创建分享记录
        share_record = ShareRecord.objects.create(
            user=user,
            platform=platform,
            page_url=page_url,
            page_title=page_title,
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        # 更新统计
        today = timezone.now().date()
        analytics, created = ShareAnalytics.objects.get_or_create(
            date=today, platform=platform, defaults={"share_count": 0, "click_count": 0}
        )
        analytics.share_count += 1
        analytics.save()

        return JsonResponse({"success": True, "record_id": share_record.id})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def create_share_link(request):
    """创建分享链接"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            original_url = data.get("url")
            title = data.get("title", "")
            description = data.get("description", "")
            image_url = data.get("image_url", "")

            if not original_url:
                return JsonResponse({"error": "URL不能为空"}, status=400)

            # 生成短链接代码
            short_code = generate_short_code()

            # 创建分享链接
            share_link = ShareLink.objects.create(
                original_url=original_url, short_code=short_code, title=title, description=description, image_url=image_url
            )

            # 生成完整的分享URL
            share_url = request.build_absolute_uri(reverse("share_page", args=[short_code]))

            return JsonResponse({"success": True, "share_link": share_link, "share_url": share_url, "short_code": short_code})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, "share/create_link.html")


def share_widget(request):
    """分享组件页面"""
    current_url = request.build_absolute_uri()
    current_title = request.GET.get("title", "QAToolBox - 多功能工具箱")
    current_description = request.GET.get("description", "发现更多实用工具")
    current_image = request.GET.get("image", "")

    # 生成分享URLs
    share_urls = get_share_urls(current_url, current_title, current_description)

    context = {
        "current_url": current_url,
        "current_title": current_title,
        "current_description": current_description,
        "current_image": current_image,
        "share_urls": share_urls,
    }

    return render(request, "share/widget.html", context)


def share_analytics(request):
    """分享数据分析（管理员功能）"""
    if not request.user.is_staff:
        return JsonResponse({"error": "权限不足"}, status=403)

    # 获取时间范围
    days = int(request.GET.get("days", 7))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days - 1)

    # 获取统计数据
    analytics = ShareAnalytics.objects.filter(date__range=[start_date, end_date]).order_by("date", "platform")

    # 按平台汇总
    platform_summary = {}
    for record in analytics:
        platform = record.get_platform_display()
        if platform not in platform_summary:
            platform_summary[platform] = {"shares": 0, "clicks": 0}
        platform_summary[platform]["shares"] += record.share_count
        platform_summary[platform]["clicks"] += record.click_count

    # 按日期汇总
    daily_summary = {}
    for record in analytics:
        date_str = record.date.strftime("%Y-%m-%d")
        if date_str not in daily_summary:
            daily_summary[date_str] = {"shares": 0, "clicks": 0}
        daily_summary[date_str]["shares"] += record.share_count
        daily_summary[date_str]["clicks"] += record.click_count

    return JsonResponse(
        {"platform_summary": platform_summary, "daily_summary": daily_summary, "analytics": list(analytics.values())}
    )


def pwa_manifest(request):
    """PWA manifest文件"""
    manifest = {
        "name": "QAToolBox - 多功能工具箱",
        "short_name": "QAToolBox",
        "description": "发现更多实用工具，提升工作效率",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#007bff",
        "orientation": "portrait-primary",
        "icons": [
            {"src": "/static/img/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "/static/img/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
    }

    return JsonResponse(manifest, content_type="application/manifest+json")


def service_worker(request):
    """Service Worker文件"""
    sw_content = """
    const CACHE_NAME = 'qatoolbox-v1';
    const urlsToCache = [
        '/',
        '/static/css/base.css',
        '/static/js/share.js'
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
                })
            )
        );
    });
    """

    return HttpResponse(sw_content, content_type="application/javascript")
