from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Order(models.Model):
    STATUS_CHOICES = (
        ("new", "New"),
        ("accepted", "Accepted"),
        ("on_the_way", "On the way"),
        ("started", "Started"),
        ("completed", "Completed"),
        ("paid", "Paid"),
    )

    client = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="orders")
    medic = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="taken_orders")
    service_type = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=255)
    time = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    payment_received = models.BooleanField(default=False)  # yangi qo‘shildi
    payment_status = models.BooleanField(default=False)  # False = not paid, True = paid
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.client} - {self.status}"

