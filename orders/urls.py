from django.urls import path
from .views import (
    OrderCreateView, ClientOrderListView, MedicOrderListView, 
    AcceptOrderView, UpdateStatusView, AdminOrderListView
)

urlpatterns = [
    path("create/", OrderCreateView.as_view(), name="order_create"),
    path("client/", ClientOrderListView.as_view(), name="client_orders"),
    path("medic/", MedicOrderListView.as_view(), name="medic_orders"),
    path("accept/<int:pk>/", AcceptOrderView.as_view(), name="accept_order"),
    path("status/<int:pk>/", UpdateStatusView.as_view(), name="update_status"),
    path("admin/list/", AdminOrderListView.as_view(), name="admin_orders"),
]
