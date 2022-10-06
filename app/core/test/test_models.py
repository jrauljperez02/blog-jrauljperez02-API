"""
Test for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

def create_user(email = 'test@example.com', password = 'testpassword123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_success(self):
        """Test creating a user with an email is successful"""
        email = 'test@example.com'
        password = 'testpassword123'

        user = get_user_model().objects.create_user(
            email =  email, 
            password = password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""

        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)
    
    def test_new_user_without_email_raises_error(self):
        """Test that creating a new user without email raise a ValueError"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'sample123')
            
    def test_create_superuser(self):
        """Test creating a superuser"""

        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_Post(self):
        """Test creating a post is successful"""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpassword123',
        )
        post = models.Post.objects.create(
            user = user,
            title = 'Sample Test Title',
            description = 'Sample Test Description',
            img_description = 'http://image.png',
            slug = 'sample-slug'
        )
        self.assertEqual(str(post), post.title)

    def test_create_author(self):
        """Test creating a new author is successful"""
        user = create_user()
        author = models.Author.objects.create(
            user = user, 
            name = 'Sample Name',
            link = 'http://example.com',
            profile_picture = 'http://example.png',
            description = 'Sample Test Description',
        )
        self.assertEqual(str(author), author.name)