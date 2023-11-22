from chatbot.models import MessageReaction, MessageRole
from django.conf import settings
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url='https://openai.torob.ir/v1')

def openai_add_response(msg):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        # todo: add more msg
        messages=[
            {"role":"system", "content":msg.chat.bot.prompt},
            {"role":"user", "content":msg.text}
        ],
    )
    msg.chat.message_set.create(chat=msg.chat,text=response.choices[0].message.content,
            role=MessageRole.BOT,previous_message=msg)

def openai_change_preview_title(msg):
    titlePrompt = f'''Come up with a creative title for a conversation starter using this message
      with a maximum of 20 characters.\n{msg.text}'''
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

def openai_update_message(msg):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        # todo: add more msg
        messages=[
            {"role":"system", "content":msg.chat.bot.prompt},
            {"role":"user", "content":msg.previous_message.text}
        ],
    )
    msg.text=response.choices[0].message.content
    msg.reaction = MessageReaction.NONE
    msg.save()