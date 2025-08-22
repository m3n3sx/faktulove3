from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from faktury.views import pobierz_dane_z_gus


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')), # Dodaj URL-e django-allauth
    path('', include('faktury.urls')),  # Dołącz URL-e Twojej aplikacji
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/get-company-data/', pobierz_dane_z_gus, name='pobierz_dane_z_gus'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #do obslugi media files

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Also serve files from STATICFILES_DIRS in DEBUG mode
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()