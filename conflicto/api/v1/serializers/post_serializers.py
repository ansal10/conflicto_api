from rest_framework.serializers import ModelSerializer, ListSerializer

from conflicto.models import Post


class PostSerializer(ModelSerializer):

    class Meta:
        model = Post
        fields = ['id', 'title', 'description', 'category', 'shared_post', 'uuid', 'tags', 'likes', 'dislikes', 'endorse', 'supports', 'conflicts', 'reports']
        read_only_fields = ['id', 'uuid', 'tags', 'likes', 'dislikes', 'endorse', 'supports', 'conflicts', 'reports']


