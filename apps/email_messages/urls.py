from django.urls import path
from . import views

app_name = 'email_messages'

urlpatterns = [
    path('', views.message_list, name='list'),
    path('create/', views.message_create, name='create'),
    path('<int:pk>/update/', views.message_update, name='update'),
    path('<int:pk>/delete/', views.message_delete, name='delete'),
]
