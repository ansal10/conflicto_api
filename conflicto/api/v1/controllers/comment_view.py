import base64

from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from conflicto.api.v1.serializers.comment_serializer import CommentSerializer
from conflicto.models import Post, Comment, Actions, Reaction, Objects


class CommentView(APIView):
    def authenticate(self, request, post_uuid):
        auth_header = request.META['HTTP_AUTHORIZATION']
        encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
        username = decoded_credentials[0]
        password = decoded_credentials[1]

        self.user = User.objects.filter(userprofile__uuid=username, is_active=True).first()
        self.post = Post.objects.filter(uuid=post_uuid).first()
        if self.user is None or self.post is None:
            raise Http404

    # {
    #     "comment": "comment1",
    #     "type": "SUPPORT",
    #     "post_uuid":"66876"
    # }
    @csrf_exempt
    def post(self, request):
        self.authenticate(request, request.data.get('post_uuid', ''))
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            data['post_uuid'] = self.post.uuid
            data['post'] = self.post
            data['user'] = self.user
            comment = Comment.objects.create(**data)
            if comment.type == Actions.SUPPORT:
                self.post.supports += 1
            elif comment.type == Actions.CONFLICT:
                self.post.conflicts += 1
            self.post.save()
            return JsonResponse(CommentSerializer(comment).data)
        else:
            return JsonResponse(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def get(self, request, post_uuid):
        user = self.authenticate(request, post_uuid)
        queryset = Comment.objects.filter(post_uuid=post_uuid).order_by('id')
        paginator = Paginator(queryset, 25)
        page = request.GET.get('page')
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            queryset = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            queryset = paginator.page(paginator.num_pages)

        serializer = CommentSerializer(queryset, many=True)
        data = self.add_reactions(serializer.data)
        return JsonResponse({"results": data}, safe=False)

    def add_reactions(self, data):
        uuids = [x['uuid'] for x in data]
        reactions = Reaction.user_reactions(self.user.id, uuids, Objects.COMMENT)
        for d in data:
            d['reactions'] = reactions.get(d['uuid'], [])
        return data
