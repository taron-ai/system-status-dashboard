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


"""This module contains all of the basic user facing views for SSD

"""


from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.db.models import F
from django.contrib import messages
from ssd.main.models import Config_Escalation
from ssd.main.models import Escalation
from ssd.main.forms import AddContactForm, EscalationConfigForm, ModifyContactForm
from ssd.main import config_value


def escalation(request):
    """Escalation page

    Print an escalation page should a user want additional information
    on who to contact when incidents occur

    """

    # Instantiate the configuration value getter
    cv = config_value.config_value()

    # If this functionality is disabled in the admin, let the user know
    if int(cv.value('escalation_display')) == 0:
        return system_message(request,True,'Your system administrator has disabled this functionality')

    # Obtain the escalation contacts
    contacts = Escalation.objects.filter(hidden=False).values('id','name','contact_details').order_by('order')

    # Help message
    help = cv.value('help_escalation')

    # Print the page
    return render_to_response(
       'escalation/escalation.html',
       {
          'title':'System Status Dashboard | Escalation Path',
          'contacts':contacts,
          'help':help
       },
       context_instance=RequestContext(request)
    )


@login_required
@staff_member_required
def escalation_config(request):
    """Main admin index view
 
    """

    # If this is a POST, then validate the form and save the data
    if request.method == 'POST':

        # Check the form elements
        form = EscalationConfigForm(request.POST)

        if form.is_valid():
            # Obtain the cleaned data
            enabled = form.cleaned_data['enabled']

            # There should only ever be one record in this table
            Config_Escalation.objects.filter(id=Config_Escalation.objects.values('id')[0]['id']).update(enabled=enabled)

            messages.add_message(request, messages.SUCCESS, 'Escalation configuration saved successfully')
        else:
            messages.add_message(request, messages.ERROR, 'Invalid data entered, please correct the errors below:')


    # Not a POST or a failed form submit
    else:
        # Create a blank form
        form = EscalationConfigForm

    # Obtain the escalation config
    escalation_config = Config_Escalation.objects.filter(id=Config_Escalation.objects.values('id')[0]['id']).values('enabled')

    # Print the page
    return render_to_response(
       'escalation/config.html',
       {
          'title':'System Status Dashboard | Escalation Admin',
          'escalation_config':escalation_config,
          'form':form,
          'breadcrumbs':{'Admin':'/admin','Escalation Configuration':'escalation_config'},
          'nav_section':'escalation',
          'nav_sub':'escalation_config'
       },
       context_instance=RequestContext(request)
    )


@login_required
@staff_member_required
def escalation_contacts(request):
    """View and Add Escalation Contacts
 
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

            # Obtain the last entry
            order = Escalation.objects.values('order').order_by('-order')[:1]
            
            # If there are no entries, this will be 1
            if not order:
                order = 1
            # Increase the order by 1
            else:
                order = order[0]['order'] + 1

            # Don't allow duplicates
            try:
                Escalation(order=order,name=name,contact_details=contact_details,hidden=True).save()
            except IntegrityError:
                pass

            # Send them back so they can see the newly created email addresses
            # incident
            return HttpResponseRedirect('/admin/escalation_contacts')

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
       'escalation/contacts.html',
       {
          'title':'System Status Dashboard | Manage Escalation Contacts',
          'form':form,
          'contacts':contacts,
          'breadcrumbs':{'Admin':'/admin','Manage Escalation Contacts':'escalation_contacts'},
          'nav_section':'escalation',
          'nav_sub':'escalation_contacts'
       },
       context_instance=RequestContext(request)
    )


@login_required
@staff_member_required
def escalation_modify(request):
    """Remove Contacts"""

    # If this is a GET, then validate the form and save the data, otherise send them
    # to the main escalation page
    if request.method == 'GET':
        
        # Check the form elements
        form = ModifyContactForm(request.GET)

        if form.is_valid():
            id = form.cleaned_data['id']
            action = form.cleaned_data['action']    

            # Obtain all id's and orders and put into a dictionar
            orders = Escalation.objects.values('id','order').order_by('order')
            contacts = {}
            for contact in orders:
                contacts[contact['id']] = contact['order']

            print contacts

            # Perform the action
            
            # Delete
            if action == 'delete':
                Escalation.objects.filter(id=id).delete()
            
            # Move up
            elif action == 'down':
                Escalation.objects.filter(id=id).update(order=F('order')+1)
            
            # Move down (only if greater than 1)
            elif action == 'up':
                if Escalation.objects.filter(id=id).values('order')[0]['order'] > 1:
                    Escalation.objects.filter(id=id).update(order=F('order')-1)

            # Hide
            elif action == 'hide':
                Escalation.objects.filter(id=id).update(hidden=True)

            # Show
            elif action == 'show':
                Escalation.objects.filter(id=id).update(hidden=False)

            # Set a success message
            messages.add_message(request, messages.SUCCESS, 'Escalation contacts successfully modified.')
        # Invalid form
        else:
            messages.add_message(request, messages.ERROR, 'There was an error processing your request: %s' % form.errors)

    # Send them back so they can see the newly updated services list
    return HttpResponseRedirect('/admin/escalation_contacts')