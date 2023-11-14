from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager

# Create your models here.
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('admin', 'Admin'),
        ('user', 'User'),
        ('maker', 'Maker')
        # Add more roles as needed
    )
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=20, choices=ROLES, default='user')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['role']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Tag(models.Model):
    title = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.title}"


class Post(models.Model):
    title = models.CharField(max_length=30)
    text = models.TextField(max_length=1000)
    pub_date = models.DateTimeField("data published", default=timezone.now)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return f"{self.title}"


class Comment(models.Model):
    title = models.CharField(max_length=20)
    text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("data published", default=timezone.now)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title}"