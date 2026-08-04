from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.management import call_command
from django.core.cache import cache
from django.db.models import Q
from .models import Mailing, MailingAttempt
from .forms import MailingForm
from .services import send_mailing, update_mailing_status
import logging

logger = logging.getLogger(__name__)


@login_required
def mailing_list(request):
    if request.user.is_manager() or request.user.is_superuser:
        mailings = Mailing.objects.all()
    else:
        mailings = Mailing.objects.filter(user=request.user)

    mailings = mailings.prefetch_related('recipients', 'message')

    # Обновляем статусы перед отображением
    for mailing in mailings:
        update_mailing_status(mailing.id)

    return render(request, 'mailings/list.html', {'mailings': mailings})


@login_required
def mailing_create(request):
    if request.method == 'POST':
        form = MailingForm(request.POST)
        if form.is_valid():
            mailing = form.save(commit=False)
            mailing.user = request.user
            mailing.save()
            form.save_m2m()
            messages.success(request, 'Рассылка успешно создана')
            return redirect('mailings:list')
    else:
        form = MailingForm()
    return render(request, 'mailings/form.html', {'form': form, 'title': 'Создать рассылку'})


@login_required
def mailing_update(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    # Проверка прав
    if not (mailing.user == request.user or request.user.is_manager() or request.user.is_superuser):
        messages.error(request, 'У вас нет прав для редактирования этой рассылки')
        return redirect('mailings:list')

    if mailing.status == 'started':
        messages.warning(request, 'Нельзя редактировать активную рассылку')
        return redirect('mailings:list')

    if request.method == 'POST':
        form = MailingForm(request.POST, instance=mailing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Рассылка успешно обновлена')
            return redirect('mailings:list')
    else:
        form = MailingForm(instance=mailing)
    return render(request, 'mailings/form.html', {'form': form, 'title': 'Редактировать рассылку'})


@login_required
def mailing_delete(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    # Проверка прав
    if not (mailing.user == request.user or request.user.is_manager() or request.user.is_superuser):
        messages.error(request, 'У вас нет прав для удаления этой рассылки')
        return redirect('mailings:list')

    if mailing.status == 'started':
        messages.warning(request, 'Нельзя удалить активную рассылку')
        return redirect('mailings:list')

    if request.method == 'POST':
        mailing.delete()
        messages.success(request, 'Рассылка успешно удалена')
        return redirect('mailings:list')
    return render(request, 'mailings/delete.html', {'mailing': mailing})


@login_required
def mailing_send(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    # Проверка прав
    if not (mailing.user == request.user or request.user.is_manager() or request.user.is_superuser):
        messages.error(request, 'У вас нет прав для отправки этой рассылки')
        return redirect('mailings:detail', pk=pk)

    update_mailing_status(mailing.id)
    mailing.refresh_from_db()

    if not mailing.can_be_sent():
        messages.warning(
            request,
            f'Рассылка не может быть отправлена (статус: {mailing.get_status_display()})'
        )
        return redirect('mailings:detail', pk=pk)

    success, failed = send_mailing(mailing.id, request.user)

    if success > 0 or failed > 0:
        messages.success(
            request,
            f'Рассылка завершена. Успешно: {success}, Ошибок: {failed}'
        )
    else:
        messages.info(request, 'Рассылка не была отправлена')

    return redirect('mailings:detail', pk=pk)


@login_required
def mailing_detail(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    # Проверка прав
    if not (mailing.user == request.user or request.user.is_manager() or request.user.is_superuser):
        messages.error(request, 'У вас нет прав для просмотра этой рассылки')
        return redirect('mailings:list')

    update_mailing_status(mailing.id)
    mailing.refresh_from_db()

    attempts = mailing.attempts.all()[:50]

    stats = {
        'total': mailing.attempts.count(),
        'success': mailing.attempts.filter(status='success').count(),
        'failed': mailing.attempts.filter(status='failed').count(),
        'success_rate': 0,
    }

    if stats['total'] > 0:
        stats['success_rate'] = round((stats['success'] / stats['total']) * 100, 2)

    return render(request, 'mailings/detail.html', {
        'mailing': mailing,
        'attempts': attempts,
        'stats': stats,
    })


@login_required
def mailing_toggle_active(request, pk):
    """Вкл/Выкл рассылку (для менеджеров)"""
    if not (request.user.is_manager() or request.user.is_superuser):
        messages.error(request, 'У вас нет прав для выполнения этого действия')
        return redirect('mailings:list')

    mailing = get_object_or_404(Mailing, pk=pk)
    mailing.is_active = not mailing.is_active
    mailing.save()

    status = 'активирована' if mailing.is_active else 'деактивирована'
    messages.success(request, f'Рассылка #{pk} {status}')
    return redirect('mailings:detail', pk=pk)


@login_required
def mailing_send_command(request, pk):
    """Отправляет рассылку через management команду"""
    mailing = get_object_or_404(Mailing, pk=pk)

    # Проверка прав
    if not (mailing.user == request.user or request.user.is_manager() or request.user.is_superuser):
        messages.error(request, 'У вас нет прав для отправки этой рассылки')
        return redirect('mailings:detail', pk=pk)

    try:
        call_command('send_mailing', str(pk))
        messages.success(request, f'Рассылка #{pk} отправлена через командную строку')
    except Exception as e:
        messages.error(request, f'Ошибка отправки: {str(e)}')

    return redirect('mailings:detail', pk=pk)
