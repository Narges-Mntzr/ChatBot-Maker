from .models import Bot, BotContent, Chat, Message
from .functions import openai_get_embedding, similar_content
from django.contrib.auth.models import User
# Create your tests here.
from django.conf import settings
from django.test import TestCase
import json
import logging
import random


# Create your tests here.
class OpenAiFunctionTests(TestCase):
    def test_similarity_function(self):
        user = User.objects.create_user(username="test1@gmail.com",password="passTest1")
        bot = Bot.objects.create(user=user, title="botTest1", detail = "this is botTest1", img="test.png")
        
        contents = json.load(open(f'{settings.BASE_DIR}/chatbot/data/data.json'))
        random.shuffle(contents['similar_data'])
        answers, trueAnswers = 0, 0
        testSize = 50

        for i in range(testSize):
            d = contents['similar_data'][i]
            botcontent = BotContent.objects.create(bot=bot,text=d["doc"])
            botcontent.embedding = openai_get_embedding(botcontent)
            botcontent.save()

        for i in range(testSize):
            d = contents['similar_data'][i]
            chat = Chat.objects.create(user=user, bot=bot)
            message = Message.objects.create(chat=chat,text=d["question"], 
                                             role=Message.Role.USER)
            
            if(similar_content(message).text==d["doc"]):
                trueAnswers+=1
            answers+=1

        logging.debug(f'number of true answer: {trueAnswers} / {answers}')            
    
class AuthenticationViewsTests(TestCase):
    def register_user(self,username,password,password2):
        data = {'username': username , 'password': password, 'password-confirm': password2}
        response = self.client.post("/chatbot/register/", data)
        return response
    
    def login_user(self,username,password):
        data = {'username': username, 'password': password}
        response = self.client.post("/chatbot/login/", data)
        return response

    #Tests
    def test_not_register(self):
        response = self.login_user(username = 'test@gmail.com',password='testPassword')
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'login.html')
        self.assertQuerysetEqual(
            response.context['error_message'],
            'Username or password is incorrect!',
        )

    def test_register_not_match(self):
        response = self.register_user(username = 'test@gmail.com',password='testPassword',password2='testPassword2')
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'register.html')
        self.assertQuerysetEqual(
            response.context['error_message'],
            'Password does not match!',
        )

    def test_register(self):
        response = self.register_user(username = 'test@gmail.com',password='testPassword',password2='testPassword')
        self.assertEqual(response.status_code, 302)  # 302 is the status code for HttpResponseRedirect
        self.assertRedirects(response, '/chatbot/')

    def test_login(self):
        self.register_user(username = 'test@gmail.com',password='testPassword',password2='testPassword')
        response = self.login_user(username = 'test@gmail.com',password='testPassword')
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, '/chatbot/')

    def test_register_duplicate_email(self):
        self.register_user(username = 'test@gmail.com',password='testPassword',password2='testPassword')
        response = self.register_user(username = 'test@gmail.com',password='testPassword2',password2='testPassword2')
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'register.html')
        self.assertQuerysetEqual(
            response.context['error_message'],
            'Email is already taken!',
        )

    def test_logout(self):
        self.register_user(username = 'test@gmail.com',password='testPassword',password2='testPassword')
        self.login_user(username = 'test@gmail.com',password='testPassword')
        response = self.client.get("/chatbot/logout/")
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, '/chatbot/login/')

        response = self.client.get("/chatbot/")
        self.assertTemplateUsed(response, 'landing.html')

class ChatsViewsTests(TestCase):
    def register_login_user(self):
        data = {'username': 'test@gmail.com' , 'password': 'testPassword', 'password-confirm': 'testPassword'}
        self.client.post("/chatbot/register/", data)
        data = {'username': 'test@gmail.com', 'password': 'testPassword'}
        self.client.post("/chatbot/login/", data)

    def create_bot(self):
        user = User.objects.create_user(username="test1@gmail.com",password="testPassword1")
        bot = Bot.objects.create(user=user, title="botTest1", detail = "this is botTest1", img="test.png")
        return bot


    def test_home_not_loggin(self):
        response = self.client.get("/chatbot/")
        self.assertTemplateUsed(response, 'landing.html')

    def test_home_loggin(self):
        self.register_login_user()
        response = self.client.get("/chatbot/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat-list.html')
        self.assertQuerysetEqual(response.context['chat_in_page'],[])
        self.assertQuerysetEqual(response.context['searchChat'],"")

    def test_home_fullTextSearch(self):
        self.register_login_user()
        response = self.client.get("/chatbot/",{'searchChat': 'cook'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat-list.html')
        self.assertQuerysetEqual(response.context['chat_in_page'],[])
        self.assertQuerysetEqual(response.context['searchChat'],"cook")

    def test_home_one_chat(self):
        self.register_login_user()
        bot = self.create_bot()
        response = self.client.get("/chatbot/createchat/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create-chat.html')
        self.assertQuerysetEqual(response.context['sorted_bot_list'],[bot])

        data = {'bot': bot.id}
        response = self.client.post("/chatbot/createchat/", data)
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, '/chatbot/chat/1/')