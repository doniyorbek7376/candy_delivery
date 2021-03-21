from django.db import models
from django.utils import timezone

# Create your models here.


class Courier(models.Model):
    courier_id = models.IntegerField(primary_key=True)
    courier_type = models.TextField(
        choices=[('foot', 'foot'), ('bike', 'bike'), ('car', 'car')])
    regions = models.JSONField()
    working_hours = models.JSONField()


class Order(models.Model):
    order_id = models.IntegerField(primary_key=True)
    weight = models.DecimalField(max_digits=4, decimal_places=2)
    region = models.IntegerField()
    delivery_hours = models.JSONField()


class OrderAssigned(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE)
    assigned_time = models.DateTimeField(auto_now_add=True)


class OrderCompleted(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True)
    complete_time = models.DateTimeField()
    time_taken = models.IntegerField(default=0)
