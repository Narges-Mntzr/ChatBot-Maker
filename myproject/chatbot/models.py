from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here.
class Bot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=20, unique=True)
    detail = models.TextField(max_length=1000)
    img = models.ImageField(upload_to='chatbot/')
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
    title = models.CharField(max_length=50)
    create_date = models.DateTimeField(default=timezone.now)
    last_message_date = models.DateTimeField(default=timezone.now)

class Reaction(models.TextChoices):
    LIKE = ('like', 'Like')
    DISLIKE = ('dislike', 'Dislike')
    NONE = ('none', 'None')

class MessageRole(models.TextChoices):
    USER = ('user','User')
    BOT = ('bot','Bot')

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    text = models.TextField(max_length=800)
    pub_date = models.DateTimeField(default=timezone.now)
    is_answer = models.CharField(max_length=20, choices=MessageRole.choices, null=False)
    reaction = models.CharField(max_length=20, choices=Reaction.choices, default=Reaction.NONE)

    def __str__(self):
        return f"{self.text}"
    
