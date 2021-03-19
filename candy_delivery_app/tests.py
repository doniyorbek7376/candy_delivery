from django.test import TestCase
from .models import Courier
from rest_framework.test import APIClient
import json

# Create your tests here.


class CouriersTest(TestCase):
    factory = None

    def setUp(self) -> None:
        self.client = APIClient()
        Courier.objects.update_or_create(courier_id=25, courier_type='foot', regions=[
            1, 2], working_hours=["09:00-18:00"])
        return super().setUp()

    def test_success_post_request(self):
        response = self.client.post('/couriers', data={
            'data': [
                {
                    'courier_id': 1,
                    'courier_type': 'foot',
                    'regions': [12, 14, 19],
                    'working_hours': ["09:00-18:00"],

                }
            ]
        }, format='json')

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content.decode())
        self.assertEqual(data['couriers'][0]['id'], 1)

    def test_error_post_request(self):
        response = self.client.post('/couriers', data={
            'data': [
                {
                    'courier_id': 1
                }
            ]
        }, format='json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode())
        self.assertEqual(data['validation_error']['couriers'][0]['id'], 1)

    def test_success_patch_request(self):
        response = self.client.patch('/couriers/25', {
            'regions': [1, 2, 3, 4]
        }, format='json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertEqual(data['regions'], [1, 2, 3, 4])

    def test_bad_patch_request(self):
        response = self.client.patch('/couriers/1', {
            'not_existing_field': 1
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_not_found_patch_request(self):
        response = self.client.patch('/couriers/1000', {
            'regions': [1, 2, 3]
        }, format='json')

        self.assertEqual(response.status_code, 404)
