from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer,
    MedicProfileSerializer,
    MedicAdminSerializer,
    RegisterSerializer,
    VerifySerializer,PasswordResetRequestSerializer,PasswordResetConfirmSerializer
)
from .permissions import IsMedic
from .models import MedicProfile
from .permissions import IsAdmin

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer   # ✅ UserSerializer emas
    permission_classes = [permissions.AllowAny]


class VerifyView(generics.GenericAPIView):
    serializer_class = VerifySerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class MedicProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = MedicProfileSerializer
    permission_classes = [IsMedic]

    def get_object(self):
        # Agar mavjud bo‘lmasa, avtomatik yaratib qo‘yadi
        profile, created = MedicProfile.objects.get_or_create(user=self.request.user)
        return profile
    
class MedicListAdminView(generics.ListAPIView):
    queryset = MedicProfile.objects.all()
    serializer_class = MedicAdminSerializer
    permission_classes = [IsAdmin]


class MedicDetailAdminView(generics.RetrieveUpdateAPIView):
    queryset = MedicProfile.objects.all()
    serializer_class = MedicAdminSerializer
    permission_classes = [IsAdmin]

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "Tasdiqlash kodi yuborildi."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)