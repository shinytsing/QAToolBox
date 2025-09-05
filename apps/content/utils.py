import os
import re
from urllib.parse import urljoin, urlparse

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

import requests
from bs4 import BeautifulSoup


def extract_favicon_url(url):
    """
    从网站提取favicon URL
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # 增加超时时间，添加重试机制
        for attempt in range(3):
            try:
                response = requests.get(url, headers=headers, timeout=15, verify=True)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                if attempt == 2:  # 最后一次尝试
                    raise e
                continue

        soup = BeautifulSoup(response.content, "html.parser")

        # 查找favicon链接
        favicon_url = None

        # 1. 查找link标签中的favicon
        favicon_links = soup.find_all("link", rel=re.compile(r"icon|shortcut", re.I))
        for link in favicon_links:
            href = link.get("href")
            if href:
                favicon_url = urljoin(url, href)
                break

        # 2. 如果没有找到，尝试常见的favicon路径
        if not favicon_url:
            common_paths = ["/favicon.ico", "/favicon.png", "/apple-touch-icon.png", "/apple-touch-icon-precomposed.png"]

            for path in common_paths:
                try:
                    test_url = urljoin(url, path)
                    test_response = requests.head(test_url, headers=headers, timeout=8, verify=True)
                    if test_response.status_code == 200:
                        favicon_url = test_url
                        break
                except:
                    continue

        return favicon_url

    except Exception as e:
        print(f"提取favicon失败: {url} - {str(e)}")
        return None


def download_and_save_icon(icon_url, filename):
    """
    下载并保存图标到本地
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # 增加重试机制
        for attempt in range(3):
            try:
                response = requests.get(icon_url, headers=headers, timeout=15, verify=True)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                if attempt == 2:  # 最后一次尝试
                    raise e
                continue

        # 确定文件扩展名
        content_type = response.headers.get("content-type", "")
        if "png" in content_type:
            ext = ".png"
        elif "jpg" in content_type or "jpeg" in content_type:
            ext = ".jpg"
        elif "svg" in content_type:
            ext = ".svg"
        elif "ico" in content_type:
            ext = ".ico"
        else:
            ext = ".png"  # 默认使用png

        # 确保文件名有正确的扩展名
        if not filename.endswith(ext):
            filename += ext

        # 保存文件
        file_path = f"ai_links/icons/{filename}"
        saved_path = default_storage.save(file_path, ContentFile(response.content))

        return saved_path

    except Exception as e:
        print(f"下载图标失败: {icon_url} - {str(e)}")
        return None


def get_domain_from_url(url):
    """
    从URL中提取域名
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return url.replace("https://", "").replace("http://", "").split("/")[0]


def get_default_icon_url(domain):
    """
    获取默认图标URL（使用Google的favicon服务）
    """
    try:
        # 使用Google的favicon服务
        return f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
    except:
        return None
