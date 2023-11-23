from .models import BotContent, Message
from datetime import timedelta
from django.conf import settings
from openai import OpenAI
from pgvector.django import CosineDistance

client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)

def similar_content(msg):
    msg_embedding = openai_get_embedding(msg)
    output = BotContent.objects.filter(bot=msg.chat.bot).order_by(CosineDistance('embedding', msg_embedding))
    if(len(output) == 0):
        return None
    return output[0]
        

def openai_add_response(msg):
    #todo: can be better
    msg.related_botcontent = similar_content(msg)
    msg.save()
    messages = [{"role":"system", "content":msg.chat.bot.prompt}] 
    # msg isn't first msg in chat
    if msg.previous_message != msg.previous_message.previous_message:
        messages.append({"role":"user", "content":msg.previous_message.previous_message.msg_with_relatedcontent()})
        messages.append({"role":"assistant", "content":str(msg.previous_message)})
    messages.append({"role":"user", "content":msg.msg_with_relatedcontent()})
    

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    msg.chat.message_set.create(chat=msg.chat,text=response.choices[0].message.content,
            role=Message.Role.BOT,previous_message=msg)

def openai_change_preview_title(msg):
    titlePrompt = f'''Come up with a creative title for a conversation starter using this message
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
    try:
        response = client.embeddings.create(
            input = [msg.text],
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    except:
        return openai_get_embedding(msg)

def openai_update_message(msg):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        # todo: add more msg and say i am not ok
        messages=[
            {"role":"system", "content":msg.chat.bot.prompt},
            {"role":"user", "content":msg.previous_message.text}
        ],
    )
    msg.chat.message_set.create(chat=msg.chat,text=response.choices[0].message.content,
            role=Message.Role.BOT,previous_message=msg.previous_message,
            pub_date = msg.pub_date + timedelta(microseconds=100))