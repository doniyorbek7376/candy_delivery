from django.db import models

# Create your models here.


class Courier(models.Model):
    courier_id = models.IntegerField(primary_key=True)
    courier_type = models.TextField(choices=['foot', 'bike', 'car'])
    regions = models.JSONField()
    working_hours = models.JSONField()


class Order(models.Model):
    order_id = models.IntegerField(primary_key=True)
    weight = models.DecimalField()
    region = models.IntegerField()
    delivery_hours = models.JSONField()


class OrderAssigned(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE)
    assigned_time = models.DateTimeField()


class OrderCompleted(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True)
