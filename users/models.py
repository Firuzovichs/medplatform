from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ("client", "Client"),
        ("medic", "Medic"),
        ("admin", "Admin"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="client")
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    push_token = models.CharField(max_length=255, null=True, blank=True)
    is_verified = models.BooleanField(default=False)



    def __str__(self):
        return f"{self.username} ({self.role})"

class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="codes")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.code}"
    
class MedicProfile(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE, related_name="medic_profile")
    specialty = models.CharField(max_length=100)
    experience = models.PositiveIntegerField(default=0)  # yillarda
    areas = models.TextField()  # qaysi hududlarda ishlaydi
    docs = models.FileField(upload_to="docs/", null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=(
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ),
        default="pending",
    )

    def __str__(self):
        return f"{self.user.username} - {self.specialty}"