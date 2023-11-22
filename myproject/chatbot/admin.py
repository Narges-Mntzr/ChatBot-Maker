from .models import Bot, BotContent, Chat, Message
from django.contrib import admin

# Register your models here.

class BotAdmin(admin.ModelAdmin):

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
        # If the user is in the 'maker' group, set the user field to the current user
        if request.user.groups.filter(name='chatbotMaker').exists():
            obj.user = request.user
        obj.save()

class BotContentAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'bot' and request.user.groups.filter(name='chatbotMaker').exists():
            # Filter choices for bot based on the current user
            kwargs['queryset'] = db_field.related_model.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # If the user is in the 'maker' group, filter by user
        if request.user.groups.filter(name='chatbotMaker').exists():
            return qs.filter(bot__user=request.user)
        return qs

admin.site.register(Bot, BotAdmin)
admin.site.register(BotContent, BotContentAdmin)
admin.site.register(Chat)
admin.site.register(Message)