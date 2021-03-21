from django.urls import path
from . import views

urlpatterns = [
    path('couriers', views.CouriersView.as_view()),
    path('couriers/<int:id>', views.CourierView.as_view()),
    path('orders', views.OrdersView.as_view()),
    path('orders/assign', views.OrderAssignView.as_view()),
]
