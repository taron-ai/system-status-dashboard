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
        'USER'     : '<<ENTER DATABASE USER NAME>>',       
        'PASSWORD' : '<<ENTER DATABASE USER PASSWORD>>', 
        'HOST'     : '', # Leave blank if the database is on the local host
        'PORT'     : '', # Leave blank if the default mysql port is being used        
    }
}
SECRET_KEY = '<<ENTER SECRET KEY>>'
TEMPLATE_DIRS = (
    '<<ENTER FULL PATH>>/templates'
)



### Optional ###

# The following are already set in the project settings.py configuration
# file but may be overridden here

#NAV = True
#REPORT_INCIDENT = True
#CONTACTS = True
#NOTIFY = True
#TIME_ZONE = 'America/Chicago'
#LOGO = ''
