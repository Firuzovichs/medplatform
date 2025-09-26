from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from utils.notifications import notify_medics_new_order

@receiver(post_save, sender=Order)
def order_created_notify(sender, instance, created, **kwargs):
    """
    Yangi buyurtma yaratilganda mediklarga push + SMS yuborish.
    """
    if created and instance.status == "new":
        # notify_medics_new_order() – utils.notifications.py dagi funksiya
        notify_medics_new_order(instance)
