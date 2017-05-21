import json

import mock as mock
from django.contrib.auth.models import User
from django.test.client import Client
from django.test.testcases import TestCase



def mocked_retrieve_fb_profile_data(token):
    return {
        'id':'123',
        'name':'abc',
        'email':'aa@xyz.com',
        'gender':'male',
        'first_name':'a',
        'last_name':'l',
        'link':'link1',
        'cover':{
            'source':'cover1'
        }
    }

class TestUserApis(TestCase):
    def setUp(self):
        self.client = Client()
        self.data1 = {
            "fcm_token": "111",
            "firebase_id": "111",
            "fb_token":"!212"
        }

        self.data2 = {
            "fcm_token": "111",
        }

    def tearDown(self):
        pass

    def call_api(self, data):
        res = self.client.post('/conflicto/user/authenticate', json.dumps(data), content_type="application/json")
        return res.status_code, json.loads(res.content) if res.content else None

    @mock.patch('conflicto.api.v1.controllers.user_view.UserView.retrieve_fb_profile_data', side_effect=mocked_retrieve_fb_profile_data)
    def test_user_creation(self, m1):
        status_code, data = self.call_api(self.data1)
        self.assertEqual(status_code, 200)
        self.assertEqual(User.objects.filter(username='aa@xyz.com').count(), 1)
        self.assertEqual(data['new_user'], True)

    @mock.patch('conflicto.api.v1.controllers.user_view.UserView.retrieve_fb_profile_data', side_effect=mocked_retrieve_fb_profile_data)
    def test_user_authentication(self, m1):
        status_code, data = self.call_api(self.data1)
        status_code, data = self.call_api(self.data1)
        self.assertEqual(status_code, 200)
        self.assertEqual(User.objects.filter(username='aa@xyz.com').count(), 1)
        self.assertEqual(data['new_user'], False)

    def test_user_authentication_without_firebaseid(self):
        status_code, data = self.call_api(self.data2)
        self.assertEqual(status_code, 401)
