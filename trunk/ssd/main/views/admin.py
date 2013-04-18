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


"""This module contains all of the administrative functions
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
            params['recipient_name'] = form.cleaned_data['recipient_name']
            
            params['greeting_incident_new'] = form.cleaned_data['greeting_incident_new']
            params['greeting_incident_update'] = form.cleaned_data['greeting_incident_update']
            params['greeting_maintenance_new'] = form.cleaned_data['greeting_maintenance_new']
            params['greeting_maintenance_update'] = form.cleaned_data['greeting_maintenance_update']
            params['email_from'] = form.cleaned_data['email_from']
            params['email_subject_incident'] = form.cleaned_data['email_subject_incident']
            params['email_subject_maintenance'] = form.cleaned_data['email_subject_maintenance']
            params['alert'] = form.cleaned_data['alert']
            params['display_alert'] = form.cleaned_data['display_alert']
            params['recipient_incident'] = form.cleaned_data['recipient_incident']
            params['recipient_maintenance'] = form.cleaned_data['recipient_maintenance']
            params['recipient_pager'] = form.cleaned_data['recipient_pager']
            params['message_success'] = form.cleaned_data['message_success']
            params['message_error'] = form.cleaned_data['message_error']
            params['escalation'] = form.cleaned_data['escalation']
            params['logo_display'] = form.cleaned_data['logo_display']
            params['logo_url'] = form.cleaned_data['logo_url']
            params['ssd_url'] = form.cleaned_data['ssd_url']
            params['nav_display'] = form.cleaned_data['nav_display']
            params['contacts_display'] = form.cleaned_data['contacts_display']
            params['report_incident_display'] = form.cleaned_data['report_incident_display']
            params['instr_sched_maint'] = form.cleaned_data['instr_sched_maint']
            params['display_sched_maint_instr'] = form.cleaned_data['display_sched_maint_instr']
            params['instr_report_incident'] = form.cleaned_data['instr_report_incident']
            params['display_report_incident_instr'] = form.cleaned_data['display_report_incident_instr']
            params['instr_create_incident'] = form.cleaned_data['instr_create_incident']
            params['display_create_incident_instr'] = form.cleaned_data['display_create_incident_instr']
            params['enable_uploads'] = form.cleaned_data['enable_uploads']
            params['upload_path'] = form.cleaned_data['upload_path']
            params['file_upload_size'] = form.cleaned_data['file_upload_size']
            params['instr_create_description'] = form.cleaned_data['instr_create_description']
            

            # Update the data
            for param in params:
                if 'update_%s' % param in request.POST:
                    Config.objects.filter(config_name=param).update(config_value=params[param])

            # Redirect back
            return HttpResponseRedirect('/admin/config')

    # Not a POST so create a blank form and return all the existing configs
    else:
        form = ConfigForm()

    # Obtain all of the config values
    configs = Config.objects.values('config_name',
                                    'friendly_name',
                                    'config_value',
                                    'description',
                                    'category',
                                    'display').order_by('category','config_name')

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