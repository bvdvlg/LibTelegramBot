KEY_STORE_DIR = "key_storage"


def obtain_key(name):
    with open("{}/{}.secret".format(KEY_STORE_DIR, name)) as f:
        key = f.read()
    return key
