import random
import string


def keygen(size=15, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def create_key(instance, size=15):
    new_keygen = keygen(size=size)
    EmailAppClass = instance.__class__
    qs_exists = EmailAppClass.objects.filter(secret=new_keygen).exists()

    if qs_exists:
        return create_key(size=size)

    return new_keygen
