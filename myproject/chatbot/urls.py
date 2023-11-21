from django.urls import path
from . import views

app_name = "chatbot"

# ex: /posts/
urlpatterns = [
    path('',views.home,name="home"),
    path('createChat/',views.create_chat,name="create_chat"),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
]