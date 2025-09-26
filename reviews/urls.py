from django.urls import path
from .views import (
    ReviewCreateView, ReviewDetailView, ReviewUpdateView,
    AdminReviewListView, AdminHideReviewView
)

urlpatterns = [
    path("create/", ReviewCreateView.as_view(), name="review_create"),
    path("<int:pk>/", ReviewDetailView.as_view(), name="review_detail"),
    path("<int:pk>/edit/", ReviewUpdateView.as_view(), name="review_update"),
    # Admin
    path("admin/list/", AdminReviewListView.as_view(), name="admin_review_list"),
    path("admin/<int:pk>/hide/", AdminHideReviewView.as_view(), name="admin_review_hide"),
]
