def unread_wiadomosci_count(request):
    """
    Dodaje do kontekstu liczbę nieprzeczytanych wiadomości użytkownika.
    """
    if request.user.is_authenticated:
        unread = request.user.odebrane_wiadomosci.filter(przeczytana=False).count()
    else:
        unread = 0
    return {'unread_wiadomosci_count': unread}


def navigation_context(request):
    """
    Dodaje informacje o nawigacji do kontekstu wszystkich szablonów
    """
    context = {}
    
    if request.user.is_authenticated:
        try:
            from .services.navigation_manager import NavigationManager
            nav_manager = NavigationManager()
            context.update({
                'navigation_status': nav_manager.get_navigation_status(),
                'breadcrumbs': nav_manager.create_breadcrumbs(request.path),
            })
        except Exception:
            # Fallback if navigation manager fails
            context.update({
                'navigation_status': {'status': 'unknown'},
                'breadcrumbs': [],
            })
    
    return context


def global_context(request):
    """
    Dodaje globalne zmienne kontekstowe dostępne we wszystkich szablonach
    """
    from django.conf import settings
    
    context = {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'FaktuLove'),
        'DEBUG': settings.DEBUG,
    }
    
    # Dodaj informacje o firmie użytkownika jeśli jest zalogowany
    if request.user.is_authenticated:
        try:
            from .models import Firma
            firma = Firma.objects.get(user=request.user)
            context['firma'] = firma
        except Firma.DoesNotExist:
            context['firma'] = None
    
    return context