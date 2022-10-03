"""
Serializers for post APIs
"""
from rest_framework import serializers
from core.models import Post

class PostSerializer(serializers.ModelSerializer):
    """Serializer for post"""

    class Meta:
        model = Post
        fields = ['id', 'title', 'description', 'img_description','slug']
        read_only_fields = ['id']
    