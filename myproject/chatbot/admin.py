from .models import Bot, BotContent, Chat, Message
from .services import openai_get_embedding
from django.contrib import admin
from django.db.models import Count, Q

@admin.display(description="Like - Dislike")
def like_number(obj):
    reaction_counts = Message.objects.filter(chat__bot=obj).values('reaction').annotate(count=Count('reaction'))
    
    reactions={'like':0,'dislike':0}
    for rc in reaction_counts:
        reactions[rc['reaction']] = rc['count']

    return f"{reactions['like']} - {reactions['dislike']}"

# Register your models here.
class BotAdmin(admin.ModelAdmin):

    list_display = ('id','user','title','is_active',like_number)
    search_fields = ['user__username','title']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # If the user is in the 'chatbotMaker' group, disable the user field and set it to the current user
        if request.user.groups.filter(name='chatbotMaker').exists():
            form.base_fields['user'].widget.attrs['disabled'] = True
            form.base_fields['user'].required = False
            form.base_fields['user'].initial = request.user

        return form
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='chatbotMaker').exists():
            return qs.filter(user=request.user)
        return qs
    
    def save_model(self, request, obj, form, change):
        # If the user is in the 'chatbotMaker' group, set the user field to the current user
        if request.user.groups.filter(name='chatbotMaker').exists():
            obj.user = request.user
        promptSuffix = "If you don't know the right answer, don't answer it."
        if( not obj.prompt.endswith(promptSuffix) ):
            obj.prompt = f'{obj.prompt}\n {promptSuffix}' 
        obj.save()

class BotContentAdmin(admin.ModelAdmin):
    
    list_display = ('id','bot')
    search_fields = ['bot__title']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'bot' and request.user.groups.filter(name='chatbotMaker').exists():
            # Filter choices for bot based on the current user
            kwargs['queryset'] = db_field.related_model.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['embedding'].widget.attrs['disabled'] = True
        form.base_fields['embedding'].required = False
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # If the user is in the 'chatbotMaker' group, filter by user
        if request.user.groups.filter(name='chatbotMaker').exists():
            return qs.filter(bot__user=request.user)
        return qs
    
    def save_model(self, request, obj, form, change):
        obj.embedding = openai_get_embedding(obj)
        obj.save()

class ChatAdmin(admin.ModelAdmin):
    list_display = ('id','user','title','bot','title')
    search_fields = ['user__username','title','message__text']

admin.site.register(Bot, BotAdmin)
admin.site.register(BotContent, BotContentAdmin)
admin.site.register(Chat, ChatAdmin)
admin.site.register(Message)