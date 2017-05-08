import copy

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.views import APIView

from conflicto.api.v1.serializers.user_serializers import UserSerializer


class UserView(APIView):
    @csrf_exempt
    def post(self, request):
        data = request.data
        firebase_id = data.get('userprofile', {}).get('firebase_id', None)
        user = User.objects.filter(userprofile__firebase_id=firebase_id).first()

        if firebase_id is None:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

        if user is None:
            serializer = UserSerializer(data=data)
        else:
            serializer = UserSerializer(user, data=data)

        if serializer.is_valid():
            serializer.save()
            res = copy.deepcopy(serializer.data)
            res['new_user'] = False if user else True
            res.update(res.pop('userprofile'))
            return JsonResponse(res)
        else:
            return JsonResponse(serializer.errors)
