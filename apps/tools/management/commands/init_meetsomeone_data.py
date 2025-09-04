"""
初始化MeeSomeone数据的Django管理命令
"""

from django.core.management.base import BaseCommand

from apps.tools.models import RelationshipTag


class Command(BaseCommand):
    help = "初始化MeeSomeone人际档案系统的基础数据"

    def handle(self, *args, **options):
        """初始化预定义关系标签"""

        # 预定义标签数据
        predefined_tags = [
            # 家庭关系
            {"name": "家人", "color": "#e91e63"},
            {"name": "父母", "color": "#e91e63"},
            {"name": "兄弟姐妹", "color": "#e91e63"},
            {"name": "亲戚", "color": "#f06292"},
            # 朋友关系
            {"name": "挚友", "color": "#ff9800"},
            {"name": "好朋友", "color": "#ffb74d"},
            {"name": "普通朋友", "color": "#ffcc02"},
            {"name": "闺蜜/兄弟", "color": "#ff9800"},
            # 工作关系
            {"name": "同事", "color": "#2196f3"},
            {"name": "上司", "color": "#1976d2"},
            {"name": "下属", "color": "#42a5f5"},
            {"name": "合作伙伴", "color": "#03a9f4"},
            {"name": "客户", "color": "#00bcd4"},
            {"name": "供应商", "color": "#0097a7"},
            # 学习关系
            {"name": "同学", "color": "#4caf50"},
            {"name": "老师", "color": "#388e3c"},
            {"name": "学生", "color": "#66bb6a"},
            {"name": "导师", "color": "#2e7d32"},
            {"name": "校友", "color": "#81c784"},
            # 爱情关系
            {"name": "恋人", "color": "#9c27b0"},
            {"name": "前任", "color": "#7b1fa2"},
            {"name": "暗恋对象", "color": "#ba68c8"},
            {"name": "配偶", "color": "#8e24aa"},
            # 社交关系
            {"name": "邻居", "color": "#795548"},
            {"name": "网友", "color": "#607d8b"},
            {"name": "兴趣爱好", "color": "#ff5722"},
            {"name": "旅行结识", "color": "#ff7043"},
            {"name": "一面之缘", "color": "#9e9e9e"},
            # 专业关系
            {"name": "医生", "color": "#00c853"},
            {"name": "律师", "color": "#1976d2"},
            {"name": "顾问", "color": "#673ab7"},
            {"name": "服务人员", "color": "#795548"},
            # 重要程度
            {"name": "重要合作", "color": "#3f51b5"},
            {"name": "需要跟进", "color": "#ff5722"},
            {"name": "保持联系", "color": "#009688"},
            {"name": "定期问候", "color": "#4caf50"},
        ]

        created_count = 0
        updated_count = 0

        for tag_data in predefined_tags:
            tag, created = RelationshipTag.objects.get_or_create(
                name=tag_data["name"],
                defaults={
                    "tag_type": "predefined",
                    "color": tag_data["color"],
                    "is_global": True,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ 创建标签: {tag.name}"))
            else:
                # 更新颜色（如果需要）
                if tag.color != tag_data["color"]:
                    tag.color = tag_data["color"]
                    tag.save()
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f"⟳ 更新标签: {tag.name}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✨ MeeSomeone数据初始化完成！"
                f"\n📝 创建了 {created_count} 个新标签"
                f"\n🔄 更新了 {updated_count} 个标签"
                f"\n🏷️  总共有 {RelationshipTag.objects.count()} 个可用标签"
            )
        )
