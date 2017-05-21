import base64
import json

from django.contrib.auth.models import User
from django.test.testcases import TestCase

from conflicto.models import UserProfile, FBProfile, Post, Reaction, Objects, Actions, Comment


class TestCommentApis(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='123', is_active=True)
        self.userprofile = UserProfile.objects.create(firebase_id='12', fcm_token='121', user=self.user)
        self.fbprofile = FBProfile.objects.create(token='1111', user=self.user, name='Asd')
        self.post = Post.objects.create(title='Title', description='des', user=self.user)

        self.data1 = {
            "comment": "comment1",
            "type": Actions.SUPPORT,
            "post_uuid":self.post.uuid
        }
        self.data2 = {
            "comment": "comment2",
            "type": Actions.CONFLICT,
            "post_uuid": self.post.uuid
        }

    def tearDown(self):
        pass

    def auth_headers(self, username, password):
        credentials = base64.encodestring('%s:%s' % (username, password)).strip()
        auth_string = 'Basic %s' % credentials
        header = {'HTTP_AUTHORIZATION': auth_string}
        return header

    def post_api(self, data):
        res = self.client.post('/conflicto/comment', json.dumps(data), content_type="application/json",
                               **self.auth_headers(self.user.userprofile.uuid, 'YY'))
        return res.status_code, json.loads(res.content) if res.content else None

    def put_api(self, post_uuid, data):
        res = self.client.put('/conflicto/post/%s'% post_uuid, json.dumps(data), content_type="application/json",
                               **self.auth_headers(self.user.userprofile.uuid, 'YY'))
        return res.status_code, json.loads(res.content) if res.content else None

    def get_api(self, post_uuid):
        res = self.client.get('/conflicto/comment/%s'% post_uuid, **self.auth_headers(self.user.userprofile.uuid, 'YY'))
        return res.status_code, json.loads(res.content)['results'] if res.content else None


    def test_successfull_conflict_comment(self):
        status_code, data = self.post_api(self.data1)
        self.assertEqual(status_code, 200)
        self.assertIn('uuid', data)
        self.assertEqual(Comment.objects.all().count(), 1)
        self.assertEqual(Post.objects.get(uuid=self.post.uuid).supports, 1)


    def test_get_comments(self):
        self.post_api(self.data1)
        self.post_api(self.data2)

        status_code, data = self.get_api(self.post.uuid)
        self.assertEqual(status_code, 200)
        self.assertEqual(data.__len__(), 2)