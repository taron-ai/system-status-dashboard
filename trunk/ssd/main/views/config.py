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


"""This module contains all of the configuration functions of ssd"""

from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from ssd.main.models import Config
from ssd.main.models import Email
from ssd.main.forms import ConfigForm
from ssd.main.models import Event
from ssd.main.models import Service
from ssd.main.models import Escalation
from ssd.main.forms import AddEmailForm
from ssd.main.forms import RemoveEmailForm
from ssd.main.forms import AddServiceForm
from ssd.main.forms import RemoveServiceForm
from ssd.main.forms import AddContactForm
from ssd.main.forms import ModifyContactForm
from ssd.main import config_value
from ssd.main.views.system import system_message


@login_required
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
            params['recipient_name'] = form.cleaned_data['recipient_name']
            params['greeting_incident_new'] = form.cleaned_data['greeting_incident_new']
            params['greeting_incident_update'] = form.cleaned_data['greeting_incident_update']
            params['email_format_maintenance'] = form.cleaned_data['email_format_maintenance']
            params['email_format_incident'] = form.cleaned_data['email_format_incident']
            params['email_from'] = form.cleaned_data['email_from']
            params['email_subject_incident'] = form.cleaned_data['email_subject_incident']
            params['email_subject_maintenance'] = form.cleaned_data['email_subject_maintenance']
            params['greeting_maintenance_new'] = form.cleaned_data['greeting_maintenance_new']
            params['greeting_maintenance_update'] = form.cleaned_data['greeting_maintenance_update']
            params['recipient_pager'] = form.cleaned_data['recipient_pager']            
            params['message_success'] = form.cleaned_data['message_success']
            params['message_error'] = form.cleaned_data['message_error']
            params['notify'] = form.cleaned_data['notify']
            params['instr_incident_description'] = form.cleaned_data['instr_incident_description']
            params['instr_incident_update'] = form.cleaned_data['instr_incident_update']
            params['instr_maintenance_impact'] = form.cleaned_data['instr_maintenance_impact']
            params['instr_maintenance_coordinator'] = form.cleaned_data['instr_maintenance_coordinator']
            params['instr_maintenance_update'] = form.cleaned_data['instr_maintenance_update']
            params['instr_maintenance_description'] = form.cleaned_data['instr_maintenance_description']            
            params['instr_report_name'] = form.cleaned_data['instr_report_name']
            params['instr_report_email'] = form.cleaned_data['instr_report_email']
            params['instr_report_detail'] = form.cleaned_data['instr_report_detail']
            params['instr_report_extra'] = form.cleaned_data['instr_report_extra']
            params['instr_escalation_name'] = form.cleaned_data['instr_escalation_name']
            params['instr_escalation_details'] = form.cleaned_data['instr_escalation_details']
            params['logo_display'] = form.cleaned_data['logo_display']
            params['logo_url'] = form.cleaned_data['logo_url']
            params['nav_display'] = form.cleaned_data['nav_display']
            params['escalation_display'] = form.cleaned_data['escalation_display']
            params['report_incident_display'] = form.cleaned_data['report_incident_display']
            params['login_display'] = form.cleaned_data['login_display']
            params['display_alert'] = form.cleaned_data['display_alert']
            params['alert'] = form.cleaned_data['alert']
            params['help_sched_maint'] = form.cleaned_data['help_sched_maint']
            params['help_report_incident'] = form.cleaned_data['help_report_incident']
            params['help_create_incident'] = form.cleaned_data['help_create_incident']
            params['help_escalation'] = form.cleaned_data['help_escalation']
            params['enable_uploads'] = form.cleaned_data['enable_uploads']
            params['upload_path'] = form.cleaned_data['upload_path']
            params['file_upload_size'] = form.cleaned_data['file_upload_size']
            params['ssd_url'] = form.cleaned_data['ssd_url']
            params['escalation'] = form.cleaned_data['escalation']
            params['information_main'] = form.cleaned_data['information_main']
 
            filter = form.cleaned_data['filter'] 
                      
            # Update the data
            for param in params:
                if 'update_%s' % param in request.POST:
                    Config.objects.filter(config_name=param).update(config_value=params[param])

            # Redirect back
            return HttpResponseRedirect('/config?filter=%s' % filter)

    # Not a POST so create a blank form and return all the existing configs
    else:
        form = ConfigForm()

    # See if we are filtering results
    # On failed POSTS, we also need this
    if 'filter' in request.POST:
        filter = request.POST['filter'] 
    elif 'filter' in request.GET:
        filter = request.GET['filter'] 
    else:
        filter = 'all'  
    
    # Obtain all of the config values
    if filter == 'all':
        configs = Config.objects.values('config_name',
                                        'friendly_name',
                                        'config_value',
                                        'description',
                                        'display')
    else:
        configs = Config.objects.filter(category=filter).values('config_name',
                                                                'friendly_name',
                                                                'config_value',
                                                                'description',
                                                                'display')

    # Print the page
    return render_to_response(
       'config/config.html',
       {
          'title':'System Status Dashboard | Configuration Manager',
          'form':form,
          'configs':configs,
          'filter':filter
       },
       context_instance=RequestContext(request)
    )






