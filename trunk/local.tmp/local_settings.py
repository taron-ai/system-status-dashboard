"""SSD Local Configuration File

   Required Configuration
    - Database username
    - Database password
      (note: database host/port can be ignored if its local and using the standard port)
    - Secret key
    - Full path to template directory

   Optional configuration
    - Everything else
   
"""

### Required ###

DATABASES = {
    'default': {
        'ENGINE'   : 'django.db.backends.mysql',
        'NAME'     : 'ssd',
        'USER'     : '$__db_user__$',    
        'PASSWORD' : '$__db_pass__$', 
        'HOST'     : '$__db_host__$', 
    }
}
SECRET_KEY = '$__secret_key__$'
TEMPLATE_DIRS = ( 
    '$__app_dir__$/templates'
)


### Optional ###

# The following are already set in the project settings.py configuration
# file but may be overridden here

#NAV = True
#REPORT_INCIDENT = True
#CONTACTS = True
#NOTIFY = True
#TIME_ZONE = ''
#LOGO = ''
#SSD_URL = ''
#MEDIA_ROOT = ''
#MAX_FILE_SIZE = ''
