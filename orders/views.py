from rest_framework import generics, permissions
from .models import Order
from .serializers import OrderSerializer
from users.permissions import IsClient, IsMedic
from rest_framework.response import Response
from rest_framework import status
from users.permissions import IsClient, IsMedic, IsAdmin
from utils.notifications import send_push_notification
from django.dispatch import receiver
from django.db.models.signals import post_save
from utils.notifications import notify_medics_new_order

# Client yangi buyurtma yaratishi
class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsClient]

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

@receiver(post_save, sender=Order)
def order_created_notify(sender, instance, created, **kwargs):
    if created and instance.status == "new":
        notify_medics_new_order(instance)


# Client o‘z buyurtmalari ro‘yxatini ko‘rishi
class ClientOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsClient]

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user)

# Medic uchun yangi buyurtmalar ro‘yxati (faqat o‘z hududi bo‘yicha keyin filterlash mumkin)
class MedicOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsMedic]

    def get_queryset(self):
        return Order.objects.filter(status="new")

class AcceptOrderView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsMedic]

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        if order.status != "new":
            return Response({"detail": "Order already taken"}, status=status.HTTP_400_BAD_REQUEST)
        order.status = "accepted"
        order.medic = request.user
        order.save()
        return Response(OrderSerializer(order).data)



class UpdateStatusView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsMedic]

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        allowed_transitions = {
            "accepted": "on_the_way",
            "on_the_way": "started",
            "started": "completed",
            "completed": "paid",
        }

        if order.status not in allowed_transitions:
            return Response({"detail": "This status cannot be updated further."}, status=400)

        old_status = order.status
        order.status = allowed_transitions[order.status]

        if order.status == "paid":
            order.payment_received = True

        order.save()

        # push notifications
        if order.client.push_token:
            send_push_notification(
                order.client.push_token,
                title=f"Order #{order.id} Status Update",
                body=f"Status changed from {old_status} to {order.status}"
            )

        if order.medic.push_token and order.medic != request.user:
            send_push_notification(
                order.medic.push_token,
                title=f"Order #{order.id} Status Update",
                body=f"Status changed from {old_status} to {order.status}"
            )

        return Response(OrderSerializer(order).data)

    

class AdminOrderListView(generics.ListAPIView):
    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [IsAdmin]