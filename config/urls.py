from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.main.urls')),
    path('clients/', include('apps.clients.urls')),
    path('messages/', include('apps.email_messages.urls', namespace='messages')),
    path('mailings/', include('apps.mailings.urls')),
    path('accounts/', include('apps.users.urls')),
]
