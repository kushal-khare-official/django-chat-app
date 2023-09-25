from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chat_app_api.urls')),
    path('', include('chat_app.urls')),
]
