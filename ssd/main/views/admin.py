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


"""This module contains all of the special administrative functions
   of ssd

"""


from django.contrib.auth import authenticate
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from ssd.main.models import Config
from ssd.main.forms import ConfigForm


@staff_member_required
def config(request):
    """Configuration Parameters

    """

    if request.method == 'POST':

        # Check the form elements
        # We'll only update values if the user indicates they want it by checking the box
        form = ConfigForm(request.POST)

        if form.is_valid():

            # Obtain the cleaned data and put into a lookup table
            params = {}
            params['company'] = form.cleaned_data['company']
            params['greeting_new'] = form.cleaned_data['greeting_new']
            params['greeting_update'] = form.cleaned_data['greeting_update']
            params['email_to'] = form.cleaned_data['email_to']
            params['email_from'] = form.cleaned_data['email_from']
            params['email_subject'] = form.cleaned_data['email_subject']
            params['maintenance'] = form.cleaned_data['maintenance']
            params['page_to'] = form.cleaned_data['page_to']
            params['message_success'] = form.cleaned_data['message_success']
            params['message_error'] = form.cleaned_data['message_error']
            params['escalation'] = form.cleaned_data['escalation']
            params['report_incident_help'] = form.cleaned_data['report_incident_help']
            params['create_incident_help'] = form.cleaned_data['create_incident_help']
            params['logo_display'] = form.cleaned_data['logo_display']
            params['logo_url'] = form.cleaned_data['logo_url']
            params['nav_display'] = form.cleaned_data['nav_display']
            params['contacts_display'] = form.cleaned_data['contacts_display']
            params['report_incident_display'] = form.cleaned_data['report_incident_display']

            # Update the data
            for param in params:
                if 'update_%s' % param in request.POST:
                    Config.objects.filter(config_name=param).update(config_value=params[param])

            # Redirect back
            return HttpResponseRedirect('/admin/config')

    # Not a POST so create a blank form and return all the existing configs
    else:
        form = ConfigForm()

    configs = Config.objects.values('config_name',
                                    'friendly_name',
                                    'config_value',
                                    'description',
                                    'display').order_by('friendly_name')

    # Print the page
    return render_to_response(
       'main/config.html',
       {
          'title':'System Status Dashboard | Configuration Manager',
          'form':form,
          'configs':configs
       },
       context_instance=RequestContext(request)
    )