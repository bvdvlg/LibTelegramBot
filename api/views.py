from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from tgClient import Pipeline, UserSessionPipeline, UsersSesions

get_message = Pipeline.fromdict([{"data_type": "text", "processor": lambda x, context: print(x['text'])}])
chats = {}

# Create your views here.
@api_view(['GET', 'POST'])
def process_telegram_request(request):
    update = request.data
    chat_id = update['message']['chat']['id']
    UsersSesions.process_user_message(update['message'])
    return HttpResponse(status=200)
