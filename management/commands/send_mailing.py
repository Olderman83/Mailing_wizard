from django.core.management.base import BaseCommand
from apps.mailings.services import send_mailing


class Command(BaseCommand):
    help = 'Отправляет рассылку по ID'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID рассылки для отправки')
        parser.add_argument(
            '--test',
            action='store_true',
            help='Тестовый режим (не отправляет реальные письма)',
        )

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']
        test_mode = options.get('test', False)

        self.stdout.write(f"Начинаем отправку рассылки #{mailing_id}...")

        success, failed = send_mailing(mailing_id, test_mode=test_mode)

        if success == 0 and failed == 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Рассылка #{mailing_id} не была отправлена. Проверьте статус и даты."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Рассылка #{mailing_id} завершена. "
                    f"Успешно: {success}, Ошибок: {failed}"
                )
            )
