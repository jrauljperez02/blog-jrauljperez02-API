import profile
from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    """Manager for users."""
    def create_user(self, email, password = None, **extra_fields):
        """Create, save adn return a new user."""
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(email =  self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using =  self._db)

        return user


    def create_superuser(self, email, password):
        """Create, save and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True

        user.save(using = self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    email = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    is_staff = models.BooleanField(default=False)
    is_active  = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

class Post(models.Model):
    """Post model objects."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    img_description = models.URLField()
    slug = models.CharField(max_length=255)

    authors = models.ManyToManyField('Author')

    def __str__(self):
        return self.title


class Author(models.Model):
    """Author model objects."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
    )
    name = models.CharField(max_length=255)
    link = models.URLField()
    profile_picture = models.URLField()
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.name
 