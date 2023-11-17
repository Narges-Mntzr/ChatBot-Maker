from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

# Create your views here.
# @login_required(login_url='chatbot:home')
def home(request):
    if request.user.is_authenticated:
        return render(request,'chatbot/chat-list.html')
    else:
        return render(request,'chatbot/landing.html')

def login(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['username'],password = request.POST['password'])
        if user is not None:
            auth.login(request,user)
            return HttpResponseRedirect(reverse("chatbot:home"))
        else:
            return render (request,'chatbot/login.html', {'error_message':'Username or password is incorrect!'})
    else:
        return render(request,'chatbot/login.html')

def logout(request):
    #todo: GET or POST
    if request.method == 'GET':
        auth.logout(request)
    return HttpResponseRedirect(reverse("chatbot:login"))

def register(request):
    if request.method == "POST":
        if request.POST['password'] == request.POST['password-confirm']:
            try:
                validate_password(request.POST['password'])
                user = User.objects.create_user(request.POST['username'],password=request.POST['password'])
                if(request.POST['group']!='normal'):
                    group = Group.objects.get(name=request.POST['group'])
                    user.groups.add(group)
                auth.login(request,user)
                return HttpResponseRedirect(reverse("chatbot:home"))
            except IntegrityError as e:
                return render (request,'chatbot/register.html', {'error_message':'email is already taken!'})
            except Exception as e:
                 return render(request,'chatbot/register.html',{'error_message':e.error_list[0]})
        else:
            return render (request,'chatbot/register.html', {'error_message':'Password does not match!'})
    else:
        return render(request,'chatbot/register.html')


    
