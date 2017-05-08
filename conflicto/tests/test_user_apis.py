import json

from django.contrib.auth.models import User
from django.test.client import Client
from django.test.testcases import TestCase


class TestUserApis(TestCase):
    def setUp(self):
        self.client = Client()
        self.data1 = {
            "userprofile": {
                "fcm_token": "111",
                "firebase_id": "111"
            }
        }

        self.data2 = {
            "userprofile": {
                "fcm_token": "111",
            }
        }

    def tearDown(self):
        pass

    def call_api(self, data):
        res = self.client.post('/conflicto/user/authenticate', json.dumps(data), content_type="application/json")
        return res.status_code, json.loads(res.content) if res.content else None

    def test_user_creation(self):
        status_code, data = self.call_api(self.data1)
        self.assertEqual(status_code, 200)
        self.assertEqual(User.objects.filter(username='111').count(), 1)
        self.assertEqual(data['new_user'], True)

    def test_user_authentication(self):
        status_code, data = self.call_api(self.data1)
        status_code, data = self.call_api(self.data1)
        self.assertEqual(status_code, 200)
        self.assertEqual(User.objects.filter(username='111').count(), 1)
        self.assertEqual(data['new_user'], False)

    def test_user_authentication_without_firebaseid(self):
        status_code, data = self.call_api(self.data2)
        self.assertEqual(status_code, 401)
