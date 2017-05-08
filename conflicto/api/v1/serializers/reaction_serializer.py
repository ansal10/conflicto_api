from rest_framework.serializers import ModelSerializer

from conflicto.models import Reaction


class ReactionSerializer(ModelSerializer):
    class Meta:
        model = Reaction
        fields = ['object_uuid', 'object_type', 'user_id', 'action']