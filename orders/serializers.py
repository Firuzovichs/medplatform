from rest_framework import serializers
from .models import Order
from users.serializers import UserSerializer

class OrderSerializer(serializers.ModelSerializer):
    client = UserSerializer(read_only=True)
    medic = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ["client", "medic", "created_at"]  # status faqat view orqali