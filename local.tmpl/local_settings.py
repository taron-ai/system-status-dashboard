#
# Copyright 2013 - Tom Alessi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""SSD Local Configuration File

   Required Configuration
    - Database username
    - Database password
      (note: database host/port can be ignored if its local and using the standard port)
    - Secret key
    - Full path to template directory
   
"""


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

# Set the timezone to match the server's timezone
TIME_ZONE = 'US/Pacific'



