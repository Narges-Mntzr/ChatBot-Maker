from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Create your models here.
class Bot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=20, unique=True)
    detail = models.TextField(max_length=1000)
    img = models.ImageField(upload_to='images/')
    #TODO: what is prompt?
    prompt = models.TextField(max_length=1000)
    is_active = models.BooleanField(null=False, default=True)

    def __str__(self):
        return f"{self.title}"

class BotContent(models.Model):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    text = models.TextField(max_length=800)

    def __str__(self):
        return f"{self.text}"

class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    create_date = models.DateTimeField(default=timezone.now)

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    text = models.TextField(max_length=800)
    pub_date = models.DateTimeField(default=timezone.now)
    is_answer = models.BooleanField(null=False, default=False)

    REACTION = (
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('none', 'None'),
    )
    reaction = models.CharField(max_length=20, choices=REACTION, default='none')

    def __str__(self):
        return f"{self.text}"