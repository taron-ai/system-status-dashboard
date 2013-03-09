#
# Copyright 2012 - Tom Alessi
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
   

from django.conf import settings


def prefs(request):
    """Set the display characteristics"""

    # Hold the values we'll check in a dict
    values = {}

    # Application Version?
    if hasattr(settings, 'APP_VERSION'):
        if not settings.APP_VERSION == False:
            values['app_version'] = settings.APP_VERSION
        else:
            values['app_version'] = False
    else:
        values['app_version'] = False

    # Display the logo?
    if hasattr(settings, 'LOGO'):
        if not settings.LOGO == False:
            values['logo'] = settings.LOGO
        else:
            values['logo'] = False
    else:
        values['logo'] = False

    # Display the nav?
    if hasattr(settings, 'NAV'):
        if settings.NAV == True:
            values['nav'] = True
        else:
            values['nav'] = False
    else:
        values['nav'] = False

    # Display the contacts?
    if hasattr(settings, 'CONTACTS'):
        if settings.CONTACTS == True:
            values['contacts'] = True
        else:
            values['contacts'] = False
    else:
        values['contacts'] = False

    # Display the report incident?
    if hasattr(settings, 'REPORT_INCIDENT'):
        if settings.REPORT_INCIDENT == True:
            values['report_incident'] = True
        else:
            values['report_incident'] = False
    else:
        values['report_incident'] = False

    # Return values to the template
    return {
            'app_version':values['app_version'],
            'logo':values['logo'],
            'nav':values['nav'],
            'contacts':values['contacts'],
            'report_incident':values['report_incident'],
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
