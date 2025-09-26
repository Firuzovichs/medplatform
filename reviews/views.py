from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Review
from .serializers import ReviewCreateSerializer, ReviewDetailSerializer
from users.permissions import IsClient, IsAdmin

class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsClient]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx.update({"request": self.request})
        return ctx

class ReviewDetailView(generics.RetrieveAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewDetailSerializer
    permission_classes = [permissions.IsAuthenticated]  # medic/client/admin can view; admin can edit/hide via admin endpoints

class ReviewUpdateView(generics.UpdateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        # only client who created can edit and only within 24h
        if request.user != review.client:
            return Response({"detail": "Siz faqat o'zingizning sharhingizni tahrirlashingiz mumkin."}, status=403)
        if not review.can_edit():
            return Response({"detail": "Sharhni faqat 24 soat ichida tahrirlash mumkin."}, status=400)

        # allow edit of comment and is_complaint fields only (not rating change)
        data = request.data.copy()
        allowed = {}
        if "comment" in data:
            allowed["comment"] = data["comment"][:300]
            review.comment = allowed["comment"]
        if "is_complaint" in data:
            review.is_complaint = data.get("is_complaint", review.is_complaint)
            review.complaint_category = data.get("complaint_category", review.complaint_category)
            review.complaint_description = data.get("complaint_description", review.complaint_description)
        review.edited_at = timezone.now()
        review.save()
        serializer = self.get_serializer(review)
        return Response(serializer.data)


# Admin: list reviews, filter by low rating or complaints, hide text
class AdminReviewListView(generics.ListAPIView):
    queryset = Review.objects.all().order_by("-created_at")
    serializer_class = ReviewDetailSerializer
    permission_classes = [IsAdmin]
    # Filtering can be added via DjangoFilterBackend in settings

class AdminHideReviewView(generics.UpdateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewDetailSerializer
    permission_classes = [IsAdmin]

    def patch(self, request, *args, **kwargs):
        review = self.get_object()
        review.is_hidden = request.data.get("is_hidden", True)
        review.save()
        return Response(self.get_serializer(review).data)
