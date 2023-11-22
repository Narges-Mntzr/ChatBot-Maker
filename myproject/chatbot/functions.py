from chatbot.models import MessageRole
from django.conf import settings
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url='https://openai.torob.ir/v1')

def openai_add_response(chat, msg):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        # todo: add more msg
        messages=[
            {"role":"system", "content":chat.bot.prompt},
            {"role":"user", "content":msg.text}
        ],
    )
    chat.message_set.create(chat=chat,text=response.choices[0].message.content,
            role=MessageRole.BOT)

def openai_change_preview_title(chat, msg):
    titlePrompt = f'''Come up with a creative title for a conversation starter using this message
      with a maximum of 20 characters.\n{msg.text}'''
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system", "content":chat.bot.prompt},
            {"role":"user", "content":titlePrompt}
        ],
    )
    chat.title = response.choices[0].message.content[1:-1]
    chat.preview = msg.text[:45]
    chat.save()