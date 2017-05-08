from rest_framework.serializers import ModelSerializer
from conflicto.models import Comment


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ['uuid', 'post_uuid', 'comment', 'type', 'reports', 'likes', 'dislikes', 'endorse']
        read_only_fields = ['post_uuid', 'reports', 'likes', 'dislikes', 'endorse']
