from django.urls import path

from . import views

app_name = "share"

urlpatterns = [
    # 分享页面重定向
    path("s/<str:short_code>/", views.share_page, name="share_page"),
    # 分享功能
    path("widget/", views.share_widget, name="share_widget"),
    path("record/", views.record_share, name="record_share"),
    path("create-link/", views.create_share_link, name="create_share_link"),
    # 数据看板
    path("dashboard/", views.share_dashboard, name="share_dashboard"),
    path("analytics/", views.share_analytics, name="share_analytics"),
    # PWA支持
    path("manifest.json", views.pwa_manifest, name="pwa_manifest"),
    path("sw.js", views.service_worker, name="service_worker"),
]
