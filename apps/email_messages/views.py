from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Message
from .forms import MessageForm

@login_required
def message_list(request):
    messages_list = Message.objects.all()
    return render(request, 'messages/list.html', {'messages': messages_list})

@login_required
def message_create(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Сообщение успешно создано')
            return redirect('email_messages:list')
    else:
        form = MessageForm()
    return render(request, 'messages/form.html', {'form': form, 'title': 'Создать сообщение'})

@login_required
def message_update(request, pk):
    message = get_object_or_404(Message, pk=pk)
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
    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Сообщение успешно удалено')
        return redirect('email_messages:list')
    return render(request, 'messages/delete.html', {'message': message})
