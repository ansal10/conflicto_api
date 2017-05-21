from rest_framework.serializers import ModelSerializer

from conflicto.api.v1.serializers.user_serializer import UserPostSerializer
from conflicto.models import Post


class PostSerializer(ModelSerializer):

    user = UserPostSerializer(required=False)
    class Meta:
        model = Post
        fields = ['id', 'title', 'description', 'category', 'shared_post', 'uuid', 'tags', 'likes', 'dislikes', 'endorse', 'supports', 'conflicts', 'reports', 'user']
        read_only_fields = ['id', 'uuid', 'tags', 'likes', 'dislikes', 'endorse', 'supports', 'conflicts', 'reports']


