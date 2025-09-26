from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from .models import MedicProfile
from .models import User, VerificationCode
import random

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    phone = serializers.CharField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "phone"]
        read_only_fields = ["id", "username"]  # username o‘zgarmasin
        
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.email = validated_data.get("email", instance.email)
        instance.phone = validated_data.get("phone", instance.phone)
        instance.save()
        return instance
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            phone=validated_data.get("phone"),
            address=validated_data.get("address"),
            role=validated_data.get("role", "client"),
            password=validated_data["password"],
        )
        return user


class MedicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicProfile
        fields = ["id", "specialty", "experience", "areas", "docs", "status"]
        read_only_fields = ["status"]  # status faqat admin tomonidan o‘zgartiriladi

    def update(self, instance, validated_data):
        instance.specialty = validated_data.get("specialty", instance.specialty)
        instance.experience = validated_data.get("experience", instance.experience)
        instance.areas = validated_data.get("areas", instance.areas)

        # Fayl kelgan bo‘lsa yangilash
        docs = validated_data.get("docs", None)
        if docs:
            instance.docs = docs

        instance.save()
        return instance
    
class MedicAdminSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = MedicProfile
        fields = ["id", "user", "specialty", "experience", "areas", "docs", "status"]



class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "phone", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            phone=validated_data.get("phone"),
            password=validated_data["password"],
        )
        # Tasdiqlash kodi yaratish
        code = str(random.randint(100000, 999999))
        VerificationCode.objects.create(user=user, code=code)
        # TODO: yuborish (email yoki SMS)
        print(f"Verification code for {user.username}: {code}")
        return user


class VerifySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        code = data["code"]
        try:
            verification = VerificationCode.objects.get(code=code, is_used=False)
        except VerificationCode.DoesNotExist:
            raise serializers.ValidationError("Invalid code")
        verification.is_used = True
        verification.save()
        user = verification.user
        user.is_verified = True
        user.save()
        return {"message": "Account verified successfully"}
    

class PasswordResetRequestSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def validate(self, data):
        phone = data.get("phone")
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError({"phone": "Bunday foydalanuvchi topilmadi."})

        # ✅ yangi tasdiqlash kodini yaratamiz
        VerificationCode.objects.create(phone=phone)
        return data


class PasswordResetConfirmSerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone = data.get("phone")
        code = data.get("code")
        new_password = data.get("new_password")

        try:
            verification = VerificationCode.objects.filter(phone=phone).latest("created_at")
        except VerificationCode.DoesNotExist:
            raise serializers.ValidationError({"phone": "Tasdiqlash kodi topilmadi."})

        if not verification.is_valid(code):
            raise serializers.ValidationError({"code": "Tasdiqlash kodi noto‘g‘ri yoki eskirgan."})

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError({"phone": "Foydalanuvchi topilmadi."})

        user.set_password(new_password)
        user.save()

        verification.delete()
        return {"message": "Parol muvaffaqiyatli yangilandi."}