from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class UserActivityMiddleware:
    """Middleware для отслеживания активности пользователей"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            # Обновляем время последней активности
            User.objects.filter(pk=request.user.pk).update(
                last_activity=timezone.now()
            )

        return response
