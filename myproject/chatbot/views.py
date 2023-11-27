from . import services
from .models import Bot, Chat, Message
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_http_methods

# Create your views here.
@require_http_methods(["GET", "POST"])
@login_required(login_url='chatbot:home')
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, pk=chat_id)

    # add new msg
    if request.method == 'POST':
        previous_message = chat.message_set.order_by('-pub_date')[0]
        if previous_message.role == Message.Role.BOT:
            msg = services.create_message(chat=chat,text=request.POST['msg-text'],
                role=Message.Role.USER, previous_message=previous_message)
            
            if(chat.title == "New Chat"):
                services.openai_change_preview_title(msg)
            services.openai_add_response(msg)
    
    sorted_msg_list = chat.message_set.order_by('pub_date')
    return render(request, "chat-details.html", {"chat":chat, "sorted_msg_list":sorted_msg_list})

@require_http_methods(["GET","POST"])
@login_required(login_url='chatbot:home')
def create_chat(request):
    if request.method == 'GET':
        sorted_bot_list = Bot.objects.filter(is_active=True).order_by('title')
        return render(request,'create-chat.html', {"sorted_bot_list":sorted_bot_list})
    else:
        bot = get_object_or_404(Bot, pk=request.POST['bot'])
        if not bot.is_active:
            sorted_bot_list = Bot.objects.filter(is_active=True).order_by('title')
            return render(request,'create-chat.html', {"sorted_bot_list":sorted_bot_list})
        
        chat = Chat.objects.create(user=request.user,bot=bot)
        msg = services.create_message(chat=chat,text="Hello! How can I assist you today? If you have any questions or need information, feel free to ask.",
            role=Message.Role.BOT)
        msg.previous_message = msg
        msg.save()
        return HttpResponseRedirect(reverse("chatbot:chat_detail", args=(chat.pk,)))

@require_http_methods(["GET"])
def home(request):
    if request.user.is_authenticated:
        user = request.user
        if request.GET.get("searchChat"):
            sorted_chat_list = services.full_text_search(query=request.GET.get("searchChat")
                                                         ,search_vector = ["title", "message__text"],user=user)
        else:
            sorted_chat_list = user.chat_set.order_by('-last_message_date')
        chat_in_page = services.pagination(chat_list=sorted_chat_list,page = request.GET.get('page', 1))
        
        return render(request,'chat-list.html', {"chat_in_page":chat_in_page,"searchChat":request.GET.get("searchChat")})
    else:
        return render(request,'landing.html')

@require_http_methods(["GET","POST"])
def login(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['username'],password = request.POST['password'])
        if user is not None:
            auth.login(request,user)
            return HttpResponseRedirect(reverse("chatbot:home"))
        else:
            return render (request,'login.html', {'error_message':'Username or password is incorrect!'}, status=400)
    else:
        return render(request,'login.html')

@require_http_methods(["GET"])
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse("chatbot:login"))

@require_http_methods(["POST"])
@login_required(login_url='chatbot:home')
def msg_reaction(request, msg_id):
    msg = get_object_or_404(Message, pk=msg_id)
    reaction = request.POST['reaction']

    if(reaction == 'like'):
        msg.reaction = Message.Reaction.LIKE
    elif(reaction == 'dislike'):
        msg.reaction = Message.Reaction.DISLIKE
        if msg.role == Message.Role.BOT:
            services.openai_update_message(msg) 
    msg.save()
    
    return HttpResponseRedirect(reverse("chatbot:chat_detail", args=(msg.chat.pk,)))

@require_http_methods(["GET","POST"])
def register(request):
    if request.method == "POST":
        if request.POST['password'] == request.POST['password-confirm']:
            try:
                user = services.create_user(username=request.POST['username'],password=request.POST['password'])
                auth.login(request,user)
                return HttpResponseRedirect(reverse("chatbot:home"))
            except IntegrityError as e:
                return render (request,'register.html', {'error_message':'Email is already taken!'}, status=400)
            except Exception as e:
                 return render(request,'register.html',{'error_message':e.error_list[0]})
        else:
            return render (request,'register.html', {'error_message':'Password does not match!'}, status=400)
    else:
        return render(request,'register.html')