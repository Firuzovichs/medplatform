from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Review(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='review')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    medic = models.ForeignKey('users.MedicProfile', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()  # 1-5
    comment = models.CharField(max_length=300, blank=True)
    is_complaint = models.BooleanField(default=False)
    complaint_category = models.CharField(max_length=200, blank=True)
    complaint_description = models.TextField(blank=True)
    is_hidden = models.BooleanField(default=False)  # admin can hide text but not rating
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['medic', 'rating']),
            models.Index(fields=['created_at']),
        ]

    def can_edit(self):
        """Return True if within 24h from created_at"""
        if not self.created_at:
            return False
        return timezone.now() <= (self.created_at + timezone.timedelta(hours=24))

    def __str__(self):
        return f"Review #{self.id} - {self.rating} - {self.medic}"
