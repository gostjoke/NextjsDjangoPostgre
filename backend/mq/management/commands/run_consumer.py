"""
啟動 RabbitMQ consumer
用法: python manage.py run_consumer
      python manage.py run_consumer --queues send_email notification
"""
from django.core.management.base import BaseCommand
from mq.consumer import start_consuming
from mq.tasks import TASK_REGISTRY


class Command(BaseCommand):
    help = "Start RabbitMQ consumer"

    def add_arguments(self, parser):
        parser.add_argument(
            '--queues',
            nargs='+',
            default=None,
            help='指定要監聽的 queue (預設監聽所有註冊的 queue)',
        )

    def handle(self, *args, **options):
        # 沒指定就用全部註冊的 queue
        queues = options['queues'] or list(TASK_REGISTRY.keys())
        self.stdout.write(self.style.SUCCESS(f"Starting consumer for: {queues}"))
        start_consuming(queues)
