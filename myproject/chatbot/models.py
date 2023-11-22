from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here.
class Bot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=20, unique=True)
    detail = models.TextField(max_length=1000)
    img = models.ImageField(upload_to='chatbot/')
    prompt = models.TextField(max_length=1000, default= "I'm a helpful assistant.")
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
    title = models.CharField(max_length=30, default="New Chat")
    preview = models.TextField(max_length=50, default="How can I assist you today?")
    create_date = models.DateTimeField(default=timezone.now)
    last_message_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title}"

class Message(models.Model):
    class Reaction(models.TextChoices):
        LIKE = ('like', 'Like')
        DISLIKE = ('dislike', 'Dislike')
        NONE = ('none', 'None')

    class Role(models.TextChoices):
        USER = ('user','User')
        BOT = ('bot','Bot')

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    previous_message = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    text = models.TextField(max_length=800)
    pub_date = models.DateTimeField(default=timezone.now)
    role = models.CharField(max_length=20, choices=Role.choices, null=False)
    reaction = models.CharField(max_length=20, choices=Reaction.choices, default=Reaction.NONE)

    def __str__(self):
        return f"{self.text}"