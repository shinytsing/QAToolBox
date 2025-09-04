from django.core.management.base import BaseCommand
from apps.tools.models import FoodItem, FoodHistory, FoodRandomizationSession


class Command(BaseCommand):
    help = "清除现有食物数据并重建"

    def handle(self, *args, **options):
        self.stdout.write("🗑️ 开始清除现有食物数据...")

        # 清除相关数据
        FoodHistory.objects.all().delete()
        self.stdout.write("✅ 已清除食物历史记录")

        FoodRandomizationSession.objects.all().delete()
        self.stdout.write("✅ 已清除食物随机会话记录")

        FoodItem.objects.all().delete()
        self.stdout.write("✅ 已清除所有食物数据")

        self.stdout.write(self.style.SUCCESS("🎉 食物数据清除完成，可以开始重建新的食物库!"))
