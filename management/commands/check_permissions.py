from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Проверяет права доступа пользователей'

    def handle(self, *args, **options):
        self.stdout.write("=== Проверка прав доступа пользователей ===\n")

        users = User.objects.all()

        for user in users:
            self.stdout.write(f"Пользователь: {user.email}")
            self.stdout.write(f"  - Активен: {user.is_active}")
            self.stdout.write(f"  - Заблокирован: {user.is_blocked}")
            self.stdout.write(f"  - Суперпользователь: {user.is_superuser}")
            self.stdout.write(f"  - Менеджер: {user.is_manager()}")
            self.stdout.write(f"  - Количество сообщений: {user.messages.count()}")
            self.stdout.write(f"  - Количество клиентов: {user.clients.count()}")
            self.stdout.write(f"  - Количество рассылок: {user.mailings.count()}")
            self.stdout.write("")
            