from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.db import transaction
from .models import User
from .forms import CustomUserCreationForm, CustomAuthenticationForm


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True


class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance
        user.is_active = False  # Деактивируем до подтверждения
        user.save()

        # Отправка письма с подтверждением
        try:
            subject = 'Подтверждение регистрации'
            html_message = render_to_string('registration/activation_email.html', {
                'user': user,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                'protocol': 'https' if self.request.is_secure() else 'http',
                'domain': self.request.get_host(),
            })
            send_mail(
                subject,
                '',
                settings.EMAIL_HOST_USER,
                [user.email],
                html_message=html_message
            )
            messages.success(self.request, 'На ваш email отправлено письмо с подтверждением')
        except Exception as e:
            messages.warning(self.request, f'Не удалось отправить письмо подтверждения: {str(e)}')

        return response


def activate_account(request, uidb64, token):
    """Активация аккаунта по ссылке из письма"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Аккаунт успешно активирован!')
        return redirect('main:index')
    else:
        messages.error(request, 'Ссылка активации недействительна или устарела')
        return redirect('users:login')


@login_required
def profile_view(request):
    return render(request, 'registration/profile.html', {'user': request.user})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы')
    return redirect('main:index')


@login_required
@user_passes_test(lambda u: u.is_manager() or u.is_superuser)
def user_list_view(request):
    users = User.objects.all()
    return render(request, 'users/list.html', {'users': users})


@login_required
@user_passes_test(lambda u: u.is_manager() or u.is_superuser)
def user_toggle_block(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.user == user:
        messages.error(request, 'Нельзя заблокировать самого себя')
        return redirect('users:list')

    if request.method == 'POST':
        user.is_blocked = not user.is_blocked
        user.save()
        status = 'заблокирован' if user.is_blocked else 'разблокирован'
        messages.success(request, f'Пользователь {user.email} {status}')
    return redirect('users:list')
