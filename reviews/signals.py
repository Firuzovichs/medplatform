from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Review
from users.models import MedicProfile
from django.db import transaction
from django.db.models import Avg, Count

@receiver(post_save, sender=Review)
def update_medic_rating_on_save(sender, instance, created, **kwargs):
    medic = instance.medic
    # recompute avg and count
    agg = medic.reviews.aggregate(avg=Avg('rating'), cnt=Count('id'))
    medic.rating_avg = agg['avg'] or 0
    medic.reviews_count = agg['cnt'] or 0
    medic.save()

@receiver(post_delete, sender=Review)
def update_medic_rating_on_delete(sender, instance, **kwargs):
    medic = instance.medic
    agg = medic.reviews.aggregate(avg=Avg('rating'), cnt=Count('id'))
    medic.rating_avg = agg['avg'] or 0
    medic.reviews_count = agg['cnt'] or 0
    medic.save()
