from django.contrib import admin
from chatbot.models import Bot, BotContent, Chat, Message

# Register your models here.
admin.site.register(Bot)
admin.site.register(BotContent)
admin.site.register(Chat)
admin.site.register(Message)