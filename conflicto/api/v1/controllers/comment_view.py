import base64

from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.http import Http404
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from conflicto.api.v1.serializers.comment_serializer import CommentSerializer
from conflicto.models import Post, Comment, Actions, Reaction, Objects
ACTIONS = ['LIKE', 'DISLIKE', 'REPORT', 'ENDORSE']


class CommentView(APIView):
    def authenticate(self, request):
        auth_header = request.META['HTTP_AUTHORIZATION']
        encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
        username = decoded_credentials[0]
        password = decoded_credentials[1]

        self.user = User.objects.filter(userprofile__uuid=username, is_active=True).first()

        if self.user is None:
            raise Http404

    def user_and_post_authentication(self, request, post_uuid):
        self.authenticate(request)
        self.post = Post.objects.filter(uuid=post_uuid).first()
        if self.post is None:
            raise Http404

    def user_and_comment_authentication(self, request, comment_uuid):
        self.authenticate(request)
        self.comment = Comment.objects.filter(uuid=comment_uuid).first()
        if self.comment is None:
            raise Http404
    # {
    #     "comment": "comment1",
    #     "type": "SUPPORT",
    #     "post_uuid":"66876"
    # }
    @csrf_exempt
    def post(self, request):
        self.user_and_post_authentication(request, request.data.get('post_uuid', ''))
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

    def get(self, request, uuid):
        self.user_and_post_authentication(request, uuid)
        queryset = Comment.objects.filter(post_uuid=uuid).order_by('-id')
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

    def put(self, request, uuid):
        self.user_and_comment_authentication(request, uuid)
        data = request.data

        if data.get("action", None) and data.get('action').upper() in ACTIONS:
            self.update_action(data.get("action").upper(), uuid, self.user)
            return JsonResponse({"status": "ok"})
        elif data.get("comment", None):
            self.comment.comment = data.get("comment")
            self.comment.save()
            return JsonResponse({"status": "ok"})

        return JsonResponse({}, status=HTTP_400_BAD_REQUEST)

    def delete(self, request, uuid):
        self.user_and_comment_authentication(request, uuid)
        post = self.comment.post
        with transaction.atomic():
            if self.comment.type == Actions.CONFLICT:
                post.conflicts -= 1
            elif self.comment.type == Actions.SUPPORT:
                post.supports -=1
            post.save()
            self.comment.delete()

        return JsonResponse({"status": "ok"})

    def add_reactions(self, data):
        uuids = [x['uuid'] for x in data]
        reactions = Reaction.user_reactions(self.user.id, uuids, Objects.COMMENT)
        for d in data:
            d['reactions'] = reactions.get(d['uuid'], [])
        return data

    def update_action(self, action, comment_uuid, user):
        comment = Comment.objects.filter(uuid=comment_uuid).first()

        with transaction.atomic():
            reaction = Reaction.objects.filter(object_uuid=comment_uuid, object_type=Objects.COMMENT, user=user).first()
            if not reaction:
                Reaction.objects.create(object_uuid=comment_uuid, object_type=Objects.COMMENT, user=user, actions=[action])
                count = 1
            else:
                if action not in reaction.actions:  # Do Action
                    reaction.actions.append(action)
                    count = 1
                else:  # Undo Action
                    reaction.actions.remove(action)
                    count = -1
                reaction.save()

            if action == "LIKE":
                comment.likes = comment.likes + count
            elif action == "DISLIKE":
                comment.dislikes = comment.dislikes + count
            elif action == "REPORT":
                comment.reports = comment.reports + count
            elif action == "ENDORSE":
                comment.endorse = comment.endorse + count

            comment.save()


