
from uuid import uuid4
import os 


def image_path(path): 
    def wrapper(instance, filename): 
        ext = filename.split('.')[-1]

        if instance.pk: 
            filename = f'{instance.pk}{ext}'
        else: 
            filename = f'{uuid4().hex, ext}'
        return os.path.join(path, filename)
    return wrapper


def photo_path(instance, filename): 

    return f'{instance.id}{image_path(filename)}'
