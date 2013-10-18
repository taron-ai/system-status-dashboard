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


"""Context processor for SSD

   This context processor is responsible for setting the user desired
   display characteristics of the header (e.g. don't show the top nav)

"""

import pytz
from ssd.main.models import Config_Admin, Config_Logo, Config_Escalation, Config_Ireport
from django.conf import settings


def prefs(request):
    """Set the display characteristics"""

    # Hold the values we'll check in a dict
    values = {}

    # Application Version?
    # This one is in a settings file
    if hasattr(settings, 'APP_VERSION'):
        if not settings.APP_VERSION == False:
            values['app_version'] = settings.APP_VERSION
        else:
            values['app_version'] = False
    else:
        values['app_version'] = False

    # The rest of the configs are in the database
    
    # Display the logo?
    if Config_Logo.objects.filter(id=Config_Logo.objects.values('id')[0]['id']).values('logo_enabled')[0]['logo_enabled'] == 1:
        # Yes, display it, what's the url
        logo_url = Config_Logo.objects.filter(id=Config_Logo.objects.values('id')[0]['id']).values('url')[0]['url']
        values['logo'] = logo_url
    else:
        values['logo'] = False

    # Display the report incident link?
    if Config_Ireport.objects.filter(id=Config_Ireport.objects.values('id')[0]['id']).values('enabled')[0]['enabled'] == 1:
        values['ireport'] = True
    else:
        values['ireport'] = False

    # Display the escalation path?
    if Config_Escalation.objects.filter(id=Config_Escalation.objects.values('id')[0]['id']).values('enabled')[0]['enabled'] == 1:
        values['escalation'] = True
    else:
        values['escalation'] = False

    # Display the admin link?
    if Config_Admin.objects.filter(id=Config_Admin.objects.values('id')[0]['id']).values('link_enabled')[0]['link_enabled'] == 1:
        values['admin_link'] = True
    else:
        values['admin_link'] = False

    # Return values to the template
    return {
            'app_version':values['app_version'],
            'admin_link':values['admin_link'],
            'logo':values['logo'],
            'ireport':values['ireport'],
            'escalation':values['escalation']
           }


def redirect(request):
    """Set the 'next' Key so that after login events, the user can be 
    sent back to where they were"""

    # If the @login_required decorator is being used on a view,
    # then 'next' will already be set so do nothing
    # Since context_processors must return a dictionary, just give back
    # what is already in 'next'
    if request.GET.has_key('next'):
        return{'next':request.GET['next']}

    # If someone is accessing the login link directly, then set the next
    # key to the referring page so they can be redirected to the page they 
    # were on after login
    elif 'HTTP_REFERER' in request.META:

        # If the referring page is 'http://<quinico server>/accounts/login', then its probably
        # a failed login, so send them back to the homepage after login
        # since we don't know the true referrer
        if request.META['HTTP_REFERER'] == 'http://%s/accounts/login/' % request.META['HTTP_HOST']:
            return{'next':'/'}
        else:
            return{'next':request.META['HTTP_REFERER']}

    # Its not an @login_required view and there is no referrer, so send
    # them back to the home page after login
    else:
        return{'next':'/'}


def timezones(request):
    """Populate the timezones in the sticky footer timezone picker"""

    # Obtain all timezones (put this in a context processor)
    timezones = pytz.all_timezones

    return {'timezones': timezones }
