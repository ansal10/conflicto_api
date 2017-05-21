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
ACTIONS = ['LIKE', 'DISLIKE', 'REPORT', 'ENDORSE']

class PostView(APIView):
    def authenticate(self, request):
        auth_header = request.META['HTTP_AUTHORIZATION']
        encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
        username = decoded_credentials[0]

        self.user = User.objects.filter(userprofile__uuid=username, is_active=True).first()
        if self.user is None:
            raise Http404
        return self.user

    def get(self, request, post_uuid=None):
        user = self.authenticate(request)
        if post_uuid is None:  # list post
            queryset = Post.objects.all().order_by('id')
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

            serializer = PostSerializer(queryset, many=True)
            data = self.add_reactions(serializer.data)
            return JsonResponse({"results": data}, safe=False)
        else:
            post = Post.objects.get(uuid=post_uuid)


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


    def put(self, request, post_uuid):
        user = self.authenticate(request)
        data = request.data

        if data.get("action", None) and data.get('action').upper() in ACTIONS:
            self.update_action(data.get("action").upper(), post_uuid, user)
            return JsonResponse({"status": "ok"})
        return JsonResponse({}, status=HTTP_400_BAD_REQUEST)


    def update_action(self, action, post_uuid, user):
        post = Post.objects.filter(uuid=post_uuid).first()

        with transaction.atomic():
            reaction = Reaction.objects.filter(object_uuid=post_uuid, object_type=Objects.POST, user=user).first()
            if not reaction:
                Reaction.objects.create(object_uuid=post_uuid, object_type=Objects.POST, user=user, actions=[action])
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
                post.likes = post.likes + count
            elif action == "DISIKE":
                post.dislikes = post.dislikes + count
            elif action == "REPORT":
                post.reports = post.reports + count
            elif action == "ENDORSE":
                post.endorse = post.endorse + count

            post.save()


    def add_reactions(self, data):
        uuids = [x['uuid'] for x in data]
        reactions = Reaction.user_reactions(self.user.id, uuids, Objects.POST)
        for d in data:
            d['reactions'] = reactions.get(d['uuid'], [])
        return data

