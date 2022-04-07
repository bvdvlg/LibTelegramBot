from tgClient import TelegramClient
import logging
from templates.pipelines.checks_pipeline import QrProcessorPipeline


class PipelineElement:
    TELEGRAM_CLIENT = None

    @classmethod
    def __init_telegram_client(cls):
        cls.TELEGRAM_CLIENT = TelegramClient()

    @classmethod
    def fromdict(cls, dct):
        return cls(**dct)

    def __init__(self, data_type, processor, validator=None, error=None, previous_message=None, after_message=None):
        self.data_type = data_type
        self.validator = validator or (lambda data: True)
        self.usr_error_message = error or "Отправленные данные не могут пройти валидацию"
        self.after_message = after_message
        self.processor = processor
        self.pre_message = previous_message
        if not self.TELEGRAM_CLIENT:
            self.__init_telegram_client()

    def send_after_message(self, context):
        if self.after_message:
            self.TELEGRAM_CLIENT.sendMessage(chat_id=(None, context['chat_id']), text=(None, self.after_message))

    def send_error_message(self, error, context):
        self.TELEGRAM_CLIENT.sendMessage(chat_id=(None, context['chat_id']), text=(None, error))

    def send_pre_message(self, context):
        if self.pre_message is not None:
            self.TELEGRAM_CLIENT.sendMessage(chat_id=(None, context['chat_id']), text=(None, self.pre_message))

    def run(self, data, context):
        return self.processor(data, context)

    def validate(self, data):
        if not data.get(self.data_type, False):
            return {"is_valid": False, "error": "Получен неверный тип данных, пожалуйста, проверьте корректность отправленных данных"}
        if self.validator(data):
            return {"is_valid": True, "error": None}
        else:
            return {"is_valid": False, "error": self.usr_error_message}


class Pipeline:
    __DEFAULT = {}

    @classmethod
    def register_operation(cls, command, pipeline_dict):
        cls.__DEFAULT[command] = pipeline_dict

    @classmethod
    def fromdict(cls, pipeline):
        return cls(pipeline=[PipelineElement.fromdict(el) for el in pipeline])

    @classmethod
    def default(cls):
        def default_processor(data, context):
            if cls.__DEFAULT.get(data['text']):
                UsersSesions.user_sessions[data['chat']['id']] = UserSessionPipeline(
                    Pipeline.fromdict(cls.__DEFAULT.get(data['text'])), context['chat_id'])
                UsersSesions.user_sessions[data['chat']['id']].start()
                return True
            else:
                context["error"] = "Команда не распознана"
                return False
        return cls.fromdict([{"data_type": "text", "processor": default_processor}])

    def __init__(self, pipeline=None):
        if not pipeline:
            self.pipeline = []
        else:
            self.pipeline = pipeline
        self.__len = len(self.pipeline)

    def __len__(self):
        return self.__len

    def __getitem__(self, item):
        return self.pipeline[item]


class UserSessionPipeline:
    def __init__(self, pipeline, chat_id):
        self.pipeline = pipeline
        self.context = {"chat_id": chat_id}
        self.index = -1
        self.finished = False

    @property
    def is_finished(self):
        return self.index >= len(self.pipeline)

    def start(self):
        self.index = 0
        self.pipeline[self.index].send_pre_message(self.context)

    def execute(self, data):
        next_el = self.pipeline[self.index]

        validation = next_el.validate(data)
        is_success = False if not validation['is_valid'] else next_el.run(data, self.context)
        if validation['is_valid'] and is_success:
            next_el.send_after_message(self.context)
            self.index += 1
            if not self.is_finished:
                self.pipeline[self.index].send_pre_message(self.context)
        elif not validation['is_valid']:
            self.pipeline[self.index].send_error_message(validation['error'], self.context)
        elif not is_success and self.context.get("error"):
            self.pipeline[self.index].send_error_message(self.context.get("error"), self.context)


class UsersSesions:
    user_sessions = {}

    @classmethod
    def process_user_message(cls, message):
        chat_id = message['chat']['id']

        if message.get('text') == "/stop":
            if cls.user_sessions.get(chat_id):
                del cls.user_sessions[chat_id]

        if not cls.user_sessions.get(chat_id):
            cls.user_sessions[chat_id] = UserSessionPipeline(Pipeline.default(), chat_id)
            cls.user_sessions[chat_id].start()

        cls.user_sessions[chat_id].execute(message)

        if cls.user_sessions[chat_id].is_finished:
            del cls.user_sessions[chat_id]
