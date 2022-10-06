"""
Views for post APIs
"""
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Post, Author
from post import serializers

class PostViewSet(viewsets.ModelViewSet):
    """View for manage post APIs."""
    serializer_class = serializers.PostSerializer
    queryset = Post.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve posts fot authenticated user."""
        return self.queryset.filter(user = self.request.user).order_by('-id')
    
    def perform_create(self, serializer):
        """Create a new post"""
        serializer.save(user = self.request.user)


class AuthorViewSet(
        mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """Manage authors in database"""
    serializer_class = serializers.AuthorSerializer
    queryset = Author.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user = self.request.user).order_by('-name')