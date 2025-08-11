import random
import string
import urllib.parse
from django.utils import timezone
from django.http import HttpRequest


def generate_short_code(length=8):
    """生成短链接代码"""
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(characters) for _ in range(length))
        # 检查是否已存在
        from .models import ShareLink
        if not ShareLink.objects.filter(short_code=code).exists():
            return code


def get_client_ip(request: HttpRequest):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_share_urls(url, title, description):
    """生成各平台的分享URL"""
    encoded_url = urllib.parse.quote(url)
    encoded_title = urllib.parse.quote(title)
    encoded_description = urllib.parse.quote(description)
    
    share_urls = {
        'wechat': {
            'name': '微信',
            'icon': 'fab fa-weixin',
            'color': '#07C160',
            'url': f'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={encoded_url}',
            'type': 'qrcode'
        },
        'weibo': {
            'name': '微博',
            'icon': 'fab fa-weibo',
            'color': '#E6162D',
            'url': f'https://service.weibo.com/share/share.php?url={encoded_url}&title={encoded_title}',
            'type': 'popup'
        },
        'douyin': {
            'name': '抖音',
            'icon': 'fab fa-tiktok',
            'color': '#000000',
            'url': f'https://www.douyin.com/share?url={encoded_url}&title={encoded_title}',
            'type': 'popup'
        },
        'xiaohongshu': {
            'name': '小红书',
            'icon': 'fas fa-book',
            'color': '#FF2442',
            'url': f'https://www.xiaohongshu.com/share?url={encoded_url}&title={encoded_title}',
            'type': 'popup'
        },
        'qq': {
            'name': 'QQ',
            'icon': 'fab fa-qq',
            'color': '#12B7F5',
            'url': f'https://connect.qq.com/widget/shareqq/index.html?url={encoded_url}&title={encoded_title}&desc={encoded_description}',
            'type': 'popup'
        },
        'linkedin': {
            'name': 'LinkedIn',
            'icon': 'fab fa-linkedin',
            'color': '#0077B5',
            'url': f'https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}',
            'type': 'popup'
        },
        'twitter': {
            'name': 'Twitter',
            'icon': 'fab fa-twitter',
            'color': '#1DA1F2',
            'url': f'https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_title}',
            'type': 'popup'
        },
        'facebook': {
            'name': 'Facebook',
            'icon': 'fab fa-facebook',
            'color': '#1877F2',
            'url': f'https://www.facebook.com/sharer/sharer.php?u={encoded_url}',
            'type': 'popup'
        },
        'telegram': {
            'name': 'Telegram',
            'icon': 'fab fa-telegram',
            'color': '#0088CC',
            'url': f'https://t.me/share/url?url={encoded_url}&text={encoded_title}',
            'type': 'popup'
        },
        'whatsapp': {
            'name': 'WhatsApp',
            'icon': 'fab fa-whatsapp',
            'color': '#25D366',
            'url': f'https://wa.me/?text={encoded_title}%20{encoded_url}',
            'type': 'popup'
        },
        'email': {
            'name': '邮件',
            'icon': 'fas fa-envelope',
            'color': '#EA4335',
            'url': f'mailto:?subject={encoded_title}&body={encoded_description}%0A%0A{encoded_url}',
            'type': 'direct'
        },
        'link': {
            'name': '复制链接',
            'icon': 'fas fa-link',
            'color': '#6C757D',
            'url': url,
            'type': 'copy'
        },
        'qrcode': {
            'name': '二维码',
            'icon': 'fas fa-qrcode',
            'color': '#000000',
            'url': f'https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={encoded_url}',
            'type': 'qrcode'
        }
    }
    
    return share_urls


def is_mobile_device(request: HttpRequest):
    """检测是否为移动设备"""
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'windows phone']
    return any(keyword in user_agent for keyword in mobile_keywords)


def get_share_meta_tags(url, title, description, image_url=''):
    """生成分享的meta标签"""
    meta_tags = {
        'og:title': title,
        'og:description': description,
        'og:url': url,
        'og:type': 'website',
        'twitter:card': 'summary_large_image',
        'twitter:title': title,
        'twitter:description': description,
        'twitter:url': url,
    }
    
    if image_url:
        meta_tags['og:image'] = image_url
        meta_tags['twitter:image'] = image_url
    
    return meta_tags


def format_share_count(count):
    """格式化分享数量显示"""
    if count < 1000:
        return str(count)
    elif count < 1000000:
        return f"{count/1000:.1f}K"
    else:
        return f"{count/1000000:.1f}M"
