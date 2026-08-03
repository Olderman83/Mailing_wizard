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

        # Отправка письма с подтверждением
        try:
            subject = 'Подтверждение регистрации'
            message = render_to_string('registration/activation_email.html', {
                'user': user,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
            messages.success(self.request, 'На ваш email отправлено письмо с подтверждением')
        except Exception as e:
            messages.warning(self.request, 'Не удалось отправить письмо подтверждения')

        return response


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
    if request.method == 'POST':
        user.is_blocked = not user.is_blocked
        user.save()
        status = 'заблокирован' if user.is_blocked else 'разблокирован'
        messages.success(request, f'Пользователь {user.email} {status}')
    return redirect('users:list')
