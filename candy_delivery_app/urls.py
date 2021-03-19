from django.urls import path
from . import views

urlpatterns = [
    path('couriers', views.CouriersView.as_view()),
    path('couriers/<int:id>', views.CourierView.as_view()),
]
