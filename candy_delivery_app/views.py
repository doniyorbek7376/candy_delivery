from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.views import Response, Request
from .models import Courier, Order, OrderAssigned, OrderCompleted
from .serializers import CourierSerializer
import datetime
from django.utils import timezone


def _check_interval(delivery, working_hours):
    start_delivery, end_delivery = delivery.split('-')
    start_delivery = datetime.time(
        *[int(i) for i in start_delivery.split(":")])
    end_delivery = datetime.time(*[int(i)
                                 for i in end_delivery.split(":")])
    for working in working_hours:
        start_work, end_work = working.split("-")
        start_work = datetime.time(*[int(i)
                                   for i in start_work.split(":")])
        end_work = datetime.time(*[int(i) for i in end_work.split(":")])
        if start_delivery < end_work and start_work < end_delivery:
            return True
    return False


class CouriersView(APIView):

    def post(self, request, format=None):
        resp = {'couriers': []}
        error_ids = []
        for i in request.data['data']:
            self._validate(i, error_ids)
            resp['couriers'].append({'id': i['courier_id']})
        if error_ids:
            resp = {
                'validation_error': {
                    'couriers': error_ids
                }
            }
            return Response(resp, status=400)

        for i in request.data['data']:
            Courier.objects.create(**i)
        return Response(resp, status=201)

    def _validate(self, data, errors):
        try:
            assert data['courier_type'] in ['foot', 'bike', 'car']
            assert type(data['regions']) == list
            assert type(data['working_hours']) == list
            assert len(data.keys()) == 4
        except:
            errors.append({'id': data['courier_id']})


class CourierView(APIView):
    def patch(self, request, id, format=None):
        try:
            self._validate(request.data)
            Courier.objects.filter(courier_id=id).update(**request.data)
            courier = Courier.objects.get(courier_id=id)
            serializer = CourierSerializer(courier)
            for assigned_order in OrderAssigned.objects.filter(courier=courier):
                assigned_order: OrderAssigned
                if all([not _check_interval(interval, courier.working_hours) for interval in assigned_order.order.delivery_hours]):
                    assigned_order.delete()

            return Response(serializer.data)
        except ObjectDoesNotExist as e:
            # print(e)
            return Response(status=404)
        except FieldDoesNotExist as e:
            # print(e)
            return Response(status=400)

    def _validate(self, data: dict):
        courier_type = data.get('courier_type', None)
        assert courier_type is None or courier_type in ['foot', 'bike', 'car']

        regions = data.get('regions', None)
        assert regions is None or type(regions) == list

        working_hours = data.get('working_hours', None)
        assert working_hours is None or type(working_hours) == list


class OrdersView(APIView):

    def post(self, request, format=None):
        resp = {'orders': []}
        errors = []
        for i in request.data['data']:
            self._validate(i, errors)
            resp['orders'].append({'id': i['order_id']})
        if errors:
            resp = {
                'validation_error': {
                    'orders': errors
                }
            }
            return Response(resp, status=400)
        for i in request.data['data']:
            Order.objects.create(**i)
        return Response(resp, status=201)

    def _validate(self, data: dict, errors: list):
        try:
            assert type(data['order_id']) == int
            assert 0.01 <= data['weight'] <= 50
            assert data['region'] > 0
            assert type(data['delivery_hours']) == list
            assert len(data.items()) == 4

        except:
            errors.append({'id': data['order_id']})


class OrderAssignView(APIView):
    def post(self, request, format=None):
        try:
            courier = Courier.objects.get(
                courier_id=request.data['courier_id'])
            courier: Courier
            weight = {'foot': 10, 'bike': 15, 'car': 50}[courier.courier_type]
            assigned_to_others = [
                assigned.order.order_id for assigned in OrderAssigned.objects.exclude(courier=courier)]
            all_orders = Order.objects.filter(weight__lte=weight).filter(
                region__in=courier.regions).exclude(order_id__in=assigned_to_others)
            orders = []
            assigned_time = None
            for order in all_orders:
                if any([_check_interval(interval, courier.working_hours) for interval in order.delivery_hours]):
                    orders.append(order)
                    assigned, _ = OrderAssigned.objects.get_or_create(order=order, courier=courier, defaults={
                        'order': order,
                        'courier': courier,
                        'assigned_time': timezone.now()
                    })
                    if assigned_time:
                        assigned_time = max(
                            [assigned_time, assigned.assigned_time]
                        )
                    else:
                        assigned_time = assigned.assigned_time
            resp = {
                'orders': [{'id': order.order_id} for order in orders],
                'assign_time': assigned_time
            }
            return Response(resp, status=200)
        except Exception as e:
            return Response(status=400)


class OrderCompleteView(APIView):
    def post(self, request, format=None):
        try:
            courier = Courier.objects.get(
                courier_id=request.data['courier_id'])
            order = Order.objects.get(order_id=request.data['order_id'])
            order_assigned = OrderAssigned.objects.get(
                order=order, courier=courier)
            OrderCompleted.objects.create(**request.data)
            order_assigned: OrderAssigned
            order_assigned.delete()
            return Response({
                'order_id': request.data['order_id']
            }, status=200)
        except:
            return Response(status=400)
