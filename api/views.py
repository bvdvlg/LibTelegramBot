from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from tgClient import Pipeline, UserSessionPipeline, UsersSesions
from templates.pipelines.checks_pipeline import QrProcessorPipeline

get_message = Pipeline.fromdict([{"data_type": "text", "processor": lambda x, context: print(x['text'])}])
chats = {}


hello = {'update_id': 712480614, 'message': {'message_id': 105, 'from': {'id': 426702546, 'is_bot': False, 'first_name': 'Владимир', 'username': 'bvdvlg', 'language_code': 'ru'}, 'chat': {'id': 426702546, 'first_name': 'Владимир', 'username': 'bvdvlg', 'type': 'private'}, 'date': 1649061165, 'text': '/hello'}}
photo = {'update_id': 712480614, 'message': {'message_id': 105, 'from': {'id': 426702546, 'is_bot': False, 'first_name': 'Владимир', 'username': 'bvdvlg', 'language_code': 'ru'}, 'chat': {'id': 426702546, 'first_name': 'Владимир', 'username': 'bvdvlg', 'type': 'private'}, 'date': 1649061165, "photo": "photo"}}
stop = {'update_id': 712480614, 'message': {'message_id': 105, 'from': {'id': 426702546, 'is_bot': False, 'first_name': 'Владимир', 'username': 'bvdvlg', 'language_code': 'ru'}, 'chat': {'id': 426702546, 'first_name': 'Владимир', 'username': 'bvdvlg', 'type': 'private'}, 'date': 1649061165, 'text': '/stop'}}
Pipeline.register_operation("/hello", QrProcessorPipeline)
# Create your views here.


@api_view(['GET', 'POST'])
def process_telegram_request(request):
    update = request.data
    chat_id = update['message']['chat']['id']
    UsersSesions.process_user_message(update['message'])
    return HttpResponse(status=200)
