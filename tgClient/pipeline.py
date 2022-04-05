from tgClient import TelegramClient
import logging


class PipelineElement:
    TELEGRAM_CLIENT = None

    @classmethod
    def __init_telegram_client(cls):
        cls.TELEGRAM_CLIENT = TelegramClient()

    @classmethod
    def fromdict(cls, dct):
        return cls(**dct)

    def __init__(self, data_type, processor, validator=None, sys_error_message=None, usr_error_message=None, previous_message=None):
        self.data_type = data_type
        self.validator = validator or (lambda data: True)
        self.sys_error_message = sys_error_message or "Validation is failed {}".format(self.validator)
        self.usr_error_message = usr_error_message or "Отправленные данные не могут пройти валидацию"
        self.processor = processor
        self.pre_message = previous_message
        if not self.TELEGRAM_CLIENT:
            self.__init_telegram_client()

    def send_error_message(self, system_error, user_error, context):
        logging.error(system_error)
        self.TELEGRAM_CLIENT.sendMessage(chat_id=(None, context['chat_id']), text=(None, user_error))

    def send_pre_message(self, context):
        if self.pre_message is not None:
            self.TELEGRAM_CLIENT.sendMessage(chat_id=(None, context['chat_id']), text=(None, self.pre_message))

    def validate(self, data):
        if not data.get(self.data_type, False):
            return {"is_valid": False, "sys_error": "Message data type doesn't matches with {}".format(self.data_type), "usr_error": "Получен неверный тип данных, пожалуйста, проверьте корректность отправленных данных"}
        if self.validator(data):
            return {"is_valid": True, "sys_error": None, "usr_error": None}
        else:
            return {"is_valid": False, "sys_error": self.sys_error_message, "usr_error": self.usr_error_message}


def e(x, context):
    print("Текст получен")
    return True


def ep(x, context):
    print("Фото получено")
    return True


def default_processor(data, context):
    if data['text'] == "/hello":
        UsersSesions.user_sessions[data['chat']['id']] = UserSessionPipeline(Pipeline.fromdict([{"data_type": "text", "processor": lambda x, context: e, "previous_message": "Введите текстовые данные!"},
                                                                                                {"data_type": "photo", "processor": lambda x, context: ep, "previous_message": "Скиньте фото!"}]), context['chat_id'])
        UsersSesions.user_sessions[data['chat']['id']].start()
        return True
    else:
        return False


class Pipeline:

    @classmethod
    def fromdict(cls, pipeline):
        return cls(pipeline=[PipelineElement.fromdict(el) for el in pipeline])

    @classmethod
    def default(cls):
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
        if validation['is_valid'] and next_el.processor(data, self.context):
            self.index += 1
            if not self.is_finished:
                self.pipeline[self.index].send_pre_message(self.context)
        else:
            if not validation['is_valid']:
                self.pipeline[self.index].send_error_message(validation['sys_error'], validation['usr_error'], self.context)


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

        user_pipeline = cls.user_sessions[chat_id]
        user_pipeline.execute(message)
        if user_pipeline.is_finished:
            del user_pipeline
