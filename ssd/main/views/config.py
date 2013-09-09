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
from django.db.models import F
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

@login_required
@staff_member_required
def email(request):
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

            # Send them back so they can see the newly created email addresses
            return HttpResponseRedirect('/email')
        else:
            print 'Invalid form: AddEmailForm: %s' % form.errors

    # Not a POST
    else:
        # Create a blank form
        form = AddEmailForm()
    
    # Obtain all current email addresses
    emails = Email.objects.all()
    
    # Print the page
    return render_to_response(
       'config/email.html',
       {
          'title':'System Status Dashboard | Manage Email Recipients',
          'form':form,
          'emails':emails
       },
       context_instance=RequestContext(request)
    )

@login_required
@staff_member_required
def rm_email(request):
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

        # Invalid form
        else:
            print 'Invalid form: RemoveEmailForm: %s' % form.errors

    # Not a POST or a failed POST
    # Send them back so they can see the newly updated services list
    return HttpResponseRedirect('/email')


@login_required
@staff_member_required
def services(request):
    """View and Add Services
 
    """

    # If this is a POST, then validate the form and save the data
    if request.method == 'POST':
       
        # Check the form elements
        form = AddServiceForm(request.POST)

        if form.is_valid():
            service = form.cleaned_data['service']

            # Don't allow duplicates
            try:
                Service(service_name=service).save()
            except IntegrityError:
                pass

            # Send them back so they can see the newly created email addresses
            # incident
            return HttpResponseRedirect('/services')

        # Invalid form
        else:
            print 'Invalid form: AddServiceForm: %s' % form.errors

    # Not a POST
    else:
        # Create a blank form
        form = AddServiceForm()
    
    # Obtain all current email addresses
    services = Service.objects.values('id','service_name')
    
    # Print the page
    return render_to_response(
       'config/services.html',
       {
          'title':'System Status Dashboard | Manage Services',
          'form':form,
          'services':services
       },
       context_instance=RequestContext(request)
    )


@login_required
@staff_member_required
def rm_services(request):
    """Remove Services"""

    # If this is a POST, then validate the form and save the data, otherise send them
    # to the main services page
    if request.method == 'POST':
        
        # Check the form elements
        form = RemoveServiceForm(request.POST)

        if form.is_valid():
            # Remove the services
            
            # If these services are currently tied to incidents or maintenances,
            # Do not allow them to be deleted w/o removing them from the relevant
            # services first
            for id in request.POST.getlist('id'):

                # Part of any incidents or maintenances?
                if Service_Issue.objects.filter(service_name_id=id) or Service_Maintenance.objects.filter(service_name_id=id):
                    return system_message(request,True,'At least one of the services you are attempting to delete is currently part of an incident or maintenance.  Please remove the service from the incident/maintenance, or delete the incident/maintenance and then delete the service.')
                # Ok, remove it
                else:
                    Service.objects.filter(id=id).delete()

        # Invalid form
        else:
            print 'Invalid form: RemoveServiceForm: %s' % form.errors

    # Not a POST or a failed POST
    # Send them back so they can see the newly updated services list
    return HttpResponseRedirect('/services')


@login_required
@staff_member_required
def contacts(request):
    """View and Add Contacts
 
    """

    # Instantiate the configuration value getter
    cv = config_value.config_value()

    # If this is a POST, then validate the form and save the data
    if request.method == 'POST':
       
        # Check the form elements
        form = AddContactForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            contact_details = form.cleaned_data['contact_details']

            # Don't allow duplicates
            try:
                Escalation(order=1,name=name,contact_details=contact_details,hidden=True).save()
            except IntegrityError:
                pass

            # Send them back so they can see the newly created email addresses
            # incident
            return HttpResponseRedirect('/contacts')

        # Invalid form
        else:
            print 'Invalid form: AddContactForm: %s' % form.errors

    # Not a POST
    else:
        # Create a blank form
        form = AddContactForm()
    
    # Obtain all current email addresses
    contacts = Escalation.objects.values('id','order','name','hidden').order_by('order')
   
    # Obtain the default maintenance textfield text
    instr_escalation_name = cv.value('instr_escalation_name')
    instr_escalation_details = cv.value('instr_escalation_details') 

    # Print the page
    return render_to_response(
       'config/contacts.html',
       {
          'title':'System Status Dashboard | Manage Contacts',
          'form':form,
          'contacts':contacts,
          'instr_escalation_name':instr_escalation_name,
          'instr_escalation_details':instr_escalation_details
       },
       context_instance=RequestContext(request)
    )


@login_required
@staff_member_required
def contacts_modify(request):
    """Remove Contacts"""

    # If this is a POST, then validate the form and save the data, otherise send them
    # to the main services page
    if request.method == 'POST':
        
        # Check the form elements
        form = ModifyContactForm(request.POST)

        if form.is_valid():
            id = form.cleaned_data['id']
            action = form.cleaned_data['action']    

            # Perform the action
            
            # Delete
            if action == 'delete':
                Escalation.objects.filter(id=id).delete()
            
            # Move up
            elif action == 'up':
                Escalation.objects.filter(id=id).update(order=F('order')+1)
            
            # Move down (only if greater than 1)
            elif action == 'down':
                if Escalation.objects.filter(id=id).values('order')[0]['order'] > 1:
                    Escalation.objects.filter(id=id).update(order=F('order')-1)

            # Hide
            elif action == 'hide':
                Escalation.objects.filter(id=id).update(hidden=True)

            # show
            elif action == 'show':
                Escalation.objects.filter(id=id).update(hidden=False)

        # Invalid form
        else:
            print 'Invalid form: RemoveContactForm: %s' % form.errors

    # Not a POST or a failed POST
    # Send them back so they can see the newly updated services list
    return HttpResponseRedirect('/contacts')