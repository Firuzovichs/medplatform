from django.urls import path
from .views import MessageListView, MessageCreateView

urlpatterns = [
    path("<int:order_id>/", MessageListView.as_view(), name="chat_list"),
    path("<int:order_id>/send/", MessageCreateView.as_view(), name="chat_send"),
]
