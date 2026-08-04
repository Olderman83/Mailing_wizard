from django.db import models
from django.utils import timezone
from django.conf import settings
from apps.clients.models import Client
from apps.email_messages.models import Message


class Mailing(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]

    start_datetime = models.DateTimeField(verbose_name='Дата и время первой отправки')
    end_datetime = models.DateTimeField(verbose_name='Дата и время окончания отправки')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='created',
        verbose_name='Статус'
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name='Сообщение'
    )
    recipients = models.ManyToManyField(
        Client,
        related_name='mailings',
        verbose_name='Получатели'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name='Владелец',
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-created_at']

    def __str__(self):
        return f"Рассылка #{self.id} - {self.message.subject[:30]}"

    def is_active_mailing(self):
        """Проверяет, активна ли рассылка"""
        if not self.is_active:
            return False
        now = timezone.now()
        return self.status == 'started' and self.start_datetime <= now <= self.end_datetime

    def can_be_sent(self):
        """Можно ли отправить рассылку"""
        if not self.is_active:
            return False
        now = timezone.now()
        return self.status in ['created', 'started'] and self.start_datetime <= now <= self.end_datetime

    def get_status_display_custom(self):
        """Возвращает отображаемое имя статуса"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)


class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('failed', 'Не успешно'),
    ]

    attempt_datetime = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время попытки')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name='Статус'
    )
    server_response = models.TextField(blank=True, verbose_name='Ответ почтового сервера')
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Рассылка'
    )
    recipient_email = models.EmailField(verbose_name='Email получателя', blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mailing_attempts',
        verbose_name='Владелец',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылок'
        ordering = ['-attempt_datetime']

    def __str__(self):
        return f"Попытка #{self.id} - {self.get_status_display()}"
