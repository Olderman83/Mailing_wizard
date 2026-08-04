from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Кастомная модель пользователя"""
    email = models.EmailField(unique=True, verbose_name='Email')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_blocked = models.BooleanField(default=False, verbose_name='Заблокирован')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='Последняя активность')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def get_full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.email

    def is_manager(self):
        """Проверяет, является ли пользователь менеджером"""
        return self.groups.filter(name='Менеджеры').exists()

    def can_edit_mailing(self, mailing):
        """Проверяет, может ли пользователь редактировать рассылку"""
        if self.is_manager():
            return True
        return mailing.user == self

    def can_edit_client(self, client):
        """Проверяет, может ли пользователь редактировать клиента"""
        if self.is_manager():
            return True
        return client.user == self
