from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Message
from .forms import MessageForm
from django.core.cache import cache


@login_required
def message_list(request):
    if request.user.is_manager() or request.user.is_superuser:
        messages_list = Message.objects.all()
    else:
        messages_list = Message.objects.filter(user=request.user)

    return render(request, 'messages/list.html', {'messages': messages_list})


@login_required
def message_create(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.save()
            messages.success(request, 'Сообщение успешно создано')
            return redirect('email_messages:list')
    else:
        form = MessageForm()
    return render(request, 'messages/form.html', {'form': form, 'title': 'Создать сообщение'})


@login_required
def message_update(request, pk):
    message = get_object_or_404(Message, pk=pk)

    # Проверка прав
    if not (message.user == request.user or request.user.is_manager() or request.user.is_superuser):
        messages.error(request, 'У вас нет прав для редактирования этого сообщения')
        return redirect('email_messages:list')

    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            messages.success(request, 'Сообщение успешно обновлено')
            return redirect('email_messages:list')
    else:
        form = MessageForm(instance=message)
    return render(request, 'messages/form.html', {'form': form, 'title': 'Редактировать сообщение'})


@login_required
def message_delete(request, pk):
    message = get_object_or_404(Message, pk=pk)

    # Проверка прав
    if not (message.user == request.user or request.user.is_manager() or request.user.is_superuser):
        messages.error(request, 'У вас нет прав для удаления этого сообщения')
        return redirect('email_messages:list')

    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Сообщение успешно удалено')
        return redirect('email_messages:list')
    return render(request, 'messages/delete.html', {'message': message})
