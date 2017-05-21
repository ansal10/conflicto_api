import copy
from datetime import datetime

import facebook
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.views import APIView

from conflicto.api.v1.serializers.user_serializer import UserSerializer
from conflicto.models import UserProfile, FBProfile


class UserView(APIView):
    # {
    #     "firebase_id":"Mandatory",
    #     "fcm_token":"Optional",
    #     "fb_token":"Optional"
    # }
    @csrf_exempt
    def post(self, request):
        data = request.data
        firebase_id = data.get('firebase_id', None)
        user = User.objects.filter(userprofile__firebase_id=firebase_id).first()

        if firebase_id is None:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

        if user is None:
            user = self.create_user(data)
            new_user = True
        else:
            user = self.update_user(user, data)
            new_user = False

        if user:
            serializer = UserSerializer(user)
            res = serializer.data
            res['new_user'] = new_user
            return JsonResponse(res)
        else:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    def retrieve_fb_profile_data(self, fb_token):
        token = fb_token
        graph = facebook.GraphAPI(access_token=token)
        FB_PROFILE_FIELDS = 'id,name,email,gender,first_name,last_name,link,cover'
        d = graph.get_object('me', fields=FB_PROFILE_FIELDS)
        return d

    def create_user(self, data):
        if not data.get('fb_token', None):
            return None

        fb_data = self.retrieve_fb_profile_data(data['fb_token'])
        self.user = User.objects.create(email=fb_data['email'], username=fb_data['email'], is_active=True,
                                        first_name=fb_data['first_name'], last_name=fb_data['last_name'])

        self.user.userprofile = UserProfile.objects.create(fcm_token=data['fcm_token'], firebase_id=data['firebase_id'], user=self.user)
        dp_link = "https://graph.facebook.com/%s/picture?type=large"%(fb_data['id'])
        self.user.fbprofile = FBProfile.objects.create(token=data['fb_token'], first_name=fb_data['first_name'], last_name=fb_data['last_name'], name=fb_data['name'],
                                                       fb_link=fb_data['link'], dp_link=dp_link, gender=fb_data['gender'], cover_link=fb_data['cover']['source'], user=self.user)

        return self.user

    def update_user(self, user, data):
        if data.get('fcm_token',None):
            user.userprofile.fcm_token = data.get('fcm_token')
            user.userprofile.save()

        return user

