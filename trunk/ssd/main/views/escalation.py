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
from ssd.main.models import Config_Escalation, Escalation
from ssd.main.forms import AddContactForm, EscalationConfigForm, ModifyContactForm


def escalation(request):
    """Escalation page

    Print an escalation page should a user want additional information
    on who to contact when incidents occur

    """

    # If this functionality is disabled in the admin, let the user know
    if Config_Escalation.objects.filter(id=Config_Escalation.objects.values('id')[0]['id']).values('enabled')[0]['enabled'] == 0:
        messages.add_message(request, messages.ERROR, 'Your system administrator has disabled the escalation path functionality')
        return HttpResponseRedirect('/')

    # Obtain the escalation contacts
    contacts = Escalation.objects.filter(hidden=False).values('id','name','contact_details').order_by('order')

    # Print the page
    return render_to_response(
       'escalation/escalation.html',
       {
          'title':'System Status Dashboard | Escalation Path',
          'contacts':contacts,
          'instructions':Config_Escalation.objects.filter(id=Config_Escalation.objects.values('id')[0]['id']).values('instructions')[0]['instructions']
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
            instructions = form.cleaned_data['instructions']

            # There should only ever be one record in this table
            Config_Escalation.objects.filter(id=Config_Escalation.objects.values('id')[0]['id']).update(enabled=enabled,instructions=instructions)

            messages.add_message(request, messages.SUCCESS, 'Escalation configuration saved successfully')
        else:
            messages.add_message(request, messages.ERROR, 'Invalid data entered, please correct the errors below:')


    # Not a POST or a failed form submit
    else:
        # Create a blank form
        form = EscalationConfigForm

    # Obtain the escalation config
    escalation_config = Config_Escalation.objects.filter(id=Config_Escalation.objects.values('id')[0]['id']).values('enabled','instructions')

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

            # Obtain all id's and orders and put into a dictionary
            orders = Escalation.objects.values('id','order').order_by('order')
            
            # Run through the orders and see if we need to change anything
            # If we are moving up, switch places with the previous
            # If we are moving down, switch places with the next
            # If we are deleting, remove and then reorder everything
            # If we are hiding, remove the order
            # If we are unhiding, add to the end

            
            # Move this up, meaning decrease the order (only if greater than 1)
            if action == 'up':

                # Get the order
                id_order = Escalation.objects.filter(id=id).values('order')[0]['order']
                
                # If the order if greater than 1, move it
                if id_order > 1:
                    
                    # Get the id of the one before this one so we can switch places with it
                    after_order = id_order - 1
                    after_id = Escalation.objects.filter(order=after_order).values('id')[0]['id']

                    # Switch places
                    Escalation.objects.filter(id=id).update(order=F('order')-1)
                    Escalation.objects.filter(id=after_id).update(order=F('order')+1)
            
            # Move this down, meaning increase the order
            elif action == "down": 

                # Get the order
                id_order = Escalation.objects.filter(id=id).values('order')[0]['order']

                # If it's already at the bottom, don't do anything
                # Get a count of contacts
                contacts_count = Escalation.objects.count()
                
                # If the order is less than the total, move it down (otherwise it's already at the bottom)
                if id_order < contacts_count:
                    
                    # Get the id of the one after this one so we can switch places with it
                    after_order = id_order + 1
                    after_id = Escalation.objects.filter(order=after_order).values('id')[0]['id']

                    # Switch places
                    Escalation.objects.filter(id=id).update(order=F('order')+1)
                    Escalation.objects.filter(id=after_id).update(order=F('order')-1)

            # Delete
            elif action == 'delete':

                # Delete the object and then re-order what's left
                Escalation.objects.filter(id=id).delete()

                # Get the orders
                orders = Escalation.objects.values('id','order').order_by('order')

                # If there's more than 1, re-order
                if orders > 1:
                    # Start a counter at 1 and reset the orders
                    counter = 1
                    for contact in orders:
                        Escalation.objects.filter(id=contact['id']).update(order=counter)
                        counter += 1
            
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