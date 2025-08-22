from django.db.models.signals import post_save
from django.dispatch import receiver
from faktury.faktury.models import Faktura
from .models import Notification

@receiver(post_save, sender=Faktura)
def create_invoice_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            title='Nowa faktura',
            content=f'Utworzono nową fakturę: {instance.numer}',
            type='INFO',
            user=instance.user,
            invoice=instance
        )

@receiver(post_save, sender=Faktura)
def create_invoice_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            title='Nowa faktura',
            content=f'Utworzono nową fakturę: {instance.numer}',
            type='INFO',
            user=instance.user,
            invoice=instance
        )