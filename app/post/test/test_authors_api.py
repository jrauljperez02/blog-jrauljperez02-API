"""
Tests for the authors API
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase


from rest_framework import status
from rest_framework.test import APIClient

from core.models import Author
from post.serializers import AuthorSerializer

AUTHORS_URL = reverse('post:author-list')

def detail_url(author_id):
    """Create and return an author detail URL"""
    return reverse('post:author-detail', args=[author_id])

def create_user(email =  'test@example.com', password = 'testpassword123'):
    """Create and return a new user"""
    return get_user_model().objects.create(email = email, password = password)

class PublicAuthorsAPITests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()
    
    def test_auth_required(self):
        """Test auth is required for retrieving authors"""
        res = self.client.get(AUTHORS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    
class PrivateAuthorsAPITests(TestCase):
    """Test authtenticated API requests"""

    def setUp(self):
        self.client =  APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_authors(self):
        """Test retrieve a list of authors"""
        Author.objects.create(
            user = self.user,
            name = 'Author 1',
            link = 'http://www.author1.com',
            profile_picture = 'http://www.profile1.com',
            description = 'Sample Test Description Author 1',
        )

        Author.objects.create(
            user = self.user,
            name = 'Author 2',
            link = 'http://www.author2.com',
            profile_picture = 'http://www.author2.com',
            description = 'Sample Test Description Author2',
        )
        res = self.client.get(AUTHORS_URL)
        
        authors = Author.objects.all().order_by('-name')
        serializer = AuthorSerializer(authors, many = True)
        # self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_authors_limited_to_user(self):
        """Test list of authors is limited to authenticated users"""
        user2 = create_user(email = 'user2@example.com')
        Author.objects.create(
            user = user2,
            name = 'AUTHOR1',
            link = 'http://www.author2.com',
            profile_picture = 'http://www.author2.com',
            description = 'Sample Test Description Author2',
        )
        author = Author.objects.create(
            user = self.user,
            name = 'AUTHOR SELF USER',
            link = 'http://www.author.com',
            profile_picture = 'http://www.author.com',
            description = 'Sample Test Description Author',
        )

        res = self.client.get(AUTHORS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], author.name)
        self.assertEqual(res.data[0]['id'], author.id)
        

    def test_update_author(self):
        """Test update a single author"""
        author = Author.objects.create(
            user = self.user,
            name = 'AUTHOR1',
            link = 'http://www.author2.com',
            profile_picture = 'http://www.author2.com',
            description = 'Sample Test Description Author2',
        )

        payload = {
            'name': 'New Author',
        }
        url = detail_url(author.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        author.refresh_from_db()
        self.assertEqual(author.name, payload['name'])

    
    def test_delete_author(self):
        """Test delete a single author"""
        author = Author.objects.create(
            user = self.user,
            name = 'Raul',
            link = 'http://www.raul.com',
            profile_picture = 'http://www.profile.com',
            description = 'Sample Test Description Raul',
        )
        url = detail_url(author.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        authors = Author.objects.filter(user = self.user)
        self.assertFalse(authors.exists())


