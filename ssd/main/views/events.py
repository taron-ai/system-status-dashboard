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
from ssd.main.models import Event
from ssd.main.models import Event_Description
from ssd.main.models import Event_Service
from ssd.main.models import Event_Status
from ssd.main.models import Event_Time
from ssd.main.models import Event_User
from ssd.main.models import Event_Update
from ssd.main.models import Event_Email
from ssd.main.models import Event_Impact
from ssd.main.models import Event_Coordinator
from ssd.main.models import Report
from ssd.main.models import Service
from ssd.main.models import Email
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
            email_id = form.cleaned_data['email_id']

            # Get the user's ID
            user_id = User.objects.filter(username=request.user.username).values('id')[0]['id']

            # Create a datetime object and add the timezone
            # Put the date and time together
            incident_time = datetime.datetime.combine(date,time)

            # Set the timezone
            tz = pytz.timezone(set_timezone)
            incident_time = tz.localize(incident_time)

            # Add the incident and services

            # Create the event and obtain the ID                                     
            e = Event.objects.create(type_id=1)
            event_id = e.pk
            
            # Save the description
            Event_Description(event_id=event_id,description=detail).save()

            # Save the status
            Event_Status(event_id=event_id,status=1).save()

            # Save the start time
            Event_Time(event_id=event_id,start=incident_time).save()

            # Add the user
            Event_User(event_id=event_id,user_id=user_id).save()

            # Add the email recipient, if requested.
            # Form validation ensures that a valid email is selected if broadcast is selected.  
            if broadcast: 
                Event_Email(event_id=event_id,email_id=email_id).save()

            # Find out which services this impacts and associate the services with the event
            # Form validation confirms that there is at least 1
            for service_id in affected_svcs:
                # Should be number only -- can't figure out how to validate
                # multiple checkboxes in the form
                if re.match(r'^\d+$', service_id):
                    Event_Service(service_id=service_id,event_id=event_id).save()

            # Send an email notification to the appropriate list about this issue if requested.  Broadcast won't be
            # allowed to be true if an email address is not defined.
            # Don't send an email if notifications are disabled
            if int(cv.value('notify')) == 1:
                if broadcast:
                    email = notify.email()
                    email.incident(event_id,email_id,set_timezone,True)

            # Send them to the incident detail page for this newly created
            # incident
            return HttpResponseRedirect('/i_detail?id=%s' % event_id)

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
    emails = Email.objects.values('id','email')

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
          'emails':emails,
          'affected_svcs':tuple(affected_svcs),
          'form':form,
          'time_now':time_now,
          'help':help,
          'notifications':notifications,
          'instr_incident_description':instr_incident_description,
          'breadcrumbs':{'Admin':'/admin','Log Incident':'incident'}

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
            id = form.cleaned_data['id']
            update = form.cleaned_data['update']
            broadcast = form.cleaned_data['broadcast']
            email_id = form.cleaned_data['email_id']
            closed = form.cleaned_data['closed']

            # Get the user's ID
            user_id = User.objects.filter(username=request.user.username).values('id')[0]['id']

            # Add the update
            # Obtain the time and add a timezone
            # Create a datetime object for right now
            time_now = datetime.datetime.now()
            # Add the server's timezone (whatever DJango is set to)
            time_now = pytz.timezone(settings.TIME_ZONE).localize(time_now)
            # Add it
            Event_Update(event_id=id,date=time_now,update=update,user_id=user_id).save()

            # Add the email recipient.  If an email recipient is missing, then the broadcast email will not be checked.
            # In both cases, delete the existing email (because it will be re-added)
            Event_Email.objects.filter(event_id=id).delete()
            if broadcast: 
                Event_Email(event_id=id,email_id=email_id).save()

            # See if we are adding or subtracting services
            # The easiest thing to do here is remove all affected  
            # services and re-add the ones indicated here

            # Remove first
            Event_Service.objects.filter(event_id=id).delete()
    
            # Now add (form validation confirms that there is at least 1)
            for service_id in affected_svcs:
                # Should be number only -- can't figure out how to validate
                # multiple checkboxes in the form
                if re.match(r'^\d+$', service_id):
                    Event_Service(event_id=id,service_id=service_id).save()

            # See if we are closing this issue 
            if closed:
                # If it was already closed, then don't re-close it because it will update the closed time
                if not Event_Status.objects.filter(event_id=id).values('status')[0]['status'] == 2:
                    Event_Status.objects.filter(event_id=id).update(status=2)
            else:
                Event_Status.objects.filter(event_id=id).update(status=1)

            # Send an email notification to the appropriate list about this issue if requested.  Broadcast won't be
            # allowed to be true if an email address is not defined.
            # Don't send an email if notifications are disabled
            if int(cv.value('notify')) == 1:
                if broadcast:
                    email = notify.email()
                    email.incident(id,email_id,set_timezone,False)
            
                # If broadcast is not selected, turn off emails
                else:
                    Event_Email.objects.filter(event_id=id).delete()


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
        affected_svcs_tmp = Event.objects.filter(id=id).values('event_service__service_id')
        affected_svcs = []
        for service_id in affected_svcs_tmp:
            affected_svcs.append(service_id['event_service__service_id'])
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

    # Obtain the details
    details = Event.objects.filter(id=id).values('event_status__status','event_email__email_id')

    # Obtain all services
    services = Service.objects.values('id','service_name').order_by('service_name')

    # Obtain all current email addresses
    emails = Email.objects.values('id','email')

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
          'emails':emails,
          'notifications':notifications,
          'time_now':time_now,
          'instr_incident_update':instr_incident_update
       },
       context_instance=RequestContext(request)
    )


@login_required
@staff_member_required
def delete(request):
    """Delete Incident Page

    Delete an event given an id

    """

    # We only accept posts
    if request.method == 'POST':
        
        # Check the form elements
        form = DeleteEventForm(request.POST)

        if form.is_valid():

            # Obtain the cleaned data
            id = form.cleaned_data['id']

            # Delete the incident
            Event.objects.filter(id=id).delete()

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
            email_id = form.cleaned_data['email_id']
                        
            # Combine the dates and times into datetime objects
            start = datetime.datetime.combine(s_date, s_time)
            end = datetime.datetime.combine(e_date, e_time)

            # Set the timezone
            tz = pytz.timezone(set_timezone)
            start = tz.localize(start)
            end = tz.localize(end)
            
            # Get the user's ID
            user_id = User.objects.filter(username=request.user.username).values('id')[0]['id']

            # Create the event and obtain the ID                                     
            e = Event.objects.create(type_id=2)
            event_id = e.pk
            
            # Save the description
            Event_Description(event_id=event_id,description=description).save()

            # Save the impact analysis
            Event_Impact(event_id=event_id,impact=impact).save()

            # Save the coordinator
            Event_Coordinator(event_id=event_id,coordinator=coordinator).save()

            # Save the status
            # Initially, the status will be inactive (not started and not completed)
            Event_Status(event_id=event_id,status=0).save()

            # Save the start time
            Event_Time(event_id=event_id,start=start,end=end).save()

            # Add the user
            Event_User(event_id=event_id,user_id=user_id).save()

            # Add the email recipient, if requested.
            # Form validation ensures that a valid email is selected if broadcast is selected.  
            if broadcast: 
                Event_Email(event_id=event_id,email_id=email_id).save()

            # Find out which services this impacts and associate the services with the event
            # Form validation confirms that there is at least 1
            for service_id in affected_svcs:
                # Should be number only -- can't figure out how to validate
                # multiple checkboxes in the form
                if re.match(r'^\d+$', service_id):
                    Event_Service(service_id=service_id,event_id=event_id).save()

            # Send an email notification to the appropriate list about this issue if requested.  Broadcast won't be
            # allowed to be true if an email address is not defined.
            # Don't send an email if notifications are disabled
            if int(cv.value('notify')) == 1:
                if broadcast:
                    email = notify.email()
                    email.maintenance(event_id,email_id,set_timezone,True)

            # Send them to the incident detail page for this newly created
            # maintenance
            return HttpResponseRedirect('/m_detail?id=%s' % event_id)

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
    emails = Email.objects.values('id','email')

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
          'emails':emails,
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
            id = form.cleaned_data['id']
            s_date = form.cleaned_data['s_date']
            s_time = form.cleaned_data['s_time']
            e_date = form.cleaned_data['e_date']
            e_time = form.cleaned_data['e_time']
            description = form.cleaned_data['description']
            impact = form.cleaned_data['impact']
            coordinator = form.cleaned_data['coordinator']
            update = form.cleaned_data['update']
            broadcast = form.cleaned_data['broadcast']
            email_id = form.cleaned_data['email_id']

            # Combine the dates and times into datetime objects
            start = datetime.datetime.combine(s_date, s_time)
            end = datetime.datetime.combine(e_date, e_time)

            # Set the timezone
            tz = pytz.timezone(set_timezone)
            start = tz.localize(start)
            end = tz.localize(end)

            # Get the user's ID
            user_id = User.objects.filter(username=request.user.username).values('id')[0]['id']

            # Update the description
            Event_Description.objects.filter(event_id=id).update(description=description)

            # Update the impact analysis
            Event_Impact.objects.filter(event_id=id).update(impact=impact)

            # Update the coordinator
            Event_Coordinator.objects.filter(event_id=id).update(coordinator=coordinator)

            # Update the status
            Event_Status.objects.filter(event_id=id).update(status=0)

            # Update the start/end times
            Event_Time.objects.filter(event_id=id).update(start=start,end=end)

            # Add the update
            # Obtain the time and add a timezone
            # Create a datetime object for right now
            time_now = datetime.datetime.now()
            # Add the server's timezone (whatever DJango is set to)
            time_now = pytz.timezone(settings.TIME_ZONE).localize(time_now)
            # Add it
            Event_Update(event_id=id,date=time_now,update=update,user_id=user_id).save()

            # Add the email recipient.  If an email recipient is missing, then the broadcast email will not be checked.
            # In both cases, delete the existing email (because it will be re-added)
            Event_Email.objects.filter(event_id=id).delete()
            if broadcast: 
                Event_Email(event_id=id,email_id=email_id).save()

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
            Event_Service.objects.filter(event_id=id).delete()
    
            # Now add (form validation confirms that there is at least 1)
            for service_id in affected_svcs:
                # Should be number only -- can't figure out how to validate
                # multiple checkboxes in the form
                if re.match(r'^\d+$', service_id):
                    Event_Service(event_id=id,service_id=service_id).save()
      
            
            # Send an email notification to the appropriate list about this issue if requested.  Broadcast won't be
            # allowed to be true if an email address is not defined.
            # Don't send an email if notifications are disabled
            if int(cv.value('notify')) == 1:
                if broadcast:
                    email = notify.email()
                    email.maintenance(event_id,email_id,set_timezone,True)

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
        affected_svcs_tmp = Event.objects.filter(id=id).values('event_service__service_id')
        affected_svcs = []
        for service_id in affected_svcs_tmp:
            affected_svcs.append(service_id['event_service__service_id'])
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

    # Obtain the details
    # Obain the incident detail
    details = Event.objects.filter(id=id).values(
                                                'event_time__start',
                                                'event_time__end',
                                                'event_status__status',
                                                'event_description__description',
                                                'event_impact__impact',
                                                'event_coordinator__coordinator',
                                                'event_email__email__email',
                                                'event_user__user__first_name',
                                                'event_user__user__last_name'
                                                )

    # Obtain all current email addresses
    emails = Email.objects.values('id','email')

    # Obtain all services
    services = Service.objects.values('id','service_name').order_by('service_name')

    start = details[0]['event_time__start']
    end = details[0]['event_time__end']

    # Set the timezone
    start = start.astimezone(pytz.timezone(set_timezone))
    end = end.astimezone(pytz.timezone(set_timezone))
    
    # Format the start/end date/time
    s_date = start.strftime("%Y-%m-%d")   
    s_time = start.strftime("%H:%M")
    e_date = end.strftime("%Y-%m-%d")
    e_time = end.strftime("%H:%M")

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
          'start':start,
          'end':end,
          's_date':s_date,
          's_time':s_time,
          'e_date':e_date,
          'e_time':e_time,
          'emails':emails,
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

   
   