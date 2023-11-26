from .models import Message 
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Message)
def message_post_save(sender, instance, created, **kwargs):
    if created:
        instance.chat.last_message_date = max(instance.chat.last_message_date,instance.pub_date)
        instance.chat.save()