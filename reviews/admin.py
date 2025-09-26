from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "client", "medic", "rating", "is_complaint", "is_hidden", "created_at")
    list_filter = ("rating", "is_complaint", "is_hidden")
    search_fields = ("client__username", "medic__user__username", "order__id", "comment")
