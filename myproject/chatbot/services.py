from .models import BotContent, Message
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from openai import OpenAI
from pgvector.django import CosineDistance

client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)

def create_message(chat, text, role, previous_message = None, pub_date = timezone.now()):
    msg = chat.message_set.create(chat=chat,text=text,role=role,previous_message=previous_message,
                pub_date = pub_date)
    
    msg.chat.last_message_date = max(msg.chat.last_message_date,msg.pub_date)
    msg.chat.save()
    
    return msg

def create_user(username, password):
    validate_password(password)
    user = User.objects.create_user(username=username,password=password)
    return user

def full_text_search(query,search_vector,user):
    search_vector = SearchVector(*search_vector)
    search_query = SearchQuery(query)
    sorted_chat_list = user.chat_set.annotate( search=search_vector, 
                                rank= SearchRank(search_vector, search_query)
                                        ).filter(search=search_query).order_by("-id").distinct('id')
    return sorted_chat_list

def get_prompt(Question, related_botcontent_text=None):
    if(not related_botcontent_text):
        return ( f'''
            Check your answer several times and give acceptable answer to the following question.
            Question: {Question} ''')
    
    return (f''' 
    "{related_botcontent_text}"
    Check your answer several times and give acceptable answer to the following question, The document above may help you, 
    Question: {Question}''')

def openai_add_response(msg):
    msg.related_botcontent = similar_content(msg)
    msg.save()
    messages = [{"role":"system", "content":msg.chat.bot.prompt}] 
    
    # msg isn't first msg in chat
    if msg.previous_message != msg.previous_message.previous_message:
        preQuestion = msg.previous_message.previous_message
        messages.append({"role":"user", "content":get_prompt(Question = preQuestion.text,
                                                         related_botcontent_text = preQuestion.related_botcontent.text if preQuestion.related_botcontent else None)})
        messages.append({"role":"assistant", "content":msg.previous_message.text})
    messages.append({"role":"user", "content":get_prompt(Question = msg.text,
                                                         related_botcontent_text = msg.related_botcontent.text if msg.related_botcontent else None)})
    

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    create_message(chat=msg.chat,text=response.choices[0].message.content,
            role=Message.Role.BOT,previous_message=msg)

def openai_change_preview_title(msg):
    titlePrompt = f'''Choose a title for a conversation starter using this message
    with a maximum of 3 words.\n{msg.text}'''
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system", "content":msg.chat.bot.prompt},
            {"role":"user", "content":titlePrompt}
        ],
    )
    msg.chat.title = response.choices[0].message.content[1:-1]
    msg.chat.preview = msg.text[:45]
    msg.chat.save()

def openai_get_embedding(msg):
    response = client.embeddings.create(
        input = [msg.text],
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def openai_update_message(msg):
    messages = [{"role":"system", "content":msg.chat.bot.prompt}] 
    # msg isn't first msg in chat
    completePreMsg = get_prompt(Question = msg.previous_message.text,
                                related_botcontent_text = msg.previous_message.related_botcontent.text if msg.previous_message.related_botcontent else None)
    messages.append({"role":"user", "content":completePreMsg})
    messages.append({"role":"assistant", "content":str(msg)})
    
    completePreMsgV2 = f''' I have asked you this question once again, but your answer was not appropriate. Be more careful and give me a better answer.
        {completePreMsg}
    '''
    messages.append({"role":"user", "content":completePreMsgV2})
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    create_message(chat=msg.chat,text=response.choices[0].message.content,
            role=Message.Role.BOT,previous_message=msg.previous_message,
            pub_date = msg.pub_date + timedelta(microseconds=100))

def pagination(chat_list, page):
    chat_cnt_each_page = 5
    paginator = Paginator(chat_list, chat_cnt_each_page)
    try:
        chat_in_page = paginator.page(page)
    except PageNotAnInteger:
        chat_in_page = paginator.page(1)
    except EmptyPage:
        chat_in_page = paginator.page(paginator.num_pages)

    return chat_in_page

def similar_content(msg):
    msg_embedding = openai_get_embedding(msg)
    output = BotContent.objects.filter(bot=msg.chat.bot).order_by(CosineDistance('embedding', msg_embedding))
    if(len(output) == 0):
        return None
    return output[0]


