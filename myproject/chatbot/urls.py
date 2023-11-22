from django.urls import path
from . import views

app_name = "chatbot"

# ex: /posts/
urlpatterns = [
    path('',views.home,name="home"),
    path('createChat/',views.create_chat,name="create_chat"),
    path('chat/<int:chat_id>/', views.chat_detail, name="chat_detail"),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
]