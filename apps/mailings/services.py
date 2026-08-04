from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from .models import Mailing, MailingAttempt
import logging

logger = logging.getLogger(__name__)


def send_mailing(mailing_id, test_mode=False):
    """
    Отправляет рассылку по указанному ID

    Args:
        mailing_id: ID рассылки
        test_mode: Если True, не отправляет реальные письма, только логирует

    Returns:
        tuple: (success_count, failed_count)
    """
    try:
        mailing = Mailing.objects.get(id=mailing_id)
    except Mailing.DoesNotExist:
        logger.error(f"Рассылка #{mailing_id} не найдена")
        return 0, 0

    # Проверяем, можно ли отправить
    if not mailing.can_be_sent():
        status_display = mailing.get_status_display()
        logger.info(f"Рассылка #{mailing_id} не может быть отправлена (статус: {status_display})")
        return 0, 0

    # Получаем получателей
    recipients = mailing.recipients.all()

    if not recipients.exists():
        logger.warning(f"Рассылка #{mailing_id} не имеет получателей")
        return 0, 0

    success_count = 0
    failed_count = 0

    # Отправляем письма каждому получателю
    for recipient in recipients:
        try:
            if test_mode:
                # В тестовом режиме только логируем
                logger.info(f"[TEST] Письмо для {recipient.email}: {mailing.message.subject}")
                server_response = "Тестовый режим - письмо не отправлено"
                status = 'success'
            else:
                # Реальная отправка
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                server_response = "Письмо успешно отправлено"
                status = 'success'

            # Создаем запись об успешной попытке
            with transaction.atomic():
                MailingAttempt.objects.create(
                    status=status,
                    server_response=server_response,
                    mailing=mailing,
                    recipient_email=recipient.email
                )
            success_count += 1

        except Exception as e:
            error_msg = str(e)[:500]  # Ограничиваем длину
            # Создаем запись о неуспешной попытке
            with transaction.atomic():
                MailingAttempt.objects.create(
                    status='failed',
                    server_response=error_msg,
                    mailing=mailing,
                    recipient_email=recipient.email
                )
            failed_count += 1
            logger.error(f"Ошибка отправки письма {recipient.email}: {error_msg}")

    # Обновляем статус рассылки
    update_mailing_status(mailing_id)

    logger.info(f"Рассылка #{mailing_id} завершена. Успешно: {success_count}, Ошибок: {failed_count}")
    return success_count, failed_count


def update_mailing_status(mailing_id):
    """
    Обновляет статус рассылки в зависимости от времени
    """
    try:
        mailing = Mailing.objects.get(id=mailing_id)
    except Mailing.DoesNotExist:
        return

    now = timezone.now()

    # Если время окончания прошло, завершаем
    if mailing.end_datetime <= now and mailing.status != 'completed':
        mailing.status = 'completed'
        mailing.save(update_fields=['status'])
        logger.info(f"Рассылка #{mailing_id} автоматически завершена")

    # Если время начала прошло и статус created, запускаем
    elif mailing.start_datetime <= now and mailing.status == 'created':
        mailing.status = 'started'
        mailing.save(update_fields=['status'])
        logger.info(f"Рассылка #{mailing_id} автоматически запущена")


def process_ready_mailings():
    """
    Обрабатывает все рассылки, готовые к отправке
    """
    now = timezone.now()

    # Находим рассылки, которые должны быть отправлены
    mailings = Mailing.objects.filter(
        status__in=['created', 'started'],
        start_datetime__lte=now,
        end_datetime__gte=now
    )

    results = {}
    for mailing in mailings:
        success, failed = send_mailing(mailing.id)
        results[mailing.id] = {'success': success, 'failed': failed}

    return results
