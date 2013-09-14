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


"""This module contains all of the email configuration functions of ssd"""

from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib import messages
from ssd.main.models import Email
from ssd.main.forms import AddEmailForm
from ssd.main.forms import RemoveEmailForm
from ssd.main.forms import EmailConfigForm
from ssd.main.models import Config_Email
from ssd.main.models import Event
from ssd.main.views.system import system_message


@login_required
@staff_member_required
def email_config(request):
    """Main admin index view
 
    """

    # If this is a POST, then validate the form and save the data
    if request.method == 'POST':

        # Check the form elements
        form = EmailConfigForm(request.POST)

        if form.is_valid():
            # Obtain the cleaned data
            email_format = form.cleaned_data['email_format']
            from_address = form.cleaned_data['from_address']
            text_pager = form.cleaned_data['text_pager']
            incident_greeting = form.cleaned_data['incident_greeting']
            incident_update = form.cleaned_data['incident_update']
            maintenance_greeting = form.cleaned_data['maintenance_greeting']
            maintenance_update = form.cleaned_data['maintenance_update']
        

            # There should only ever be one record in this table
            Config_Email.objects.filter(id=Config_Email.objects.values('id')[0]['id']).update(
                                                        email_format=email_format,
                                                        from_address=from_address,
                                                        text_pager=text_pager,
                                                        incident_greeting=incident_greeting,
                                                        incident_update=incident_update,
                                                        maintenance_greeting=maintenance_greeting,
                                                        maintenance_update=maintenance_update
                                                    )

            messages.add_message(request, messages.SUCCESS, 'Recipient saved successfully')
        else:
            messages.add_message(request, messages.ERROR, 'Invalid data entered, please correct the errors below:')



    # Not a POST or a failed form submit
    else:
        # Create a blank form
        form = EmailConfigForm

    # Obtain the email config

    email_config = Config_Email.objects.filter(id=Config_Email.objects.values('id')[0]['id']).values(
                                                                                    'email_format',
                                                                                    'from_address',
                                                                                    'text_pager',
                                                                                    'incident_greeting',
                                                                                    'incident_update',
                                                                                    'maintenance_greeting',
                                                                                    'maintenance_update',
                                                                                    )

    # Print the page
    return render_to_response(
       'email/config.html',
       {
          'title':'System Status Dashboard | Admin',
          'email_config':email_config,
          'form':form,
          'breadcrumbs':{'Admin':'/admin','Email Configuration':'email_config'},
          'nav_section':'email',
          'nav_sub':'email_config'
       },
       context_instance=RequestContext(request)
    )


@login_required
@staff_member_required
def email_recipients(request):
    """Manage Recipient Email Addresses
 
    """

    # If this is a POST, then validate the form and save the data
    if request.method == 'POST':
       
        # Check the form elements
        form = AddEmailForm(request.POST)

        if form.is_valid():
            
            email = form.cleaned_data['email']

            # Don't allow duplicates
            try:
                Email(email=email).save()
            except IntegrityError:
                pass
            
            messages.add_message(request, messages.SUCCESS, 'Preferences saved successfully')
            
            # Send them back so they can see the newly created email addresses
            return HttpResponseRedirect('/admin/email_recipients')
        else:
            messages.add_message(request, messages.ERROR, 'Invalid data entered, please correct the errors below:')

    # Not a POST
    else:
        # Create a blank form
        form = AddEmailForm()
    
    # Obtain all current email addresses
    emails = Email.objects.all()
    
    # Print the page
    return render_to_response(
       'email/recipients.html',
       {
          'title':'System Status Dashboard | Manage Email Recipients',
          'form':form,
          'emails':emails,
          'breadcrumbs':{'Admin':'/admin','Manage Recipients':'email_recipients'},
          'nav_section':'email',
          'nav_sub':'recipients'
       },
       context_instance=RequestContext(request)
    )


@login_required
@staff_member_required
def email_delete(request):
    """Remove Email Recipients"""

    # If this is a POST, then validate the form and save the data, otherise send them
    # to the main recipients page
    if request.method == 'POST':
        
        # Check the form elements
        form = RemoveEmailForm(request.POST)

        if form.is_valid():
            # Remove the email recipients

            # If these recipients are currently tied to incidents or maintenances,
            # Do not allow them to be deleted w/o removing them from the relevant
            # recipients first
            for id in request.POST.getlist('id'):

                # Part of any incidents or maintenances?
                if Event.objects.filter(event_email__email__id=id):
                    return system_message(request,True,'At least one of the recipients you are attempting to delete is currently part of an incident or maintenance.  Please remove the recipient from the incident/maintenance, or delete the incident/maintenance and then delete the recipient.')
                # Ok, remove it
                else:
                    Email.objects.filter(id=id).delete()

    # Not a POST or a failed POST
    # Send them back so they can see the newly updated services list
    return HttpResponseRedirect('/admin/email_recipients')