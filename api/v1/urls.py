from django.urls import path, include
from rest_framework.routers import DefaultRouter

# 导入各模块路由
from .auth import urls as auth_urls
from .fitness import urls as fitness_urls
from .life import urls as life_urls
from .tools import urls as tools_urls
from .social import urls as social_urls
from .share import urls as share_urls
from .admin import urls as admin_urls

# 创建路由器
router = DefaultRouter()

# API v1 路由配置
urlpatterns = [
    # 认证模块
    path('auth/', include(auth_urls)),
    
    # 健身模块
    path('fitness/', include(fitness_urls)),
    
    # 生活工具模块
    path('life/', include(life_urls)),
    
    # 极客工具模块
    path('tools/', include(tools_urls)),
    
    # 社交娱乐模块
    path('social/', include(social_urls)),
    
    # 分享模块
    path('share/', include(share_urls)),
    
    # 管理模块
    path('admin/', include(admin_urls)),
]

# 添加路由器路由
urlpatterns += router.urls
