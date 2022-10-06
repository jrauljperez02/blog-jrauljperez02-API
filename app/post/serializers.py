"""
Serializers for post APIs
"""
from rest_framework import serializers
from core.models import Post, Author

class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for authors"""

    class Meta:
        model = Author
        fields = [
            'id', 
            'name', 
            'link', 
            'profile_picture', 
            'description'
            ]
        read_only_fields = ['id']

class PostSerializer(serializers.ModelSerializer):
    """Serializer for post"""

    authors = AuthorSerializer(many = True, required = False)

    class Meta:
        model = Post
        fields = ['id', 'title', 'description', 'img_description','slug', 'authors']
        read_only_fields = ['id']

    def _get_or_create_authors(self, authors, post):
        """Handle getting or creating authors as needed"""
        auth_user = self.context['request'].user
        for author in authors:
            author_obj, created = Author.objects.get_or_create(
                user = auth_user,
                **author
            )
            post.authors.add(author_obj)
    
    def create(self, validated_data):
        """Create a new post"""
        authors = validated_data.pop('authors',[])
        post = Post.objects.create(**validated_data)

        self._get_or_create_authors(authors, post)

        return post

    def update(self, instance, validated_data):
        """Update a post"""

        authors = validated_data.pop('authors',None)
        if authors is not None:
            instance.authors.clear()
            self._get_or_create_authors(authors, instance)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance