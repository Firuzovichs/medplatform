from rest_framework import serializers
from .models import Review
from users.serializers import UserSerializer
from orders.serializers import OrderSerializer

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id", "order", "rating", "comment",
            "is_complaint", "complaint_category", "complaint_description"
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        order = attrs.get("order")
        user = self.context['request'].user

        # Check order belongs to client and status completed
        if order.client != user:
            raise serializers.ValidationError("Siz ushbu buyurtma uchun sharh qoldira olmaysiz.")
        if order.status != "completed":
            raise serializers.ValidationError("Faqat 'completed' bo'lgan buyurtma uchun sharh qoldirish mumkin.")
        # Check one review per order
        if hasattr(order, 'review'):
            raise serializers.ValidationError("Ushbu buyurtma uchun sharh allaqachon mavjud.")
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        order = validated_data['order']
        # medic must be set on order
        medic_profile = order.medic.medic_profile if hasattr(order.medic, 'medic_profile') else None
        review = Review.objects.create(
            order=order,
            client=request.user,
            medic=medic_profile,
            rating=validated_data['rating'],
            comment=validated_data.get('comment', '')[:300],
            is_complaint=validated_data.get('is_complaint', False),
            complaint_category=validated_data.get('complaint_category', ''),
            complaint_description=validated_data.get('complaint_description', ''),
        )
        return review


class ReviewDetailSerializer(serializers.ModelSerializer):
    client = UserSerializer(read_only=True)
    # optionally include order minimal info
    order = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ["id", "client", "medic", "created_at", "rating"]
