def qr_code_processor(data, context):
    print("qr code threated")
    return True


def telephone_number_processor(data, context):
    print("Telephone number therated")
    return False


QrProcessorPipeline = [{"data_type": "photo", "processor": qr_code_processor, "previous_message": "Пришлите фото qr-кода из кассового чека", "after_message": "Кассовый чек получен"},
                       {"data_type": "text", "processor": telephone_number_processor, "previous_message": "Введите номер телефона клиента!", "after_message": "Номер телефона обработан"}]
