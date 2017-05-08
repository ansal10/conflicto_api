from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

from conflicto.api.v1.controllers.post_view import PostView
from conflicto.models import Reaction


class ReactionView(APIView):
    @csrf_exempt
    def post(self, request):
        user = PostView().authenticate(request)
        data = request.data
        data['action'] = data['action'].upper()
        data['user'] = user
        if not Reaction.objects.filter(**data).exists():
            Reaction.objects.create(**data)
            return JsonResponse({"status": "created"})
        else:
            return JsonResponse({"status": "existed"})
