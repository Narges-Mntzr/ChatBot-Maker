from chatbot.functions import openai_add_response, openai_change_preview_title
from chatbot.models import Bot, Chat, MessageRole
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
        msg = chat.message_set.create(chat=chat,text=request.POST['msg-text'],
            role=MessageRole.USER)
        
        if(chat.title == "New Chat"):
            openai_change_preview_title(chat, msg)
        openai_add_response(chat, msg)
    
    sorted_msg_list = chat.message_set.order_by('pub_date')
    return render(request, "chat-details.html", {"chat":chat, "sorted_msg_list":sorted_msg_list})

@require_http_methods(["GET","POST"])
@login_required(login_url='chatbot:home')
def create_chat(request):
    if request.method == 'GET':
        sorted_bot_list = Bot.objects.order_by('title')
        return render(request,'create-chat.html', {"sorted_bot_list":sorted_bot_list})
    else:
        bot = get_object_or_404(Bot, pk=request.GET.get('bot', 1))
        chat = Chat.objects.create(user=request.user,bot=bot)
        chat.message_set.create(chat=chat,text="Hello! How can I assist you today? If you have any questions or need information, feel free to ask.",
            role=MessageRole.BOT)
        return HttpResponseRedirect(reverse("chatbot:chat_detail", args=(chat.pk,)))

@require_http_methods(["GET"])
def home(request):
    if request.user.is_authenticated:
        user = request.user
        sorted_chat_list = user.chat_set.order_by('-last_message_date')
        page = request.GET.get('page', 1)
        paginator = Paginator(sorted_chat_list, 5)
        try:
            chat_in_page = paginator.page(page)
        except PageNotAnInteger:
            chat_in_page = paginator.page(1)
        except EmptyPage:
            chat_in_page = paginator.page(paginator.num_pages)
        return render(request,'chat-list.html', {"chat_in_page":chat_in_page})
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
            return render (request,'login.html', {'error_message':'Username or password is incorrect!'})
    else:
        return render(request,'login.html')

def logout(request):
    #todo: GET or POST
    if request.method == 'GET':
        auth.logout(request)
    return HttpResponseRedirect(reverse("chatbot:login"))

@require_http_methods(["GET","POST"])
def register(request):
    if request.method == "POST":
        if request.POST['password'] == request.POST['password-confirm']:
            try:
                validate_password(request.POST['password'])
                user = User.objects.create_user(username=request.POST['username'],password=request.POST['password'])
                if(request.POST['group']!='normal'):
                    group = Group.objects.get(name=request.POST['group'])
                    user.groups.add(group)
                auth.login(request,user)
                return HttpResponseRedirect(reverse("chatbot:home"))
            except IntegrityError as e:
                return render (request,'register.html', {'error_message':'email is already taken!'})
            except Exception as e:
                 return render(request,'register.html',{'error_message':e.error_list[0]})
        else:
            return render (request,'register.html', {'error_message':'Password does not match!'})
    else:
        return render(request,'register.html')


    
