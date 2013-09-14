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


"""This module contains all of the incident report functions of ssd"""

import datetime
import pytz
from django.utils import timezone as jtz
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib import messages
from ssd.main.models import Config_Ireport
from ssd.main.forms import IreportConfigForm
from ssd.main.models import Report
from ssd.main.models import Service
from ssd.main.models import Email
from ssd.main.forms import ReportIncidentForm
from ssd.main import notify
from ssd.main import config_value
from ssd.main.views.system import system_message


def ireport(request):
    """Report View

    Accept a report from a user of an incident

    """

    # Instantiate the configuration value getter
    cv = config_value.config_value()

    # If this functionality is disabled in the admin, let the user know
    if int(cv.value('report_incident_display')) == 0:
        return system_message(request,True,'Your system administrator has disabled this functionality')

    # If this is a POST, then check the input params and perform the
    # action, otherwise print the index page
    if request.method == 'POST':
        # Check the form elements
        form = ReportIncidentForm(request.POST, request.FILES)

        if form.is_valid():
            # Obtain the cleaned data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            detail = form.cleaned_data['detail']
            extra = form.cleaned_data['extra']

            # Create a datetime object for right now
            report_time = datetime.datetime.now()

            # Add the server's timezone (whatever DJango is set to)
            report_time = pytz.timezone(settings.TIME_ZONE).localize(report_time)

            # Save the data
            # If file uploads are disabled but the user included them somehow, ignore them
            if int(cv.value('enable_uploads')) == 1:
                if 'screenshot1' in request.FILES:
                    screenshot1 = request.FILES['screenshot1']
                else:
                    screenshot1 = ''

                if 'screenshot2' in request.FILES:
                    screenshot2 = request.FILES['screenshot2']
                else:
                    screenshot2 = ''

            # Screenshots are disabled
            else:
                screenshot1 = ''
                screenshot2 = ''
            
            # Save the data (if the admin has not setup the upload directory, it'll fail)
            try:
                Report(date=report_time,
                       name=name,
                       email=email,
                       detail=detail,
                       extra=extra,
                       screenshot1=screenshot1,
                       screenshot2=screenshot2,
                      ).save()
            except Exception as e:
                return system_message(request,True,e)

            # If notifications are turned on, report the issue to the pager address
            # and save the return value for the confirmation page
            # If notifications are turned off, give the user a positive confirmation
            
            if int(cv.value('notify')) == 1:
                pager = notify.email()
                pager_status = pager.page(detail)
            else:
                pager_status = 'success'

            if pager_status == 'success':
                message = cv.value('message_success')
                return system_message(request,False,message)
            else:
                message = cv.value('message_error')
                message = '%s: %s' % (message,pager_status)
                return system_message(request,True,message)

    # Ok, its a GET or an invalid form so create a blank form
    else:
        form = ReportIncidentForm()

    # Print the page
    # On a POST, the form will give back error values for printing in the template

    # Help message
    help = cv.value('help_report_incident')

    # Obtain the default maintenance textfield text
    instr_report_name = cv.value('instr_report_name')
    instr_report_email = cv.value('instr_report_email')
    instr_report_detail= cv.value('instr_report_detail')
    instr_report_extra= cv.value('instr_report_extra')
    
    return render_to_response(
       'ireport/ireport.html',
       {
          'title':'System Status Dashboard | Report Incident',
          'form':form,
          'help':help,
          'instr_report_name':instr_report_name,
          'instr_report_email':instr_report_email,
          'instr_report_detail':instr_report_detail,
          'instr_report_extra':instr_report_extra,
          'enable_uploads':int(cv.value('enable_uploads'))
       },
       context_instance=RequestContext(request)
    )


@login_required
@staff_member_required
def ireport_config(request):
    """Main system url view
 
    """

    # If this is a POST, then validate the form and save the data
    if request.method == 'POST':

        # Check the form elements
        form = IreportConfigForm(request.POST)

        if form.is_valid():
            # Obtain the cleaned data
            enabled = form.cleaned_data['enabled']
            upload_path = form.cleaned_data['upload_path']
            upload_enabled = form.cleaned_data['upload_enabled']
            file_size = form.cleaned_data['file_size']
        
            # There should only ever be one record in this table
            Config_Ireport.objects.filter(id=Config_Ireport.objects.values('id')[0]['id']).update(
                                                  enabled=enabled,
                                                  upload_path=upload_path,
                                                  upload_enabled=upload_enabled,
                                                  file_size=file_size
                                                  )

            messages.add_message(request, messages.SUCCESS, 'Preferences saved successfully')
        else:
            messages.add_message(request, messages.ERROR, 'Invalid data entered, please correct the errors below:')

    # Not a POST or a failed form submit
    else:
        # Create a blank form
        form = IreportConfigForm

    # Obtain the email config

    ireport_config = Config_Ireport.objects.filter(id=Config_Ireport.objects.values('id')[0]['id']).values('enabled','upload_path','upload_enabled','file_size')

    # Print the page
    return render_to_response(
       'ireport/config.html',
       {
          'title':'System Status Dashboard | Incident Report Configuration',
          'ireport_config':ireport_config,
          'form':form,
          'breadcrumbs':{'Admin':'/admin','Incident Report Configuration':'ireport_config'},
          'nav_section':'ireport',
          'nav_sub':'ireport_config'
       },
       context_instance=RequestContext(request)
    )