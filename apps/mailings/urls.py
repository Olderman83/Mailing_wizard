from django.urls import path
from . import views

app_name = 'mailings'

urlpatterns = [
    path('', views.mailing_list, name='list'),
    path('create/', views.mailing_create, name='create'),
    path('<int:pk>/', views.mailing_detail, name='detail'),
    path('<int:pk>/update/', views.mailing_update, name='update'),
    path('<int:pk>/delete/', views.mailing_delete, name='delete'),
    path('<int:pk>/send/', views.mailing_send, name='send'),
    path('<int:pk>/send-command/', views.mailing_send_command, name='send_command'),
    path('<int:pk>/toggle-active/', views.mailing_toggle_active, name='toggle_active'),
]
