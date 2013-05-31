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


"""Views for the SSD Project that pertain to creating events (incidents, maintenance)

"""


import datetime
import pytz
import re
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone as jtz
from ssd.main.models import Incident
from ssd.main.models import Incident_Update
from ssd.main.models import Report
from ssd.main.models import Service
from ssd.main.models import Service_Issue
from ssd.main.models import Maintenance
from ssd.main.models import Maintenance_Update
from ssd.main.models import Recipient
from ssd.main.models import Service_Maintenance
from ssd.main.forms import AddIncidentForm
from ssd.main.forms import DeleteEventForm
from ssd.main.forms import UpdateIncidentForm
from ssd.main.forms import UpdateMaintenanceForm
from ssd.main.forms import EmailMaintenanceForm
from ssd.main.forms import ReportIncidentForm
from ssd.main.forms import AddMaintenanceForm
from ssd.main import notify
from ssd.main import config_value
from ssd.main.views.main import system_message


def report(request):
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
       'events/report.html',
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
def incident(request):
    """Create Incident Page

    Create a new incident view

    """

    # Instantiate the configuration value getter
    cv = config_value.config_value()

    # Obtain the timezone (or set to the default DJango server timezone)
    if request.COOKIES.get('timezone') == None:
        set_timezone = settings.TIME_ZONE
    else:
        set_timezone = request.COOKIES.get('timezone')
    
    # If this is a POST, then validate the form and save the data
    # Some validation must take place manually
    if request.method == 'POST':
        # Give the template a blank time if this is a post 
        # the user will have already set it.
        time_now = ''

        # If this is a form submit that fails, we want to reset whatever services were selected
        # by the user.  Templates do not allow access to Arrays stored in QueryDict objects so we have
        # to determine the list and send back to the template on failed form submits
        affected_svcs = request.POST.getlist('service')

        # Check the form elements
        form = AddIncidentForm(request.POST)

        if form.is_valid():
            # Obtain the cleaned data
            date = form.cleaned_data['date']
            detail = form.cleaned_data['detail']
            time = form.cleaned_data['time']
            broadcast = form.cleaned_data['broadcast']
            recipient_id = form.cleaned_data['recipient_id']

            # Get the user's ID
            user_id = User.objects.filter(username=request.user.username).values('id')[0]['id']

            # Create a datetime object and add the timezone
            # Put the date and time together
            incident_time = datetime.datetime.combine(date,time)

            # Set the timezone
            tz = pytz.timezone(set_timezone)
            incident_time = tz.localize(incident_time)

            # Add the incident and services
            # Don't allow the same incident to be added 2x
            # The user might have hit the back button and submitted again

            # Check for this incident
            incident_id = Incident.objects.filter(date=incident_time,detail=detail,user_id=user_id).values('id')
            
            # If its not there, add it                                     
            if not incident_id:
                Incident(date=incident_time,detail=detail,email_address_id=recipient_id,user_id=user_id).save()
                incident_id = Incident.objects.filter(date=incident_time,detail=detail,user_id=user_id).values('id')

                # Find out which services this impacts and save the data
                # Form validation confirms that there is at least 1
                for service_id in affected_svcs:
                    # Should be number only -- can't figure out how to validate
                    # multiple checkboxes in the form
                    if re.match(r'^\d+$', service_id):
                        Service_Issue(service_name_id=service_id,incident_id=incident_id[0]['id']).save()

            # Send an email notification to the appropriate list about this issue if requested.  Broadcast won't be
            # allowed to be true if an email address is not defined.
            # Don't send an email if notifications are disabled
            if int(cv.value('notify')) == 1:
                if broadcast:
                    email = notify.email()
                    email.incident(incident_id[0]['id'],recipient_id,set_timezone,True)

            # Send them to the incident detail page for this newly created
            # incident
            return HttpResponseRedirect('/i_detail?id=%s' % incident_id[0]['id'])

        # Bad form validation
        else:
            print 'Invalid form: %s.  Errors: %s' % ('AddIncidentForm',form.errors)

    # Not a POST so create a blank form
    else:
        # There are no affected services selected yet
        affected_svcs = []

        form = AddIncidentForm()

        # Obtain the current date/time so we can pre-fill them
        # Create a datetime object for right now
        time_now = datetime.datetime.now()

        # Add the server's timezone (whatever DJango is set to)
        time_now = pytz.timezone(settings.TIME_ZONE).localize(time_now)

        # Now convert to the requested timezone
        time_now = time_now.astimezone(pytz.timezone(set_timezone))

    # Obtain all services
    services = Service.objects.values('id','service_name').order_by('service_name')

    # Obtain all current email addresses
    recipients = Recipient.objects.values('id','email_address')

    # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
    jtz.activate(set_timezone)

    # Help message
    help = cv.value('help_create_incident')

    # See if email notifications are enabled
    notifications = int(cv.value('notify'))

    # Obtain the incident description text
    instr_incident_description = cv.value('instr_incident_description')

    # Print the page
    return render_to_response(
       'events/incident.html',
       {
          'title':'System Status Dashboard | Create Incident',
          'services':services,
          'recipients':recipients,
          'affected_svcs':tuple(affected_svcs),
          'form':form,
          'time_now':time_now,
          'help':help,
          'notifications':notifications,
          'instr_incident_description':instr_incident_description

       },
       context_instance=RequestContext(request)
    )


@login_required
@staff_member_required
def i_update(request):
    """Update Incident Page

    Accept input to update the incident

    """

    # Instantiate the configuration value getter
    cv = config_value.config_value()

    # Obtain the timezone (or set to the default DJango server timezone)
    if request.COOKIES.get('timezone') == None:
        set_timezone = settings.TIME_ZONE
    else:
        set_timezone = request.COOKIES.get('timezone')

    # If this is a POST, then validate the form and save the data
    # Some validation must take place manually (service
    # addition/subtraction
    if request.method == 'POST':

        # Give the template a blank time if this is a post 
        # the user will have already set it.
        time_now = ''

        # If this is a form submit that fails, we want to reset whatever services were selected
        # by the user.  Templates do not allow access to Arrays stored in QueryDict objects so we have
        # to determine the list and send back to the template on failed form submits
        affected_svcs = request.POST.getlist('service')

        # Check the form elements
        form = UpdateIncidentForm(request.POST)

        if form.is_valid():

            # Obtain the cleaned data
            date = form.cleaned_data['date']
            update = form.cleaned_data['update']
            time = form.cleaned_data['time']
            broadcast = form.cleaned_data['broadcast']
            recipient_id = form.cleaned_data['recipient_id']
            id = form.cleaned_data['id']
            closed = form.cleaned_data['closed']

            # Get the user's ID
            user_id = User.objects.filter(username=request.user.username).values('id')[0]['id']

            # Create a datetime object and add the timezone
            # Put the date and time together
            incident_time = datetime.datetime.combine(date,time)

            # Set the timezone
            tz = pytz.timezone(set_timezone)
            incident_time = tz.localize(incident_time)

            # Add the detail text 
            # Don't allow the same detail to be added 2x
            # The user might have hit the back button and submitted again
            detail_id = Incident_Update.objects.filter(date=incident_time,detail=update,).values('id')
            if not detail_id:
                Incident_Update(date=incident_time,incident_id=id,detail=update,user_id=user_id).save()

                # See if we are adding or subtracting services
                # The easiest thing to do here is remove all affected  
                # services and re-add the ones indicated here

                # Remove first
                Service_Issue.objects.filter(incident_id=id).delete()
        
                # Now add (form validation confirms that there is at least 1)
                for service_id in affected_svcs:
                    # Should be number only -- can't figure out how to validate
                    # multiple checkboxes in the form
                    if re.match(r'^\d+$', service_id):
                        Service_Issue(service_name_id=service_id,incident_id=id).save()

            # See if we are closing this issue 
            if closed:
                # If it was already closed, then don't re-close it because it will update the closed time
                if not Incident.objects.filter(id=id).values('closed')[0]['closed']:
                    Incident.objects.filter(id=id).update(closed=incident_time)
            else:
                Incident.objects.filter(id=id).update(closed=None)

            # Send an email notification to the appropriate list about this issue if requested.  Broadcast won't be
            # allowed to be true if an email address is not defined.
            # Don't send an email if notifications are disabled
            if int(cv.value('notify')) == 1:
                if broadcast:
                    # Update the email address
                    recipient = Recipient.objects.filter(id=recipient_id).values('email_address')
                    Incident.objects.filter(id=id).update(email_address=recipient_id)

                    email = notify.email()
                    email.incident(id,recipient_id,set_timezone,False)
            
                # If broadcast is not selected, turn off emails
                else:
                    Incident.objects.filter(id=id).update(email_address=None)


            # All done so redirect to the incident detail page so
            # the new data can be seen.
            return HttpResponseRedirect('/i_detail?id=%s' % id)
        
        # Bad form validation
        else:
            print 'Invalid form: %s.  Errors: %s' % ('UpdateIncidentForm',form.errors)

            # Obtain the id so we can print the update page again
            if 'id' in request.POST: 
                if re.match(r'^\d+$', request.POST['id']):
                    id = request.POST['id']
                else:
                    return system_message(request,True,'Improperly formatted id') 
            else:
                return system_message(request,True,'No incident ID given') 

    # Not a POST so create a blank form
    else:
        # Obtain the id 
        if 'id' in request.GET: 
            if re.match(r'^\d+$', request.GET['id']):
                id = request.GET['id']
            else:
                return system_message(request,True,'Improperly formatted id') 
        else:
            return system_message(request,True,'No incident ID given')

        # In the case of a GET, we can acquire the proper services from the DB
        affected_svcs_tmp = Service_Issue.objects.filter(incident_id=id).values('service_name_id')
        affected_svcs = []
        for service_id in affected_svcs_tmp:
            affected_svcs.append(service_id['service_name_id'])
        affected_svcs = list(affected_svcs)
        
        # Create a blank form
        form = UpdateIncidentForm()

        # Obtain the current date/time so we can pre-fill them
        # Create a datetime object for right now
        time_now = datetime.datetime.now()

        # Add the server's timezone (whatever DJango is set to)
        time_now = pytz.timezone(settings.TIME_ZONE).localize(time_now)

        # Now convert to the requested timezone
        time_now = time_now.astimezone(pytz.timezone(set_timezone))

    # Obtain the open/closed status and the email address (if assigned)
    details = Incident.objects.filter(id=id).values('closed','email_address_id')

    # Obtain all services
    services = Service.objects.values('id','service_name').order_by('service_name')

    # Obtain all current email addresses
    recipients = Recipient.objects.values('id','email_address')

    # See if email notifications are enabled
    notifications = int(cv.value('notify'))

    # Obtain the incident update text
    instr_incident_update = cv.value('instr_incident_update')

    # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
    jtz.activate(set_timezone)

    # Print the page
    return render_to_response(
       'events/i_update.html',
       {
          'title':'System Status Dashboard | Update Incident',
          'details':details,
          'services':services,
          'affected_svcs':affected_svcs,
          'id':id,
          'form':form,
          'recipients':recipients,
          'notifications':notifications,
          'time_now':time_now,
          'instr_incident_update':instr_incident_update
       },
       context_instance=RequestContext(request)
    )


@login_required
@staff_member_required
def i_delete(request):
    """Delete Incident Page

    Delete an incident given an id

    """

    # We only accept posts
    if request.method == 'POST':
        
        # Check the form elements
        form = DeleteEventForm(request.POST)

        if form.is_valid():

            # Obtain the cleaned data
            id = form.cleaned_data['id']

            # Delete the incident
            Incident.objects.filter(id=id).delete()

            # Redirect to the homepage
            return HttpResponseRedirect('/')

    # If processing got this far, its either not a POST
    # or its an invalid form submit.  Either way, give an error        
    return system_message(request,True,'Invalid delete request')


@login_required
@staff_member_required
def maintenance(request):
    """Schedule maintenance page

    """

    # Instantiate the configuration value getter
    cv = config_value.config_value()

    # Obtain the timezone (or set to the default DJango server timezone)
    if request.COOKIES.get('timezone') == None:
        set_timezone = settings.TIME_ZONE
    else:
        set_timezone = request.COOKIES.get('timezone')

    # If this is a POST, then validate the form and save the data
    # Some validation must take place manually
    if request.method == 'POST':

        # If this is a form submit that fails, we want to reset whatever services were selected
        # by the user.  Templates do not allow access to Arrays stored in QueryDict objects so we have
        # to determine the list and send back to the template on failed form submits
        affected_svcs = request.POST.getlist('service')

        # Check the form elements
        form = AddMaintenanceForm(request.POST)

        if form.is_valid():
            # Obtain the cleaned data
            s_date = form.cleaned_data['s_date']
            s_time = form.cleaned_data['s_time']
            e_date = form.cleaned_data['e_date']
            e_time = form.cleaned_data['e_time']
            description = form.cleaned_data['description']
            impact = form.cleaned_data['impact']
            coordinator = form.cleaned_data['coordinator']
            broadcast = form.cleaned_data['broadcast']
            recipient_id = form.cleaned_data['recipient_id']
                        
            # Combine the dates and times into datetime objects
            start = datetime.datetime.combine(s_date, s_time)
            end = datetime.datetime.combine(e_date, e_time)

            # Set the timezone
            tz = pytz.timezone(set_timezone)
            start = tz.localize(start)
            end = tz.localize(end)
            
            # Get the user's ID
            user_id = User.objects.filter(username=request.user.username).values('id')[0]['id']
            
            # Add the maintenance and services
            # Don't allow the same maintenance to be added 2x
            # The user might have hit the back button and submitted again

            # Look for an existing maintenance w/ these params
            maintenance_id = Maintenance.objects.filter(
                                                        start=start,
                                                        end=end,
                                                        description=description,
                                                        impact=impact,
                                                        coordinator=coordinator,
                                                        user_id=user_id,
                                                        completed=0
                                                       ).values('id')
            
            # Create it, if not there
            if not maintenance_id:
                Maintenance(
                            start=start,
                            end=end,
                            description=description,
                            impact=impact,
                            coordinator=coordinator,
                            user_id=user_id,
                            email_address_id=recipient_id,
                            completed=0,
                           ).save()

                # Obtain the maintenance id
                maintenance_id = Maintenance.objects.filter(
                                                            start=start,
                                                            end=end,
                                                            description=description,
                                                            impact=impact,
                                                            coordinator=coordinator,
                                                            user_id=user_id,
                                                            completed=0
                                                           ).values('id')

                # Find out which services this impacts and save the data
                # Form validation confirms that there is at least 1
                for service_id in affected_svcs:
                    # Should be number only -- can't figure out how to validate
                    # multiple checkboxes in the form
                    if re.match(r'^\d+$', service_id):
                        Service_Maintenance(service_name_id=service_id,maintenance_id=maintenance_id[0]['id']).save()

            # Send an email notification to the appropriate list about this maintenance, if requested
            # Don't send an email if notifications are disabled
            if int(cv.value('notify')) == 1:
                if broadcast:
                    email = notify.email()
                    email.maintenance(maintenance_id[0]['id'],recipient_id,set_timezone,True)

            # Send them to the incident detail page for this newly created
            # maintenance
            return HttpResponseRedirect('/m_detail?id=%s' % maintenance_id[0]['id'])

        # Invalid Form
        else:
            print 'Invalid form: AddMaintenanceForm: %s' % form.errors

    # Not a POST so create a blank form
    else:

        # There are no affected services selected yet
        affected_svcs = []
        
        form = AddMaintenanceForm() 
    
    # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
    jtz.activate(set_timezone)

    # Obtain all current email addresses
    recipients = Recipient.objects.values('id','email_address')

    # Obtain all services
    services = Service.objects.values('id','service_name').order_by('service_name')
    
    # Help message
    help = cv.value('help_sched_maint')

    # See if email notifications are enabled
    notifications = int(cv.value('notify'))

    # Obtain the default maintenance textfield text
    instr_maintenance_description = cv.value('instr_maintenance_description')
    instr_maintenance_impact = cv.value('instr_maintenance_impact')
    instr_maintenance_coordinator= cv.value('instr_maintenance_coordinator')

    # Print the page
    return render_to_response(
       'events/maintenance.html',
       {
          'title':'System Status Dashboard | Scheduled Maintenance',
          'form':form,
          'help':help,
          'services':services,
          'affected_svcs':tuple(affected_svcs),
          'recipients':recipients,
          'notifications':notifications,
          'instr_maintenance_description':instr_maintenance_description,
          'instr_maintenance_impact':instr_maintenance_impact,
          'instr_maintenance_coordinator':instr_maintenance_coordinator
       },
       context_instance=RequestContext(request)
    )


@login_required
@staff_member_required
def m_update(request):
    """Update Maintenance Page

    Accept input to update the scheduled maintenance

    """

    # Instantiate the configuration value getter
    cv = config_value.config_value()

    # Obtain the timezone (or set to the default DJango server timezone)
    if request.COOKIES.get('timezone') == None:
        set_timezone = settings.TIME_ZONE
    else:
        set_timezone = request.COOKIES.get('timezone')

    # If this is a POST, then validate the form and save the data
    # Some validation must take place manually (service
    # addition/subtraction
    if request.method == 'POST':

        # If this is a form submit that fails, we want to reset whatever services were selected
        # by the user.  Templates do not allow access to Arrays stored in QueryDict objects so we have
        # to determine the list and send back to the template on failed form submits
        affected_svcs = request.POST.getlist('service')

        # Check the form elements
        form = UpdateMaintenanceForm(request.POST)

        if form.is_valid():
            # Obtain the cleaned data
            s_date = form.cleaned_data['s_date']
            s_time = form.cleaned_data['s_time']
            e_date = form.cleaned_data['e_date']
            e_time = form.cleaned_data['e_time']
            description = form.cleaned_data['description']
            impact = form.cleaned_data['impact']
            coordinator = form.cleaned_data['coordinator']
            update = form.cleaned_data['update']
            broadcast = form.cleaned_data['broadcast']
            recipient_id = form.cleaned_data['recipient_id']
            id = form.cleaned_data['id']

            # Get the user's ID
            user_id = User.objects.filter(username=request.user.username).values('id')[0]['id']

            # Check if we are starting/completing
            # The logic of when these two can/cannot be done is handled
            # in the form validation
            if 'started' in request.POST:
                started = 1
            else:
                started = 0

            # Check if we are completing
            if 'completed' in request.POST:
                completed = 1
            else:
                completed = 0

            # See if we are adding or subtracting services
            # The easiest thing to do here is remove all affected  
            # services and re-add the ones indicated here
            # Remove first
            Service_Maintenance.objects.filter(maintenance_id=id).delete()
        
            # Now add the services (form validation confirms that there is at least 1)
            for service_id in request.POST.getlist('service'):
                # Should be number only -- can't figure out how to validate
                # multiple checkboxes in the form
                if re.match(r'^\d+$', service_id):
                    Service_Maintenance(service_name_id=service_id,maintenance_id=id).save()
            
            # Add the update
            # Obtain the time and add a timezone
            # Create a datetime object for right now
            time_now = datetime.datetime.now()
            # Add the server's timezone (whatever DJango is set to)
            time_now = pytz.timezone(settings.TIME_ZONE).localize(time_now)
            # Add it
            Maintenance_Update(date=time_now,maintenance_id=id,user_id=user_id,detail=update).save()
            
            # Update the core maintenance parameters
            # Combine the dates and times into datetime objects
            start = datetime.datetime.combine(s_date, s_time)
            end = datetime.datetime.combine(e_date, e_time)

            # Set the timezone
            tz = pytz.timezone(set_timezone)
            start = tz.localize(start)
            end = tz.localize(end)
           
            # Update the main entry 
            Maintenance.objects.filter(id=id).update(
                                                     start=start,
                                                     end=end,
                                                     description=description,
                                                     impact=impact,
                                                     coordinator=coordinator,
                                                     started=started,
                                                     completed=completed
                                                    )

            # Send an email notification to the appropriate list about this issue if requested.  Broadcast won't be
            # allowed to be true if an email address is not defined.
            # Don't send an email if notifications are disabled
            if int(cv.value('notify')) == 1:
                if broadcast:
                    # Update the email address
                    recipient = Recipient.objects.filter(id=recipient_id).values('email_address')
                    Maintenance.objects.filter(id=id).update(email_address=recipient_id)

                    email = notify.email()
                    email.maintenance(id,recipient_id,set_timezone,False)
            
                # If broadcast is not selected, turn off emails
                else:
                    Maintenance.objects.filter(id=id).update(email_address=None)

            # All done so redirect to the maintenance detail page so
            # the new data can be seen.
            return HttpResponseRedirect('/m_detail?id=%s' % id)
    
        else:
            print 'Invalid form: UpdateMaintenanceForm: %s' % form.errors

    # Not a POST
    else:

        # Obtain the id 
        if 'id' in request.GET: 
            if re.match(r'^\d+$', request.GET['id']):
                id = request.GET['id']
            else:
                return system_message(request,True,'Improperly formatted id') 
        else:
            return system_message(request,True,'No incident ID given')

        # In the case of a GET, we can acquire the proper services from the DB
        affected_svcs_tmp = Service_Maintenance.objects.filter(maintenance_id=id).values('service_name_id')
        affected_svcs = []
        for service_id in affected_svcs_tmp:
            affected_svcs.append(service_id['service_name_id'])
        affected_svcs = list(affected_svcs)

        # Create a blank form
        form = UpdateIncidentForm()

    # Obtain the id (this could have been a GET or a failed POST)
    if request.method == 'GET':
        if 'id' in request.GET:
            id = request.GET['id']
    elif request.method == 'POST':
        if 'id' in request.POST:
            id = request.POST['id']

    # If we don't have the ID, then we have to give them an error
    if not id:
        return system_message(request,True,'No incident ID given')

    # Make sure the ID is properly formed
    if not re.match(r'^\d+$', id):
        return system_message(request,True,'Improperly formatted ID: %s' % id)

    # See if the maintenance is completed
    status = Maintenance.objects.filter(id=id).values('started','completed')

    # Obtain all services
    services = Service.objects.values('id','service_name').order_by('service_name')

    # Obtain the details of this maintenance
    details = Maintenance.objects.filter(id=id).values('start','end','description','impact','coordinator','started','completed','email_address_id')

    start = details[0]['start']
    end = details[0]['end']

    # Set the timezone
    start = start.astimezone(pytz.timezone(set_timezone))
    end = end.astimezone(pytz.timezone(set_timezone))
    
    # Format the start/end date/time
    s_date = start.strftime("%Y-%m-%d")   
    s_time = start.strftime("%H:%M")
    e_date = end.strftime("%Y-%m-%d")
    e_time = end.strftime("%H:%M")

    # Obtain all current email addresses
    recipients = Recipient.objects.values('id','email_address')

    # See if email notifications are enabled
    notifications = int(cv.value('notify'))

    # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
    jtz.activate(set_timezone)

    # Obtain the default maintenance textfield text
    instr_maintenance_description = cv.value('instr_maintenance_description')
    instr_maintenance_impact = cv.value('instr_maintenance_impact')
    instr_maintenance_coordinator= cv.value('instr_maintenance_coordinator')
    instr_maintenance_update= cv.value('instr_maintenance_update')

    # Print the page
    return render_to_response(
       'events/m_update.html',
       {
          'title':'System Status Dashboard | Scheduled Maintenance Update',
          'details':details,
          'affected_svcs':affected_svcs,
          'services':services,
          'id':id,
          'form':form,
          'status':status,
          's_date':s_date,
          's_time':s_time,
          'e_date':e_date,
          'e_time':e_time,
          'recipients':recipients,
          'notifications':notifications,
          'instr_maintenance_description':instr_maintenance_description,
          'instr_maintenance_impact':instr_maintenance_impact,
          'instr_maintenance_coordinator':instr_maintenance_coordinator,
          'instr_maintenance_update':instr_maintenance_update,
       },
       context_instance=RequestContext(request)
    )


@login_required
@staff_member_required
def m_email(request):
    """Send an Email Notification about a Maintenance"""

    # Instantiate the configuration value getter
    cv = config_value.config_value()

    # Obtain the timezone (or set to the default DJango server timezone)
    if request.COOKIES.get('timezone') == None:
        set_timezone = settings.TIME_ZONE
    else:
        set_timezone = request.COOKIES.get('timezone')

    # We will only accept POSTs
    if request.method == 'POST':

        # Check the form elements
        form = EmailMaintenanceForm(request.POST)

        if form.is_valid():
            # Obtain the cleaned data
            id = form.cleaned_data['id']

            # Obtain the email address id
            recipient_id = Maintenance.objects.filter(id=id).values('email_address_id')[0]['email_address_id']

            # If there is no recipient defined, give them an error
            if not recipient_id:
                return system_message(request,True,'There is no recipient defined for this maintenance.  Please go back and add one.')

            if int(cv.value('notify')) == 1:
                email = notify.email()
                email_status = email.maintenance(id,recipient_id,set_timezone,False)

                if email_status == 'success':
                    return system_message(request,False,'Email successfully sent')
                else:
                    return system_message(request,True,'Email failed: %s' % email_status)
            else:
                return system_message(request,True,'Email functionality is disabled')
       
    # Not a POST or a failed form submit
    else:
        return system_message(request,True,'Invalid request - please go back and try again.')


@login_required
@staff_member_required
def m_delete(request):
    """Delete Maintenance Page

    Delete a maintenance given an id

    """

    # We only accept posts
    if request.method == 'POST':
        
        # Check the form elements
        form = DeleteEventForm(request.POST)

        if form.is_valid():

            # Obtain the cleaned data
            id = form.cleaned_data['id']

            # Delete the incident
            Maintenance.objects.filter(id=id).delete()

            # Redirect to the homepage
            return HttpResponseRedirect('/')

    # If processing got this far, its either not a POST
    # or its an invalid form submit.  Either way, give an error        
    return system_message(request,True,'Invalid delete request')

    
   