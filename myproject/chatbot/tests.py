from .models import Bot, BotContent, Chat, Message
from .functions import openai_get_embedding, similar_content
from django.contrib.auth.models import User
from django.conf import settings
from django.test import TestCase
import json
import logging


# Create your tests here.
class OpenAiFunctionTests(TestCase):
    def test_similarity_function(self):
        user = User.objects.create_user(username="test1@gmail.com",password="passTest1")
        bot = Bot.objects.create(user=user, title="botTest1", detail = "this is botTest1", img="test.png")
        
        contents = json.load(open(f'{settings.BASE_DIR}/chatbot/data/data.json'))
        # for d in contents['similar_data']:
        for i in range(50):
            d = contents['similar_data'][i]
            botcontent = BotContent.objects.create(bot=bot,text=d["doc"])
            botcontent.embedding = openai_get_embedding(botcontent)
            botcontent.save()

        trueAnswers = 0
        answers = 0
        # for d in contents['similar_data']:
        for i in range(50):
            d = contents['similar_data'][i]
            chat = Chat.objects.create(user=user, bot=bot)
            message = Message.objects.create(chat=chat,text=d["question"], 
                                             role=Message.Role.USER)
            
            if(similar_content(message).text==d["doc"]):
                trueAnswers+=1
            answers+=1

        logging.debug(f'number of true answer: {trueAnswers} / {answers}')            