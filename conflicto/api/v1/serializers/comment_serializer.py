from rest_framework.serializers import ModelSerializer

from conflicto.api.v1.serializers.user_serializer import UserPostSerializer
from conflicto.models import Comment


class CommentSerializer(ModelSerializer):

    user = UserPostSerializer(required=False)
    class Meta:
        model = Comment
        fields = ['uuid', 'post_uuid', 'comment', 'type', 'reports', 'likes', 'dislikes', 'endorse', 'user', 'id', 'created_on']
        read_only_fields = ['post_uuid', 'reports', 'likes', 'dislikes', 'endorse', 'user', 'id', 'created_on']
