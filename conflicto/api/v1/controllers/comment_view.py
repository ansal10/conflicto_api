import base64

from django.contrib.auth.models import User
from django.http import Http404
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from conflicto.api.v1.serializers.comment_serializer import CommentSerializer
from conflicto.models import Post, Comment


class CommentView(APIView):
    def authenticate(self, request):
        auth_header = request.META['HTTP_AUTHORIZATION']
        encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
        username = decoded_credentials[0]
        password = decoded_credentials[1]

        self.user = User.objects.filter(userprofile__uuid=username, is_active=True).first()
        self.post = Post.objects.filter(uuid=request.data.get('post_uuid', '')).first()
        if self.user is None or self.post is None:
            raise Http404

    @csrf_exempt
    def post(self, request):
        self.authenticate(request)
        serializer = CommentSerializer(request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            data['post_uuid'] = self.post.uuid
            data['post'] = self.post
            data['user'] = self.user
            comment = Comment.objects.create(**data)
            return JsonResponse(CommentSerializer(comment).data)
        else:
            return JsonResponse(serializer.errors, status=HTTP_400_BAD_REQUEST)

