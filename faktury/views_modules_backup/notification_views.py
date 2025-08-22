"""
Notification and messaging views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.humanize.templatetags.humanize import naturaltime

from ..models import Wiadomosc, Partnerstwo
from ..notifications.models import Notification
from ..forms import SystemowaWiadomoscForm


@login_required
def notifications(request):
    """Get recent unread notifications for AJAX"""
    unread = Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).order_by('-timestamp')[:5]
    
    data = [{
        'id': n.id,
        'message': n.content,
        'title': n.title,
        'link': '#',  # Add proper link handling if needed
        'time': naturaltime(n.timestamp)
    } for n in unread]
    
    return JsonResponse(data, safe=False)


@login_required
def notifications_json(request):
    """Get notifications in JSON format for frontend"""
    notifications = Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).order_by('-timestamp')[:5]
    
    data = [{
        'id': n.id,
        'title': n.title,
        'content': n.content,
        'timestamp': n.timestamp.isoformat(),
        'type': n.type,
        'link': '#'  # Add proper link handling
    } for n in notifications]
    
    return JsonResponse(data, safe=False)


@login_required
def notifications_list(request):
    """List all notifications for user"""
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-timestamp')
    
    context = {
        'notifications': notifications
    }
    return render(request, 'faktury/notifications_list.html', context)


@login_required
def mark_notification_read(request, pk):
    """Mark single notification as read"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'ok'})


@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read for user"""
    Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).update(is_read=True)
    return JsonResponse({'status': 'ok'})


@login_required
def delete_notification(request, notification_id):
    """Delete notification"""
    if request.method == "POST":
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.delete()
        messages.success(request, 'Powiadomienie zostało usunięte.')
    return redirect(reverse("notifications_list"))


@login_required
def unread_notifications_count(request):
    """Get count of unread notifications"""
    count = Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).count()
    return JsonResponse({'count': count})


# Message Management Views

@login_required
def szczegoly_wiadomosci(request, pk):
    """Display message details"""
    wiadomosc = get_object_or_404(Wiadomosc, pk=pk)
    
    # Check permissions - user should be sender or receiver
    if (wiadomosc.autor != request.user and 
        wiadomosc.odbiorca_user != request.user):
        messages.error(request, "Nie masz dostępu do tej wiadomości.")
        return redirect('panel_uzytkownika')
    
    # Mark message as read if current user is the receiver
    if (wiadomosc.odbiorca_user == request.user and 
        not wiadomosc.przeczytana):
        wiadomosc.przeczytana = True
        wiadomosc.save()
    
    context = {'wiadomosc': wiadomosc}
    return render(request, 'faktury/szczegoly_wiadomosci.html', context)


@login_required
def odp_wiadomosc(request, pk):
    """Reply to a message"""
    oryginalna_wiadomosc = get_object_or_404(Wiadomosc, pk=pk)
    
    # Check permissions
    if (oryginalna_wiadomosc.autor != request.user and 
        oryginalna_wiadomosc.odbiorca_user != request.user):
        messages.error(request, "Nie masz dostępu do tej wiadomości.")
        return redirect('panel_uzytkownika')
    
    if request.method == 'POST':
        tresc = request.POST.get('tresc', '').strip()
        if tresc:
            # Determine receiver - if current user is sender, reply goes to original receiver
            if oryginalna_wiadomosc.autor == request.user:
                odbiorca = oryginalna_wiadomosc.odbiorca_user
            else:
                odbiorca = oryginalna_wiadomosc.autor
            
            # Create reply message
            odpowiedz = Wiadomosc.objects.create(
                autor=request.user,
                odbiorca_user=odbiorca,
                temat=f"Re: {oryginalna_wiadomosc.temat}",
                tresc=tresc,
                typ_wiadomosci=oryginalna_wiadomosc.typ_wiadomosci,
                wiadomosc_nadrzedna=oryginalna_wiadomosc
            )
            
            messages.success(request, 'Odpowiedź została wysłana.')
            return redirect('szczegoly_wiadomosci', pk=oryginalna_wiadomosc.pk)
        else:
            messages.error(request, 'Treść wiadomości nie może być pusta.')
    
    context = {
        'oryginalna_wiadomosc': oryginalna_wiadomosc,
    }
    return render(request, 'faktury/odp_wiadomosc.html', context)


@login_required
def lista_wiadomosci(request):
    """List messages for user"""
    # Messages from partners
    partner_wiadomosci = Wiadomosc.objects.filter(
        odbiorca_user=request.user, 
        typ_wiadomosci='partner'
    ).select_related('autor').order_by('-data_wyslania')
    
    # Team messages
    zespol_wiadomosci = Wiadomosc.objects.filter(
        odbiorca_user=request.user,
        typ_wiadomosci='zespol'
    ).select_related('autor', 'zespol').order_by('-data_wyslania')
    
    # System messages
    systemowe_wiadomosci = Wiadomosc.objects.filter(
        odbiorca_user=request.user,
        typ_wiadomosci='systemowa'
    ).select_related('autor').order_by('-data_wyslania')
    
    # Sent messages
    wyslane_wiadomosci = Wiadomosc.objects.filter(
        autor=request.user
    ).select_related('odbiorca_user').order_by('-data_wyslania')
    
    # Mark messages as read when viewing the list
    Wiadomosc.objects.filter(
        odbiorca_user=request.user,
        przeczytana=False
    ).update(przeczytana=True)
    
    context = {
        'partner_wiadomosci': partner_wiadomosci,
        'zespol_wiadomosci': zespol_wiadomosci,
        'systemowe_wiadomosci': systemowe_wiadomosci,
        'wyslane_wiadomosci': wyslane_wiadomosci,
    }
    
    return render(request, 'faktury/lista_wiadomosci.html', context)


@login_required
def wyslij_systemowa(request):
    """Send system message to all users (admin only)"""
    if not request.user.is_staff:
        messages.error(request, "Nie masz uprawnień do wysyłania wiadomości systemowych.")
        return redirect('panel_uzytkownika')
    
    if request.method == 'POST':
        form = SystemowaWiadomoscForm(request.POST)
        if form.is_valid():
            temat = form.cleaned_data['temat']
            tresc = form.cleaned_data['tresc']
            
            # Send to all active users
            users = User.objects.filter(is_active=True)
            created_count = 0
            
            for user in users:
                if user != request.user:  # Don't send to self
                    Wiadomosc.objects.create(
                        autor=request.user,
                        odbiorca_user=user,
                        temat=temat,
                        tresc=tresc,
                        typ_wiadomosci='systemowa'
                    )
                    created_count += 1
            
            messages.success(
                request, 
                f'Wiadomość systemowa została wysłana do {created_count} użytkowników.'
            )
            return redirect('panel_uzytkownika')
    else:
        form = SystemowaWiadomoscForm()
    
    return render(request, 'faktury/wyslij_systemowa.html', {'form': form})


@login_required
def wyslij_wiadomosc_partner(request):
    """Send message to business partner"""
    if request.method == 'POST':
        partner_id = request.POST.get('partner_id')
        temat = request.POST.get('temat', '').strip()
        tresc = request.POST.get('tresc', '').strip()
        
        if not all([partner_id, temat, tresc]):
            messages.error(request, 'Wszystkie pola są wymagane.')
            return redirect('lista_partnerstw')
        
        try:
            # Find partnership
            partnerstwo = Partnerstwo.objects.get(
                id=partner_id,
                aktywne=True
            )
            
            # Determine recipient
            if partnerstwo.firma1.user == request.user:
                odbiorca_user = partnerstwo.firma2.user
            elif partnerstwo.firma2.user == request.user:
                odbiorca_user = partnerstwo.firma1.user
            else:
                messages.error(request, "Nie masz dostępu do tego partnerstwa.")
                return redirect('lista_partnerstw')
            
            # Create message
            Wiadomosc.objects.create(
                autor=request.user,
                odbiorca_user=odbiorca_user,
                temat=temat,
                tresc=tresc,
                typ_wiadomosci='partner',
                partnerstwo=partnerstwo
            )
            
            messages.success(request, 'Wiadomość została wysłana do partnera biznesowego.')
            
        except Partnerstwo.DoesNotExist:
            messages.error(request, 'Nie znaleziono partnerstwa.')
    
    return redirect('lista_partnerstw')


def create_notification(user, title, content, notification_type='INFO'):
    """
    Helper function to create notifications
    """
    Notification.objects.create(
        user=user,
        title=title,
        content=content,
        type=notification_type,
        is_read=False
    )
