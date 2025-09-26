from rest_framework import generics, permissions
from .models import Message
from .serializers import MessageSerializer
from orders.models import Order

class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        order_id = self.kwargs["order_id"]
        return Message.objects.filter(order_id=order_id)

class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order_id = self.kwargs["order_id"]
        order = Order.objects.get(id=order_id)
        serializer.save(sender=self.request.user, order=order)
