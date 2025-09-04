from django.core.management.base import BaseCommand

from apps.content.models import AILink
from apps.content.utils import download_and_save_icon, extract_favicon_url, get_default_icon_url, get_domain_from_url


class Command(BaseCommand):
    help = "创建预定义的AI友情链接"

    def handle(self, *args, **options):
        # 预定义的AI链接数据
        ai_links_data = [
            {
                "name": "Midjourney",
                "url": "https://www.midjourney.com/account",
                "category": "visual",
                "description": "AI图像生成工具，创建高质量的艺术作品",
                "sort_order": 1,
            },
            {
                "name": "RoboNeo",
                "url": "https://www.roboneo.com/home",
                "category": "visual",
                "description": "AI视觉创作平台，提供先进的图像生成和编辑功能",
                "sort_order": 2,
            },
            {
                "name": "Suno",
                "url": "https://suno.com/",
                "category": "music",
                "description": "AI音乐创作平台，生成原创音乐",
                "sort_order": 3,
            },
            {
                "name": "Cursor",
                "url": "https://cursor.com/cn/agents",
                "category": "programming",
                "description": "AI编程助手，智能代码生成和编辑",
                "sort_order": 4,
            },
            {
                "name": "Pollo AI",
                "url": "https://pollo.ai/image-to-video",
                "category": "image",
                "description": "AI图片转视频工具，将静态图片转换为动态视频",
                "sort_order": 5,
            },
            {
                "name": "Viggle AI",
                "url": "https://viggle.ai/home",
                "category": "image",
                "description": "AI视频生成工具，创建动态视频内容",
                "sort_order": 6,
            },
            {
                "name": "MiniMax",
                "url": "https://www.minimaxi.com/",
                "category": "other",
                "description": "全栈自研的新一代AI模型矩阵，包含文本、视频、音频等多种AI能力",
                "sort_order": 7,
            },
        ]

        created_count = 0
        updated_count = 0

        for link_data in ai_links_data:
            # 检查是否已存在
            existing_link = AILink.objects.filter(url=link_data["url"]).first()

            if existing_link:
                # 更新现有链接
                for key, value in link_data.items():
                    setattr(existing_link, key, value)
                existing_link.save()
                updated_count += 1
                self.stdout.write(f"✅ 更新链接: {link_data['name']}")
            else:
                # 创建新链接
                link = AILink.objects.create(**link_data)

                # 尝试获取图标
                try:
                    domain = get_domain_from_url(link_data["url"])
                    favicon_url = extract_favicon_url(link_data["url"])

                    if favicon_url:
                        # 下载并保存图标
                        icon_path = download_and_save_icon(favicon_url, domain)
                        if icon_path:
                            link.icon = icon_path
                            link.save()
                            self.stdout.write(f"✅ 成功获取图标: {link_data['name']}")
                        else:
                            # 使用Google favicon服务作为备用
                            link.icon_url = get_default_icon_url(link_data["url"])
                            link.save()
                            self.stdout.write(f"⚠️ 使用备用图标: {link_data['name']}")
                    else:
                        # 使用Google favicon服务
                        link.icon_url = get_default_icon_url(link_data["url"])
                        link.save()
                        self.stdout.write(f"⚠️ 使用Google图标: {link_data['name']}")

                except Exception as e:
                    # 使用Google favicon服务作为最终备用
                    link.icon_url = get_default_icon_url(link_data["url"])
                    link.save()
                    self.stdout.write(f"❌ 图标获取失败，使用备用: {link_data['name']} - {str(e)}")

                created_count += 1
                self.stdout.write(f"✅ 创建链接: {link_data['name']}")

        self.stdout.write(
            self.style.SUCCESS(
                f"AI友情链接创建完成！\n"
                f"✅ 新创建: {created_count} 个\n"
                f"🔄 更新: {updated_count} 个\n"
                f"📊 总计: {AILink.objects.count()} 个链接"
            )
        )
