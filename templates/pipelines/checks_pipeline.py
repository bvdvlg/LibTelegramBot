def qr_code_processor(data, context):
    print("qr code threated")
    return True


def telephone_number_processor(data, context):
    if context.get('telephone_number'):
        return True


QrProcessorPipeline = [{"data_type": "photo", "processor": qr_code_processor, "previous_message": "Пришлите фото qr-кода из кассового чека", "after_message": "кассовый чек получен"},
                       {"data_type": "text", "processor": telephone_number_processor, "previous_message": "Введите номер телефона клиента!"}]