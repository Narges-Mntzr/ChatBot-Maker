from . import views
from django.urls import path

app_name = "chatbot"

# ex: /posts/
urlpatterns = [
    path('',views.home,name="home"),
    path('createchat/',views.create_chat,name="create_chat"),
    path('chat/<int:chat_id>/', views.chat_detail, name="chat_detail"),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('<int:msg_id>/reaction/',views.msg_reaction, name="msg_reaction"),
]