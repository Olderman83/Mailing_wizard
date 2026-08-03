from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache
from .models import Client
from .forms import ClientForm
from apps.users.models import User


@login_required
def client_list(request):
    if request.user.is_manager() or request.user.is_superuser:
        clients = Client.objects.all()
    else:
        clients = Client.objects.filter(user=request.user)

    # Кеширование списка клиентов на 5 минут
    cache_key = f'client_list_{request.user.id}'
    clients = cache.get(cache_key)
    if not clients:
        clients = Client.objects.filter(user=request.user) if not request.user.is_manager() else Client.objects.all()
        cache.set(cache_key, clients, 300)

    return render(request, 'clients/list.html', {'clients': clients})


@login_required
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.user = request.user
            client.save()
            # Очищаем кеш
            cache.delete(f'client_list_{request.user.id}')
            messages.success(request, 'Получатель успешно добавлен')
            return redirect('clients:list')
    else:
        form = ClientForm()
    return render(request, 'clients/form.html', {'form': form, 'title': 'Добавить получателя'})


@login_required
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)

    # Проверка прав доступа
    if not request.user.can_edit_client(client):
        messages.error(request, 'У вас нет прав для редактирования этого получателя')
        return redirect('clients:list')

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            cache.delete(f'client_list_{request.user.id}')
            messages.success(request, 'Получатель успешно обновлен')
            return redirect('clients:list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/form.html', {'form': form, 'title': 'Редактировать получателя'})


@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)

    if not request.user.can_edit_client(client):
        messages.error(request, 'У вас нет прав для удаления этого получателя')
        return redirect('clients:list')

    if request.method == 'POST':
        client.delete()
        cache.delete(f'client_list_{request.user.id}')
        messages.success(request, 'Получатель успешно удален')
        return redirect('clients:list')
    return render(request, 'clients/delete.html', {'client': client})
