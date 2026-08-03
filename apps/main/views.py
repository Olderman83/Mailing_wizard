from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.clients.models import Client
from apps.mailings.models import Mailing
from apps.mailings.services import update_mailing_status


@login_required
def index(request):
    # Обновляем статусы всех рассылок
    for mailing in Mailing.objects.filter(status__in=['created', 'started']):
        update_mailing_status(mailing.id)

    context = {
        'total_mailings': Mailing.objects.count(),
        'active_mailings': Mailing.objects.filter(status='started').count(),
        'total_clients': Client.objects.count(),
        'completed_mailings': Mailing.objects.filter(status='completed').count(),
        'created_mailings': Mailing.objects.filter(status='created').count(),
    }
    return render(request, 'main/index.html', context)
