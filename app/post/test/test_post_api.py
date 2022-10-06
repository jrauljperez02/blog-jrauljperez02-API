"""
Tests for post APIs
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


from rest_framework import status
from rest_framework.test import APIClient

from core.models import Author, Post
from post.serializers import PostSerializer

POST_URL = reverse('post:post-list')

def detail_url(post_id):
    """Create and return a  post detail url"""
    return reverse('post:post-detail', args = [post_id])

def create_post(user, **params):
    """Create and return a sample post"""
    defaults = {
        'title' : 'Post Title',
        'description' : 'Post description',
        'img_description' :  'http://placehold.it',
        'slug' : 'slug-test',
    }
    defaults.update(params)

    post = Post.objects.create(user=user, **defaults)
    return post

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)

class PublicPostAPITest(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()
    
    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(POST_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    
class PrivatePostAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email = 'user@example.com',
            password = 'testpassword123'
        )
        self.client.force_authenticate(self.user)
    
    def test_retrieve_posts(self):
        """Test retrieving a list of posts"""
        create_post(user = self.user)
        create_post(user = self.user)

        res = self.client.get(POST_URL)

        posts = Post.objects.all().order_by('-id')
        serializer = PostSerializer(posts, many = True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_post_list_limited_to_user(self):
        """Test list of posts if limited to authenticated users."""
        other_user = create_user(email='other@example.com', password='test123')
        create_post(user = other_user)
        create_post(user = self.user)

        res = self.client.get(POST_URL)
        
        posts = Post.objects.filter(user = self.user)
        serializer = PostSerializer(posts, many = True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)   
        self.assertEqual(res.data, serializer.data)

    def test_get_post_detail(self):
        """Test get post detail"""

        post = create_post(user = self.user)

        url = detail_url(post.id)
        res = self.client.get(url)

        serializer = PostSerializer(post)
        self.assertEqual(res.data, serializer.data)

    def test_create_post(self):
        """Test creating a post"""
        payload = {
            'title' : 'Sample Title',
            'description' : 'Sample Description',
            'img_description' : 'http://placehold.png',
            'slug' : 'slug-test'
        }
        res = self.client.post(POST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        post = Post.objects.get(id = res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(post, k), v)
        self.assertEqual(post.user, self.user)

    def test_partial_update(self):
        """Test partial update"""

        original_slug = 'test-slug'
        post = create_post(
            user = self.user,
            title = 'Sample Test Title',
            slug = original_slug,
        )

        payload = {'title': 'New Test Title',}
        url = detail_url(post.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, payload['title'])
        self.assertEqual(post.slug, original_slug)
        self.assertEqual(post.user, self.user)
    
    def test_full_update(self):
        """Test full update of post"""
        post = create_post(
            user = self.user,
            title = 'Sample Test Title',
            description = 'Sample Test Description',
            img_description = 'http://placehold.it/',
            slug = 'sample-test',
        )
        payload = {
            'title': 'New Test Title',
            'description': 'New Test Description',
            'img_description': 'http://new-image.png',
            'slug' : 'slug-new-test'
        }
        url = detail_url(post.id)
        res =  self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(post, k), v)
        self.assertEqual(post.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the post user results in an error"""
        new_user = create_user(email = 'user2@example.com', password = 'testpassword123')
        post = create_post(user = self.user)

        payload = {'user': new_user.id}
        url = detail_url(post.id)
        self.client.patch(url, payload)

        post.refresh_from_db()
        self.assertEqual(post.user, self.user)
    
    def test_delete_post(self):
        """Test deleting a post successful."""
        post = create_post(user = self.user)

        url = detail_url(post.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id = post.id).exists())

    def test_post_other_users_post_error(self):
        """Test trying to delete another users post gives error"""

        new_user = create_user(email = 'user2@example.com', password = 'testpassword123')
        post = create_post(user = new_user)

        url = detail_url(post.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Post.objects.filter(id = post.id).exists())

    def test_create_post_with_new_authors(self):
        """Test creating a post with new authors"""
        payload = {
            'title' : 'Sample Test Author',
            'description' : 'Sample Test Description',
            'img_description' : 'http://example.com',
            'slug' : 'slug-test',
            'authors' : [
                {
                    'name' : 'Jesus',
                    'link' : 'http://example.com',
                    'profile_picture' : 'http://example-facebook.com',
                    'description' : 'Sample Test Description 1'
                },
                {
                    'name' :  'Sample Name',
                    'link' : 'http://example2.com',
                    'profile_picture' : 'https://example-facebook2.com',
                    'description' : 'Sample Test Description 2',
                }
            ]
        }

        res = self.client.post(POST_URL, payload, format = 'json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        posts = Post.objects.filter(user = self.user)
        self.assertEqual(posts.count(), 1)
        post = posts[0]

        self.assertEqual(post.authors.count(), 2)
        for author in payload['authors']:
            exists = post.authors.filter(
                name = author['name'],
                link = author['link'],
                profile_picture = author['profile_picture'],
                description = author['description'],
                user = self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_post_with_existing_authors(self):
        """Test creating a post with existing author"""
        raul_author = Author.objects.create(
            user = self.user,
            name = 'Raul',
            link = 'http://www.raul.com',
            profile_picture = 'http://www.profile.com',
            description = 'Sample Test Description Raul',
        )
        payload = {
            'title' : 'Sample Test Author',
            'description' : 'Sample Test Description',
            'img_description' : 'http://example.com',
            'slug' : 'slug-test',
            'authors' : [
                {
                    'name' : 'Raul',
                    'link' : 'http://www.raul.com',
                    'profile_picture' : 'http://www.profile.com',
                    'description' : 'Sample Test Description Raul'
                },
                {
                    'name' :  'Sample Name',
                    'link' : 'http://example2.com',
                    'profile_picture' : 'https://example-facebook2.com',
                    'description' : 'Sample Test Description 2',
                }
            ]
        }
        res = self.client.post(POST_URL, payload, format = 'json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        posts = Post.objects.filter(user = self.user)
        self.assertEqual(posts.count(), 1)
        post = posts[0]
        self.assertEqual(post.authors.count(), 2)
        self.assertIn(raul_author, post.authors.all())
        for author in payload['authors']:
            exists = post.authors.filter(
                name = author['name'],
                link = author['link'],
                profile_picture = author['profile_picture'],
                description = author['description'],
                user = self.user,
            ).exists()
            self.assertTrue(exists)
    
    def test_create_author_on_update(self):
        """Test create a new author updating a post"""
        post = create_post(user = self.user)

        payload = {
            'authors' : [
                {
                    'name' : 'Jesus',
                    'link' : 'http://example.com',
                    'profile_picture' : 'http://example-facebook.com',
                    'description' : 'Sample Test Description 1'
                }
            ]
        }
        url = detail_url(post.id)
        res = self.client.patch(url, payload, format = 'json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_author = Author.objects.get(user = self.user, name = 'Jesus')
        self.assertIn(new_author, post.authors.all())
        
    
    def test_update_post_assign_author(self):
        """Test assigning an existing author when updating a post"""
        author1 = Author.objects.create(
            user = self.user,
            name = 'Author 1',
            link = 'http://www.author1.com',
            profile_picture = 'http://www.profile-picture1.com',
            description = 'Sample Test Description Author 1',
        )
        post = create_post(user = self.user)
        post.authors.add(author1)



        author2 = Author.objects.create(
            user = self.user,
            name = 'Author 2',
            link = 'http://www.author2.com',
            profile_picture = 'http://www.profile-picture2.com',
            description = 'Sample Test Description Author 2',
        )
        payload = {
            'authors' : [
                {
                    'name' : 'Author 2',
                    'link' : 'http://www.author2.com',
                    'profile_picture' : 'http://www.profile-picture2.com',
                    'description' : 'Sample Test Description Author 2',
                }
            ]
        }
        url = detail_url(post.id)
        res = self.client.patch(url, payload, format = 'json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(author2, post.authors.all())
        self.assertNotIn(author1, post.authors.all())

    def test_clear_authors(self):
        """Test clearing a post author list"""
        author = Author.objects.create(
            user = self.user,
            name = 'Raul',
            link = 'http://www.raul.com',
            profile_picture = 'http://www.profile.com',
            description = 'Sample Test Description Raul',
        )
        post = create_post(user = self.user)
        post.authors.add(author)

        payload = {'authors' : []}

        url = detail_url(post.id)
        res = self.client.patch(url, payload, format = 'json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(post.authors.count(), 0)
        