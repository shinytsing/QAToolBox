from django.core.management.base import BaseCommand
from apps.tools.services.tarot_service import TarotService


class Command(BaseCommand):
    help = '初始化塔罗牌数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化塔罗牌数据...')
        
        try:
            tarot_service = TarotService()
            
            # 初始化塔罗牌
            self.stdout.write('正在创建塔罗牌...')
            tarot_service.initialize_tarot_deck()
            
            # 创建默认牌阵
            self.stdout.write('正在创建默认牌阵...')
            tarot_service.create_default_spreads()
            
            self.stdout.write(
                self.style.SUCCESS('塔罗牌数据初始化成功！')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'初始化失败: {str(e)}')
            ) 