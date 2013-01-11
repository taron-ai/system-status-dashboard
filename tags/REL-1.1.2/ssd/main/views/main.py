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


"""This module contains all of the views that are not related
   to search or preferences (basically everything).  As this becomes
   unmanageable, views will be moved to their own modules

"""


import logging
import datetime
import pytz
import re
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone as jtz
from ssd.main.models import Config
from ssd.main.models import Incident
from ssd.main.models import Incident_Update
from ssd.main.models import Report
from ssd.main.models import Service
from ssd.main.models import Service_Issue
from ssd.main.forms import AddIncidentForm
from ssd.main.forms import UpdateIncidentForm
from ssd.main.forms import ReportIncidentForm
from ssd.main.forms import SearchForm
from ssd.main import notify


def return_error(request,error):
    """Error Page

    Return an error page with a helpful error and also write the error to the Apache log

    """

    # Print the error to the Apache log
    print error

    # Create the response object
    response = render_to_response(
     'error/error.html',
      {
        'title':'SSD Error',
        'error':error
      },
      context_instance=RequestContext(request)
    )

    # Give the response back
    return response


def report(request):
    """Report View

    Accept a report from a user of an incident

    """

    # If this functionality is disabled in the admin, let the user know
    if hasattr(settings, 'REPORT_INCIDENT'):
        if not settings.REPORT_INCIDENT == True:
            return return_error(request,'Your system administrator has disabled this functionality')

    # If this is a POST, then check the input params and perform the
    # action, otherwise print the index page
    if request.method == 'POST':
        # Check the form elements
        form = ReportIncidentForm(request.POST, request.FILES)

        if form.is_valid():
            # Obtain the cleaned data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            description = form.cleaned_data['description']
            additional = form.cleaned_data['additional']

            # Create a datetime object for right now
            report_time = datetime.datetime.now()

            # Add the server's timezone (whatever DJango is set to)
            report_time = pytz.timezone(settings.TIME_ZONE).localize(report_time)

            # Save the data

            if 'screenshot1' in request.FILES:
                screenshot1 = request.FILES['screenshot1']
            else:
                screenshot1 = ''

            if 'screenshot2' in request.FILES:
                screenshot2 = request.FILES['screenshot2']
            else:
                screenshot2 = ''

            Report(date=report_time,
                   name=name,
                   email=email,
                   description=description,
                   additional=additional,
                   screenshot1=screenshot1,
                   screenshot2=screenshot2,
                  ).save()

            # If notifications are turned on, report the issue to the pager 
            # and save the return value for the confirmation page
            # If notifications are turned off, give the user a positive confirmation
            if hasattr(settings, 'NOTIFY'):
                if settings.NOTIFY == True:
                    pager = notify.email()
                    pager_status = pager.page(description)
                else:
                    pager_status = 'success'
            else:
                pager_status = 'success'

            # Give them a confirmation page
            message_success = Config.objects.filter(config_name='message_success').values('config_value')[0]['config_value']
            message_error = Config.objects.filter(config_name='message_error').values('config_value')[0]['config_value']

            # Print the page
            return render_to_response(
                'main/confirmation.html',
                {
                   'title':'SSD Report Confirmation ',
                   'pager_status':pager_status,
                   'message_success':message_success,
                   'message_error':message_error
                },
                context_instance=RequestContext(request)
             )

    # Ok, its a GET or an invalid form so create a blank form
    else:
        form = ReportIncidentForm()

    # Print the page
    # On a POST, the form will give back error values for printing in the template

    # Obtain the report incident help message
    report_incident_help = Config.objects.filter(config_name='report_incident_help').values('config_value')[0]['config_value']

    return render_to_response(
       'main/report.html',
       {
          'title':'SSD Report Incident',
          'form':form,
          'report_incident_help':report_incident_help
       },
       context_instance=RequestContext(request)
    )


def index(request):
    """Index Page View

    Show the calendar view with 7 days of information on all services

    """

    # See if the timezone is set, if not, give them the server timezone
    if request.COOKIES.get('timezone') == None:
        set_timezone = settings.TIME_ZONE
    else:
        set_timezone = request.COOKIES.get('timezone')

    # Get the reference date (if its not given, then its today)
    try:
        ref = request.GET['ref']
    # Not there, so set it
    except KeyError:
        # Create a datetime object for right now
        ref = datetime.datetime.now()

        # Add the server's timezone (whatever DJango is set to)
        ref = pytz.timezone(settings.TIME_ZONE).localize(ref)

        # Now convert to the requested timezone
        ref = ref.astimezone(pytz.timezone(set_timezone))

        # Format for just the year, month, day.  We'll add the entire day later
        ref = ref.strftime("%Y-%m-%d")

    # The reference date we use in the query to find relevant incidents
    # is different than the reference date we use for the calendar
    # because the query needs to go through 23:59:59
    ref_q = ref + ' 23:59:59'
    ref_q = datetime.datetime.strptime(ref_q,'%Y-%m-%d %H:%M:%S') 
    ref_q = pytz.timezone(set_timezone).localize(ref_q)

    # The reference date is the last date displayed in the calendar
    # so add that and create a datetime object in the user's timezone
    # (hopefully they set it)
    ref += ' 00:00:00'
    ref = datetime.datetime.strptime(ref,'%Y-%m-%d %H:%M:%S') 
    ref = pytz.timezone(set_timezone).localize(ref)

    # Obtain the current 7 days
    dates = []
    headings = ['Current Status']
    # Subtract successive days (the reference date is the first day)
    for i in [6,5,4,3,2,1]:
       delta = ref - datetime.timedelta(days=i)

       # Add each date
       dates.append(delta)
       headings.append(delta)
 
    # Add the ref date
    dates.append(ref)
    headings.append(ref)

    # The forward and back buttons will be -7 (back) and +7 (forward)
    backward = (ref - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    backward_link = '/?ref=%s' % (backward)
    forward = (ref + datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    forward_link = '/?ref=%s' % (forward)

    # See if we have any open incidents
    # Any open incidents will turn the service red on the
    # dashboard, regardless of date and the specific date marker
    # will be red or orange, depending on the open/closed state
    # of the incident.
    #
    # These will be lookup tables for the template
    active_incidents = Service_Issue.objects.filter(incident__closed__isnull=True).values('service_name_id__service_name')

    # Rewrite this so its quickly searchable by the template
    impaired_services = {}
    for name in active_incidents:
        impaired_services[name['service_name_id__service_name']] = ''

    # We'll print 7 days of dates at any time
    # Construct a dictionary like this to pass to the template
    # [
    #  [service][2012-10-11][2012-10-12],
    #  [www.domain.com][color or ID],
    #  [www.domain1.com][color or ID]
    # ]
    #
    # and also a lookup table of incidents and if they are closed or not
    # like this:
    # {
    #   'id':{'open':date,'closed':date}
    # }
    incident_status = {}

    # Put together the first row, which are the headings
    data = []
    data.append(headings)
    services = Service.objects.values('service_name').order_by('service_name')
    incidents = Service_Issue.objects.filter(incident__date__range=[dates[0],ref_q]).values('incident__date',
                                                                                            'incident_id',
                                                                                            'service_name_id__service_name',
                                                                                            'incident__closed')

    # Run through each service and see if it had an incident during the time range
    for service in services:
        # Make a row for this service
        row = []
        row.append(service['service_name'])

        # Run through each date for each service
        for date in dates:

            # If there is a match, append it, otherwise leave blank
            match = False

            # Check each incident to see if there is a match
            # There could be more than one incident per day
            row_incident = []
            for incident in incidents:
                if service['service_name'] == incident['service_name_id__service_name']:

                    # This incident affected our service
                    # Convert to the requested timezone
                    incident_date = incident['incident__date']
                    incident_date = incident_date.astimezone(pytz.timezone(set_timezone))

                    if date.date() == incident_date.date():
                        # This is our date so add the incident ID
                        match = True
                        row_incident.append(incident['incident_id'])
                        # Also add to the open/closed lookup table
                        incident_status[incident['incident_id']] = {'open':incident_date,'closed':incident['incident__closed']}

            if match == False:
                row_incident.append('green')

            # Add the incident row to the main row
            row.append(row_incident)

        # Add the main row to our data dict
        data.append(row)
  
    # Obtain the maintenance text (if there)
    maintenance = Config.objects.filter(config_name='maintenance').values('config_value')[0]['config_value']

    # Obtain all timezones
    timezones = pytz.all_timezones

    # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
    jtz.activate(set_timezone)

    # Print the page
    return render_to_response(
       'main/index.html',
       {
          'title':'SSD Home',
          'data':data,
          'impaired_services':impaired_services,
          'backward_link':backward_link,
          'forward_link':forward_link,
          'incident_status':incident_status,
          'maintenance':maintenance,
          'timezones':timezones
       },
       context_instance=RequestContext(request)
    )


def detail(request):
    """Incident Detail View

    Show all available information on an incident

    """

    try:
        # Obtain the query parameters
        id = request.GET['id']
    except KeyError, e:
        return return_error(request,e)

    # Ensure the id is well formed
    if not re.match(r'^\d+$', request.GET['id']):
        return return_error(request,'Improperly formatted id: %s' % (request.GET['id']))

    # Which services were impacted
    services = Service_Issue.objects.filter(incident_id=id).values('service_name_id__service_name')

    # Obain the incident detail
    detail = Incident.objects.filter(id=id).values('date','closed','detail')

    # Obain any incident updates
    updates = Incident_Update.objects.filter(incident_id=id).values('id','date','detail').order_by('id')


    # See if the timezone is set, if not, give them the server timezone
    if request.COOKIES.get('timezone') == None:
        set_timezone = settings.TIME_ZONE
    else:
        set_timezone = request.COOKIES.get('timezone')

    # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
    jtz.activate(set_timezone)

    # Print the page
    return render_to_response(
       'main/detail.html',
       {
          'title':'SSD Incident',
          'services':services,
          'id':id,
          'detail':detail,
          'updates':updates
       },
       context_instance=RequestContext(request)
    )


@staff_member_required
def update(request):
    """Update Incident Page

    Accept input to update the incident

    """

    # Obtain the timezone (or set to the default DJango server timezone)
    if request.COOKIES.get('timezone') == None:
        set_timezone = settings.TIME_ZONE
    else:
        set_timezone = request.COOKIES.get('timezone')

    # If this is a POST, then validate the form and save the data
    # Some validation must take place manually (deletes and service
    # addition/subtraction
    if request.method == 'POST':
        # If this is a delete request, then no need to check the 
        # rest of the form.  Make sure the ID is well formatted
        if 'delete' in request.POST and 'id' in request.POST:
            if re.match(r'^\d+$', request.POST['id']):
                # Delete it (deletes will be cascaded)
                Incident.objects.filter(id=request.POST['id']).delete()

                # Redirect to the home page
                return HttpResponseRedirect('/')

        # Give the template a blank time if this is a post 
        # the user will have already set it.
        time_now = ''

        # If this is a request to broadcast an email w/o any other
        # options, then do that and send back to home page
        # Don't check the rest of the form
        if 'email' in request.POST and 'id' in request.POST and request.POST['detail'] == '' and not 'close' in request.POST:
            if re.match(r'^\d+$', request.POST['id']):
                email = notify.email()
                email.send(request.POST['id'],settings.SSD_URL,set_timezone,False)

                # Redirect to the home page
                return HttpResponseRedirect('/')

        # Check the form elements
        form = UpdateIncidentForm(request.POST)

        if form.is_valid():
            # Obtain the cleaned data
            date = form.cleaned_data['date']
            detail = form.cleaned_data['detail']
            time = form.cleaned_data['time']
            id = form.cleaned_data['id']

            # Check if we are re-opening this incident (if its closed)
            if not 'close' in form.cleaned_data:
                Incident.objects.filter(id=id).update(closed=None)

            # Create a datetime object and add the user's timezone
            # (hopefully they set it)
            # Put the date and time together
            incident_time = '%s %s' % (date,time)

            # Create a datetime object
            incident_time = datetime.datetime.strptime(incident_time,'%Y-%m-%d %H:%M')

            # Set the timezone
            tz = pytz.timezone(set_timezone)
            incident_time = tz.localize(incident_time)

            # Add the detail text 
            # Don't allow the same detail to be added 2x
            # The user might have hit the back button and submitted again
            detail_id = Incident_Update.objects.filter(date=incident_time,detail=detail).values('id')
            if not detail_id:
                Incident_Update(date=incident_time,incident_id=id,detail=detail).save()

                # See if we are adding or subtracting services
                # The easiest thing to do here is remove all affected  
                # services and re-add the ones indicated here

                # Remove first
                Service_Issue.objects.filter(incident_id=id).delete()
        
                # Now add (form validation confirms that there is at least 1)
                for service_id in request.POST.getlist('service'):
                    # Should be number only -- can't figure out how to validate
                    # multiple checkboxes in the form
                    if re.match(r'^\d+$', service_id):
                        Service_Issue(service_name_id=service_id,incident_id=id).save()

            # See if we are closing this issue
            if 'close' in request.POST:
                Incident.objects.filter(id=id).update(closed=incident_time)

            # If an email update is being requested, send it
            if 'email' in request.POST:
                email = notify.email()
                email.send(request.POST['id'],settings.SSD_URL,set_timezone,False)

            # All done so redirect to the incident detail page so
            # the new data can be seen.
            return HttpResponseRedirect('/detail?id=%s' % id)

    # Not a POST so create a blank form
    else:
        form = UpdateIncidentForm()

        # Obtain the current date/time so we can pre-fill them
        # Create a datetime object for right now
        time_now = datetime.datetime.now()

        # Add the server's timezone (whatever DJango is set to)
        time_now = pytz.timezone(settings.TIME_ZONE).localize(time_now)

        # Now convert to the requested timezone
        time_now = time_now.astimezone(pytz.timezone(set_timezone))

    # Obtain the id (this could have been a GET or a failed POST)
    if request.method == 'GET':
        if 'id' in request.GET:
            id = request.GET['id']
    elif request.method == 'POST':
        if 'id' in request.POST:
            id = request.POST['id']

    # If we don't have the ID, then we have to give them an error
    if not id:
        return return_error(request,'No incident ID given')

    # Make sure the ID is properly formed
    if not re.match(r'^\d+$', id):
        return return_error(request,'Improperly formatted ID: %s' % id)

    # See if the incident is closed
    closed = Incident.objects.filter(id=id).values('closed')

    # Obtain all services
    services = Service.objects.values('id','service_name').order_by('service_name')

    # Obtain all services that this issue impacts
    a_services = Service_Issue.objects.filter(incident_id=id).values('service_name_id')

    # Put together the data in an easy to parse format
    # for the template like this:
    # services[service_id][service_name][affected]
    affected_services = []
    # Look through each service
    for service in services:
        dict = {}
        dict['id'] = service['id']
        dict['name'] = service['service_name']

        # Check each affected service
        for a_service in a_services:
            if service['id'] == a_service['service_name_id']:
                dict['affected'] = 'on'

        # If the service is not affected, set to False
        if not 'affected' in dict:
            dict['affected'] = 'off'

        # Add the dict
        affected_services.append(dict)

    # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
    jtz.activate(set_timezone)

    # Print the page
    return render_to_response(
       'main/update.html',
       {
          'title':'SSD Incident Update',
          'closed':closed,
          'affected_services':affected_services,
          'id':id,
          'form':form,
          'time_now':time_now
       },
       context_instance=RequestContext(request)
    )


@staff_member_required
def create(request):
    """Update Incident Page

    Create a new incident view

    """

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


        # Check the form elements
        form = AddIncidentForm(request.POST)

        if form.is_valid():
            # Obtain the cleaned data
            date = form.cleaned_data['date']
            detail = form.cleaned_data['detail']
            time = form.cleaned_data['time']

            # Create a datetime object and add the timezone
            # Put the date and time together
            incident_time = '%s %s' % (date,time)

            # Create a datetime object
            incident_time = datetime.datetime.strptime(incident_time,'%Y-%m-%d %H:%M')

            # Set the timezone
            tz = pytz.timezone(set_timezone)
            incident_time = tz.localize(incident_time)

            # Add the incident and services
            # Don't allow the same incident to be added 2x
            # The user might have hit the back button and submitted again
            incident_id = Incident.objects.filter(date=incident_time,detail=detail).values('id')
            if not incident_id:
                Incident(date=incident_time,detail=detail).save()
                incident_id = Incident.objects.filter(date=incident_time,detail=detail).values('id')

                # Find out which services this impacts and save the data
                # Form validation confirms that there is at least 1
                for service_id in request.POST.getlist('service'):
                    # Should be number only -- can't figure out how to validate
                    # multiple checkboxes in the form
                    if re.match(r'^\d+$', service_id):
                        Service_Issue(service_name_id=service_id,incident_id=incident_id[0]['id']).save()

            # Send an email notification to the appropriate list
            # about this issue if requested
            if 'email' in request.POST:
                email = notify.email()
                email.send(incident_id[0]['id'],settings.SSD_URL,set_timezone,True)

            # Send them to the incident detail page for this newly created
            # incident
            return HttpResponseRedirect('/detail?id=%s' % incident_id[0]['id'])

    # Not a POST so create a blank form
    else:
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

    # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
    jtz.activate(set_timezone)

    # Obtain the create incident help message
    create_incident_help = Config.objects.filter(config_name='create_incident_help').values('config_value')[0]['config_value']

    # Print the page
    return render_to_response(
       'main/create.html',
       {
          'title':'SSD Create Issue',
          'services':services,
          'form':form,
          'time_now':time_now,
          'create_incident_help':create_incident_help
       },
       context_instance=RequestContext(request)
    )


def escalation(request):
    """Escalation page

    Print an escalation page should a user want additional information
    on who to contact when incidents occur

    """

    # If this functionality is disabled in the admin, let the user know
    if hasattr(settings, 'CONTACTS'):
        if not settings.CONTACTS == True:
            return return_error(request,'Your system administrator has disabled this functionality')

    # Obtain the escalation message
    escalation = Config.objects.filter(config_name='escalation').values('config_value')[0]['config_value']

    # Print the page
    return render_to_response(
       'main/escalation.html',
       {
          'title':'SSD Escalation Path',
          'escalation':escalation
       },
       context_instance=RequestContext(request)
    )
