DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'conflicto',
        'HOST': 'localhost',
        'PORT': '5432',
        'USERNAME': 'deploy',
        'PASSWORD': 'deploy'
    }
}

DEBUG = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/apps/ConflictoServer/logs/application.log',
            'maxBytes': 1024*1024*50, # 50 MB
            'backupCount': 5,
            'formatter': 'verbose'
        },
        'cronfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/apps/ConflictoServer/logs/crons.log',
            'maxBytes': 1024 * 1024 * 50,  # 50 MB
            'backupCount': 5,
            'formatter': 'verbose'

        }

    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'conflicto':{
            'handlers':['file'],
            'propogate': True,
            'level': 'INFO'
        },
        'cron':{
            'handlers':['cronfile'],
            'propogate': True,
            'level': 'INFO'
        }
    },
}
