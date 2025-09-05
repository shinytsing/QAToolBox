"""
极客工具模块路由
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()
router.register(r'pdf', views.PDFConversionViewSet, basename='pdf-conversion')
router.register(r'crawler', views.WebCrawlerViewSet, basename='web-crawler')
router.register(r'testcase', views.TestCaseGeneratorViewSet, basename='testcase-generator')
router.register(r'formatter', views.CodeFormatterViewSet, basename='code-formatter')
router.register(r'qrcode', views.QRCodeGeneratorViewSet, basename='qrcode-generator')
router.register(r'hash', views.HashGeneratorViewSet, basename='hash-generator')
router.register(r'base64', views.Base64EncoderViewSet, basename='base64-encoder')
router.register(r'analysis', views.DataAnalysisViewSet, basename='data-analysis')

urlpatterns = [
    path('', include(router.urls)),
]
