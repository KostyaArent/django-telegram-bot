import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('tgadmin/', admin.site.urls),
    path('', include('tgbot.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'tgbot.views.error_404'
handler500 = 'tgbot.views.error_500'