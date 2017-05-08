import base64
import json

from django.contrib.auth.models import User
from django.test.testcases import TestCase

from conflicto.models import UserProfile, FBProfile, Post, Reaction


class TestPostApis(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='123', is_active=True)
        self.userprofile = UserProfile.objects.create(firebase_id='12', fcm_token='121', user=self.user)
        self.fbprofile = FBProfile.objects.create(token='1111', user=self.user)

        self.data1 = {
            "title": "My Title",
            "description": "Detailed Description"
        }

    def tearDown(self):
        pass

    def auth_headers(self, username, password):
        credentials = base64.encodestring('%s:%s' % (username, password)).strip()
        auth_string = 'Basic %s' % credentials
        header = {'HTTP_AUTHORIZATION': auth_string}
        return header

    def post_api(self, data):
        res = self.client.post('/conflicto/post', json.dumps(data), content_type="application/json",
                               **self.auth_headers(self.user.userprofile.uuid, 'YY'))
        return res.status_code, json.loads(res.content) if res.content else None

    def get_post(self):
        res = self.client.get('/conflicto/post', **self.auth_headers(self.user.userprofile.uuid, 'YY'))
        return res.status_code, json.loads(res.content) if res.content else None

    def test_successfull_post_submission(self):
        status_code, data = self.post_api(self.data1)
        self.assertEqual(status_code, 200)
        self.assertIn('uuid', data)
        self.assertEqual(Post.objects.all().count(), 1)

    def test_without_data_post_submission(self):
        status_code, data = self.post_api({})
        self.assertEqual(status_code, 400)
        self.assertEqual(Post.objects.all().count(), 0)

    def test_post_retrieval(self):
        for i in range(0, 10):
            self.post_api(self.data1)
        for p in Post.objects.all():
            Reaction.objects.create(user_id=self.user.id, object_uuid=p.uuid, object_type='POST', action='LIKE')
            Reaction.objects.create(user_id=self.user.id, object_uuid=p.uuid, object_type='POST', action='DISLIKE')
        status_code, data = self.get_post()
        self.assertEqual(status_code, 200)
        self.assertEqual(data.__len__(), 2)
        self.assertIn('reaction', data[0])
        self.assertEqual(data[0]['reaction'].__len__(), 2)
        self.assertEqual(data[1]['reaction'].__len__(), 2)
