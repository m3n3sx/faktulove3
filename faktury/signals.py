from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Faktura
from .fakture_ksiegowosc import auto_ksieguj_fakture_service

@receiver(post_save, sender=Faktura)
def auto_ksieguj_fakture(sender, instance, created, **kwargs):
    if created: # Uruchom tylko przy tworzeniu faktury
        auto_ksieguj_fakture_service(instance)
