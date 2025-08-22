def generuj_numer(user, typ_dokumentu):
    today = datetime.date.today()
    ostatnia_faktura = Faktura.objects.filter(
        user=user,
        data_wystawienia__year=today.year,
        typ_dokumentu=typ_dokumentu
    ).order_by('-numer').first()

    numer_kolejny = 1
    if ostatnia_faktura:
        try:
            numer_kolejny = int(ostatnia_faktura.numer.split('/')[1]) + 1
        except (IndexError, ValueError):
            numer_kolejny = Faktura.objects.filter(
                user=user,
                data_wystawienia__year=today.year,
                typ_dokumentu=typ_dokumentu
            ).count() + 1

    return f"{typ_dokumentu}/{numer_kolejny:04d}/{today.year}"
