from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from faktury.views import pobierz_dane_z_gus
from faktury.services.navigation_manager import MissingPageHandler


urlpatterns = [
    path('admin/', admin.site.urls),
    path('superadmin/', include('faktury.urls_superadmin')),  # Super Admin Panel - MUST be before empty path
    path('accounts/', include('allauth.urls')), # Dodaj URL-e django-allauth
    path('i18n/', include('django.conf.urls.i18n')),
    path('api/get-company-data/', pobierz_dane_z_gus, name='pobierz_dane_z_gus'),
    path('api/', include('faktury.api.urls')),  # API endpoints with documentation
    path('', include('faktury.urls')),  # Dołącz URL-e Twojej aplikacji - MUST be last
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #do obslugi media files

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = MissingPageHandler.create_404_fallback