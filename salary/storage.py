from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):

        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
            print(os.path.join(settings.MEDIA_ROOT, name))
        return name
    
def change_name(instance, filename):
    print(instance, filename)