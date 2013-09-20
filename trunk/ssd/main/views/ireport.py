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

import os
import datetime
import logging
import pytz
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from ssd.main.models import Config_Ireport
from ssd.main.models import Config_Email
from ssd.main.forms import IreportConfigForm
from ssd.main.models import Ireport
from ssd.main.forms import ReportIncidentForm
from ssd.main.forms import IncidentReportListForm
from ssd.main.forms import DeleteEventForm
from ssd.main.forms import DetailForm
from ssd.main import notify
from ssd.main.views.system import system_message


# Get an instance of the ssd logger
logger = logging.getLogger(__name__)


def ireport(request):
    """Report View

    Accept a report from a user of an incident

    """

    # If this functionality is disabled in the admin, let the user know
    if Config_Ireport.objects.filter(id=Config_Ireport.objects.values('id')[0]['id']).values('enabled')[0]['enabled'] == 0:
        return system_message(request,True,'Your system administrator has disabled this functionality')

    # See if file uploads are anabled
    enable_uploads = Config_Ireport.objects.filter(id=Config_Ireport.objects.values('id')[0]['id']).values('upload_enabled')[0]['upload_enabled']

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
            if enable_uploads == 1:
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
                Ireport(date=report_time,
                        name=name,
                        email=email,
                        detail=detail,
                        extra=extra,
                        screenshot1=screenshot1,
                        screenshot2=screenshot2,
                       ).save()
            except Exception as e:
                return system_message(request,True,e)

            # If email is enabled and report notifications are turned on, send an email to the pager address
            if Config_Email.objects.filter(id=Config_Email.objects.values('id')[0]['id']).values('enabled')[0]['enabled'] == 1:
                if Config_Ireport.objects.filter(id=Config_Ireport.objects.values('id')[0]['id']).values('email_enabled')[0]['email_enabled'] == 1:
                    pager = notify.email()
                    pager.page(detail)

            # Give the user a thank you and let them know what to expect
            message = Config_Ireport.objects.filter(id=Config_Ireport.objects.values('id')[0]['id']).values('submit_message')[0]['submit_message']
            return system_message(request,False,message)


    # Ok, its a GET or an invalid form so create a blank form
    else:
        form = ReportIncidentForm()

    # Print the page
    return render_to_response(
       'ireport/ireport.html',
       {
          'title':'System Status Dashboard | Report Incident',
          'form':form,
          'enable_uploads':enable_uploads,
          'instructions':Config_Ireport.objects.filter(id=Config_Ireport.objects.values('id')[0]['id']).values('instructions')[0]['instructions']
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
            email_enabled = form.cleaned_data['email_enabled']
            instructions = form.cleaned_data['instructions']
            submit_message = form.cleaned_data['submit_message']
            upload_path = form.cleaned_data['upload_path']
            upload_enabled = form.cleaned_data['upload_enabled']
            file_size = form.cleaned_data['file_size']
        
            # There should only ever be one record in this table
            Config_Ireport.objects.filter(id=Config_Ireport.objects.values('id')[0]['id']).update(
                                                  enabled=enabled,
                                                  email_enabled=email_enabled,
                                                  instructions=instructions,
                                                  submit_message=submit_message,
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
    ireport_config = Config_Ireport.objects.filter(id=Config_Ireport.objects.values('id')[0]['id']).values('enabled','email_enabled','instructions','submit_message','upload_path','upload_enabled','file_size')

    # Print the page
    return render_to_response(
       'ireport/config.html',
       {
          'title':'System Status Dashboard | Incident Report Configuration',
          'ireport_config':ireport_config,
          'form':form,
          'email_enabled':Config_Email.objects.filter(id=Config_Email.objects.values('id')[0]['id']).values('enabled')[0]['enabled'],
          'breadcrumbs':{'Admin':'/admin','Incident Report Configuration':'ireport_config'},
          'nav_section':'ireport',
          'nav_sub':'ireport_config'
       },
       context_instance=RequestContext(request)
    )


@login_required
@staff_member_required
def ireport_list(request):
    """Incident Report List View

    Show all incident reports

    """

    form = IncidentReportListForm(request.GET)

    # Check the params
    if form.is_valid():

        page = form.cleaned_data['page']

        # Obtain all open incidents
        ireports_all = Ireport.objects.values('id','date','name','email','detail','extra','screenshot1','screenshot2').order_by('-id')

        # Create a paginator and paginate the list w/ 10 messages per page
        paginator = Paginator(ireports_all, 10)

        # Paginate them
        try:
            ireports = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, or is not given deliver first page.
            ireports = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            ireports = paginator.page(paginator.num_pages)

        # Print the page
        return render_to_response(
           'ireport/ireport_list.html',
           {
              'title':'System Status Dashboard | Incident Report List',
              'ireports':ireports,
              'breadcrumbs':{'Admin':'/admin','List Open Incident Reports':'ireport_list'},
              'nav_section':'ireport',
              'nav_sub':'ireport_list'
           },
           context_instance=RequestContext(request)
        )

    # Invalid form
    else:
        messages.add_message(request, messages.ERROR, 'Invalid request, please submit your request again.')
        return HttpResponseRedirect('/admin/ireport_list')


@login_required
@staff_member_required
def ireport_delete(request):
    """Delete Incident Report Page

    Delete an incident report given an id

    """

    # If it's a POST, then we are going to delete it after confirmation
    if request.method == 'POST':
        
        # Check the form elements
        form = DeleteEventForm(request.POST)

        if form.is_valid():

            # Obtain the cleaned data
            id = form.cleaned_data['id']

            # First, delete any screenshots
            # Obtain the local uploads location
            upload_path = Config_Ireport.objects.filter(id=Config_Ireport.objects.values('id')[0]['id']).values('upload_path')[0]['upload_path']
            # Get any screenshots
            screenshots = Ireport.objects.filter(id=id).values('screenshot1','screenshot2')
            for screenshot in screenshots:
                for name,file_path in screenshot.items():
                    if file_path:
                        # Remove the file
                        try:
                            os.remove('%s/%s' % (upload_path,file_path))
                        except OSError:
                            pass


            # Delete the incident
            Ireport.objects.filter(id=id).delete()

            # Set a message that the delete was successful
            messages.add_message(request, messages.SUCCESS, 'Incident report id:%s successfully deleted' % id)

            # Redirect to the incident reports page
            return HttpResponseRedirect('/admin/ireport_list')

        # Invalid form submit
        else:
            # Set a message that the delete was not successful
            messages.add_message(request, messages.ERROR, 'Incident report id:%s not deleted' % id)
            
            # Redirect to the incident reports page
            return HttpResponseRedirect('/admin/ireport_list')

    # If we get this far, it's a GET and we're looking for confirmation of the delete
   
    # Make sure we have an ID
    form = DeleteEventForm(request.GET)
    if form.is_valid():

        # Obtain the cleaned data
        id = form.cleaned_data['id']

        # Print the page (confirm they want to delete the incident)
        return render_to_response(
           'ireport/ireport_delete.html',
           {
              'title':'System Status Dashboard | Confirm Incident Report Delete',
              'id':id,
              'breadcrumbs':{'Admin':'/admin','List Open Incident Reports':'ireport_list'},
              'nav_section':'ireport',
              'nav_sub':'ireport_delete'
           },
           context_instance=RequestContext(request)
        )

        # Redirect to the incident reports page
        return HttpResponseRedirect('/admin/ireport_list')

    # Invalid request
    else:
        # Redirect to the incident reports page
        return HttpResponseRedirect('/admin/ireport_list')


def ireport_detail(request):
    """Incident Report Detail View

    Show all available information on an incident report

    """

    form = DetailForm(request.GET)

    if form.is_valid():
        # Obtain the cleaned data
        id = form.cleaned_data['id']

    # Bad form
    else:
        # Redirect to the admin reports page
        return HttpResponseRedirect('/admin')

    # Obain the incident report detail
    detail = Ireport.objects.filter(id=id).values(
                                                'id',
                                                'date',
                                                'name',
                                                'email',
                                                'detail',
                                                'extra',
                                                'screenshot1',
                                                'screenshot2'
                                                )

    # Print the page
    return render_to_response(
       'ireport/ireport_detail.html',
       {
          'title':'System Status Dashboard | Incident Report Detail',
          'detail':detail,
          'breadcrumbs':{'Admin':'/admin','Incident Report Detail':'ireport_list'},
          'nav_section':'ireport',
          'nav_sub':'ireport_detail'
       },
       context_instance=RequestContext(request)
    )
