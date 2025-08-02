from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.tools.services.social_media_crawler import run_crawler_task


class Command(BaseCommand):
    help = '运行社交媒体爬虫任务'

    def add_arguments(self, parser):
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='持续运行爬虫任务',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=300,
            help='检查间隔（秒），默认300秒',
        )

    def handle(self, *args, **options):
        continuous = options['continuous']
        interval = options['interval']
        
        self.stdout.write(
            self.style.SUCCESS(f'开始运行社交媒体爬虫任务...')
        )
        
        if continuous:
            self.stdout.write(
                self.style.WARNING(f'持续模式：每 {interval} 秒检查一次')
            )
            
            import time
            while True:
                try:
                    self.stdout.write(
                        f'[{timezone.now().strftime("%Y-%m-%d %H:%M:%S")}] 开始检查...'
                    )
                    run_crawler_task()
                    self.stdout.write(
                        self.style.SUCCESS(f'检查完成，等待 {interval} 秒...')
                    )
                    time.sleep(interval)
                except KeyboardInterrupt:
                    self.stdout.write(
                        self.style.WARNING('用户中断，停止爬虫任务')
                    )
                    break
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'爬虫任务出错: {str(e)}')
                    )
                    time.sleep(60)  # 出错后等待1分钟再重试
        else:
            # 单次运行
            run_crawler_task()
            self.stdout.write(
                self.style.SUCCESS('爬虫任务完成')
            ) 