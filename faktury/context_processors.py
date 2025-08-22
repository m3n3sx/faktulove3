def unread_wiadomosci_count(request):
    """
    Dodaje do kontekstu liczbę nieprzeczytanych wiadomości użytkownika.
    """
    if request.user.is_authenticated:
        unread = request.user.odebrane_wiadomosci.filter(przeczytana=False).count()
    else:
        unread = 0
    return {'unread_wiadomosci_count': unread}