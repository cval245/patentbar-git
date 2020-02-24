from patentbar.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'patentbar',
        'USER': 'djangoconnect',
        #'HOST': '172.17.0.1',
        'HOST': '192.168.0.14',
        #'HOST': 'localhost',
        'PASSWORD': 'Belgrade2010',
        'PORT': '5432',
    }

}
