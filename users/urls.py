from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, VerifyView,
    UserListView, UserDetailView, ProfileView,
    MedicProfileView, MedicListAdminView, MedicDetailAdminView,
    PasswordResetRequestView, PasswordResetConfirmView
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify/", VerifyView.as_view(), name="verify"),   # ✅ yangi qo‘shiladi
    path("password-reset/request/", PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("medic/profile/", MedicProfileView.as_view(), name="medic_profile"),
    path("admin/medics/", MedicListAdminView.as_view(), name="admin_medic_list"),
    path("admin/medics/<int:pk>/", MedicDetailAdminView.as_view(), name="admin_medic_detail"),
]
