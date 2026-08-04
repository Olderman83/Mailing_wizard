from django.core.management.base import BaseCommand
from apps.mailings.services import process_ready_mailings


class Command(BaseCommand):
    help = 'Обрабатывает все готовые к отправке рассылки'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Тестовый режим (не отправляет реальные письма)',
        )

    def handle(self, *args, **options):
        self.stdout.write("Начинаем обработку готовых рассылок...")

        results = process_ready_mailings()

        if results:
            self.stdout.write(self.style.SUCCESS("Обработка завершена:"))
            for mailing_id, stats in results.items():
                self.stdout.write(
                    f"  Рассылка #{mailing_id}: "
                    f"успешно {stats['success']}, "
                    f"ошибок {stats['failed']}"
                )
        else:
            self.stdout.write(self.style.WARNING("Нет рассылок для обработки"))
