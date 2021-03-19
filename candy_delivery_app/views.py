from rest_framework.views import APIView
from rest_framework.views import Response, Request
from .models import Courier
from .serializers import CourierSerializer


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
            return Response(serializer.data)
        except Exception as e:
            print(e)
            return Response(status=400)

    def _validate(self, data: dict):
        courier_type = data.get('courier_type', None)
        assert courier_type is None or courier_type in ['foot', 'bike', 'car']

        regions = data.get('regions', None)
        assert regions is None or type(regions) == list

        working_hours = data.get('working_hours', None)
        assert working_hours is None or type(working_hours) == list
