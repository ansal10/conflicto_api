import base64

from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from conflicto.api.v1.serializers.post_serializer import PostSerializer
from conflicto.models import Post, Reaction, Objects


class PostView(APIView):
    def authenticate(self, request):
        auth_header = request.META['HTTP_AUTHORIZATION']
        encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
        username = decoded_credentials[0]
        password = decoded_credentials[1]

        self.user = User.objects.filter(userprofile__uuid=username, is_active=True).first()
        if self.user is None:
            raise Http404
        return self.user

    def get(self, request):
        user = self.authenticate(request)
        queryset = Post.objects.all().order_by('id')
        paginator = Paginator(queryset, 2)
        page = request.GET.get('page')
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            queryset = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            queryset = paginator.page(paginator.num_pages)

        serializer = PostSerializer(queryset, many=True)
        data = self.add_reactions(serializer.data)
        return JsonResponse(data, safe=False)

    @csrf_exempt
    def post(self, request):
        user = self.authenticate(request)
        data = request.data
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            with transaction.atomic():
                data = serializer.validated_data
                data['user'] = user
                p = Post.objects.create(**data)
                return JsonResponse(PostSerializer(p).data)
        else:
            return JsonResponse(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def add_reactions(self, data):
        uuids = [x['uuid'] for x in data]
        reactions = Reaction.user_reactions(self.user.id, uuids, Objects.POST)
        for d in data:
            d['reaction'] = reactions.get(d['uuid'], [])
        return data
