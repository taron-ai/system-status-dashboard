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
from ssd.main.models import Service_Maintenance
from ssd.main.forms import AddIncidentForm
from ssd.main.forms import UpdateIncidentForm
from ssd.main.forms import UpdateMaintenanceForm
from ssd.main.forms import ReportIncidentForm
from ssd.main.forms import SearchForm
from ssd.main.forms import AddMaintenanceForm
from ssd.main import notify
from ssd.main import config_value

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

    # Instantiate the configuration value getter
    cv = config_value.config_value()

    # If this functionality is disabled in the admin, let the user know
    if int(cv.value('report_incident_display')) == 0:
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
                       description=description,
                       additional=additional,
                       screenshot1=screenshot1,
                       screenshot2=screenshot2,
                      ).save()
            except Exception as e:
                return return_error(request,e)

            # If notifications are turned on, report the issue to the pager address
            # and save the return value for the confirmation page
            # If notifications are turned off, give the user a positive confirmation
            
            if int(cv.value('logo_display')) == 1:
                pager = notify.email()
                pager_status = pager.page(description)
            else:
                pager_status = 'success'

            # Give them a confirmation page
            message_success = cv.value('message_success')
            message_error = cv.value('message_error')

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

    # Determine if we are showing the create maintenance help message
    if int(cv.value('display_report_incident_instr')):
        instr = cv.value('instr_report_incident')
    else:
        instr = None
    
    return render_to_response(
       'main/report.html',
       {
          'title':'SSD Report Incident',
          'form':form,
          'instr':instr,
          'enable_uploads':int(cv.value('enable_uploads'))
       },
       context_instance=RequestContext(request)
    )


def index(request):
    """Index Page View

    Show the calendar view with 7 days of information on all services

    """
    
    # Instantiate the configuration value getter
    cv = config_value.config_value()
    
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

    # See if we have any open incidents or maintenances
    # Any open incidents will turn the service red on the
    # dashboard, regardless of date and the specific date marker
    # will be red or orange, depending on the open/closed state
    # of the incident.
    #
    # These will be lookup tables for the template
    active_incidents = Service_Issue.objects.filter(incident__closed__isnull=True).values('service_name_id__service_name')
    active_maintenances = Service_Maintenance.objects.filter(maintenance__started=1,maintenance__completed=0).values('service_name_id__service_name')
    
    # Rewrite this so its quickly searchable by the template
    impaired_services = {}
    for name in active_incidents:
        impaired_services[name['service_name_id__service_name']] = ''

    # Rewrite this so its quickly searchable by the template
    maintenance_services = {}
    for name in active_maintenances:
        maintenance_services[name['service_name_id__service_name']] = ''

    # We'll print 7 days of dates at any time
    # Construct a dictionary like this to pass to the template
    # [
    #  [service][2012-10-11][2012-10-12],
    #  [www.domain.com,['green'],['green']],
    #  [www.domain1.com,['green'],[{'open':,'closed':,'type':,'id':}]]
    # ]

    # Put together the first row, which are the headings
    data = []
    data.append(headings)
    services = Service.objects.values('service_name').order_by('service_name')
    incidents = Service_Issue.objects.filter(incident__date__range=[dates[0],ref_q]).values('incident__date',
                                                                                            'incident_id',
                                                                                            'service_name_id__service_name',
                                                                                            'incident__closed')

    maintenances = Service_Maintenance.objects.filter(maintenance__start__range=[dates[0],ref_q]).values('maintenance__start',
                                                                                                         'maintenance__end',
                                                                                                         'maintenance_id',
                                                                                                         'service_name_id__service_name',
                                                                                                         'maintenance__started',
                                                                                                         'maintenance__completed')

    # Run through each service and see if it had an incident during the time range
    for service in services:
        # Make a row for this service
        row = []
        row.append(service['service_name'])

        # Run through each date for each service
        for date in dates:

            # If there is a match, append it, otherwise leave blank
            match = False

            # Check each incident and maintenance to see if there is a match
            # There could be more than one incident per day
            row_incident = []

            # First the incidents
            for incident in incidents:
                if service['service_name'] == incident['service_name_id__service_name']:

                    # This incident affected our service
                    # Convert to the requested timezone
                    incident_date = incident['incident__date']
                    incident_date = incident_date.astimezone(pytz.timezone(set_timezone))

                    # If the incident closed date is there, make sure the time zone is correct
                    closed_date = incident['incident__closed']
                    if incident['incident__closed']:
                        closed_date = closed_date.astimezone(pytz.timezone(set_timezone))

                    if date.date() == incident_date.date():
                        # This is our date so add the incident ID
                        match = True
                        event = {
                                 'type':'incident',
                                 'id':incident['incident_id'],
                                 'open':incident_date,
                                 'closed':closed_date
                                 }
                        row_incident.append(event)
            
            # Now the maintenance
            for maint in maintenances:
                if service['service_name'] == maint['service_name_id__service_name']:

                    # This maintenance affected our service
                    # Convert to the requested timezone
                    start_date = maint['maintenance__start']
                    start_date = start_date.astimezone(pytz.timezone(set_timezone))
                    
                    # Convert the closed date to our timezone
                    closed_date = maint['maintenance__end']
                    closed_date = closed_date.astimezone(pytz.timezone(set_timezone))

                    if date.date() == start_date.date():
                        # This is our date so add the incident ID
                        match = True
                        event = {
                                 'type':'maintenance',
                                 'id':maint['maintenance_id'],
                                 'open':start_date,
                                 'closed':closed_date
                                 }
                        row_incident.append(event)

            if match == False:
                row_incident.append('green')

            # Add the incident row to the main row
            row.append(row_incident)

        # Add the main row to our data dict
        data.append(row)
  
    # Obtain the alert text (if there)
    if int(cv.value('display_alert')):
        alert = cv.value('alert')
    else:
        alert = None
    
    # Obtain all timezones
    timezones = pytz.all_timezones

    # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
    jtz.activate(set_timezone)

    print data
    # Print the page
    return render_to_response(
       'main/index.html',
       {
          'title':'System Status Dashboard | Home',
          'data':data,
          'impaired_services':impaired_services,
          'maintenance_services':maintenance_services,
          'backward_link':backward_link,
          'forward_link':forward_link,
          'alert':alert,
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


def m_detail(request):
    """Maintenance Detail View

    Show all available information on a scheduled maintenance

    """

    try:
        # Obtain the query parameters
        id = request.GET['id']
    except KeyError, e:
        return return_error(request,e)

    # Ensure the id is well formed
    if not re.match(r'^\d+$', request.GET['id']):
        return return_error(request,'Improperly formatted id: %s' % (request.GET['id']))


    # Obain the incident detail
    detail = Maintenance.objects.filter(id=id).values('start','end','description','impact','coordinator','started','completed')

    # Which services were impacted
    services = Service_Maintenance.objects.filter(maintenance_id=id).values('service_name_id__service_name')

    # Obain any incident updates
    updates = Maintenance_Update.objects.filter(maintenance_id=id).values(
                                                                          'id',
                                                                          'date',
                                                                          'user_id__first_name',
                                                                          'user_id__last_name',
                                                                          'detail'
                                                                         ).order_by('id')


    # See if the timezone is set, if not, give them the server timezone
    if request.COOKIES.get('timezone') == None:
        set_timezone = settings.TIME_ZONE
    else:
        set_timezone = request.COOKIES.get('timezone')

    # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
    jtz.activate(set_timezone)

    # Print the page
    return render_to_response(
       'main/m_detail.html',
       {
          'title':'System Status Dashboard | Scheduled Maintenance Detail',
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
                email.incident(request.POST['id'],set_timezone,False)

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
            else:
                Incident.objects.filter(id=id).update(closed=None)

            # If an email update is being requested, send it
            if 'email' in request.POST:
                email = notify.email()
                email.incident(request.POST['id'],set_timezone,False)

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
def m_update(request):
    """Update Maintenance Page

    Accept input to update the scheduled maintenance

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
                print 'deleting %s' % request.POST['id']
                # Delete it (deletes will be cascaded)
                Maintenance.objects.filter(id=request.POST['id']).delete()

                # Redirect to the home page
                return HttpResponseRedirect('/')

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
            id = form.cleaned_data['id']
            
            # Check if we are starting/completing
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

            # Get the user's ID
            user_id = User.objects.filter(username=request.user.username).values('id')[0]['id']

            # If there is an update, add it
            if update:
                Maintenance_Update(maintenance_id=id,user_id=user_id,detail=update).save()

            # Update the core maintenance parameters
            # Combine the dates and times into datetime objects
            start = datetime.datetime.combine(s_date, s_time)
            end = datetime.datetime.combine(e_date, e_time)

            # Set the timezone
            tz = pytz.timezone(set_timezone)
            start = tz.localize(start)
            end = tz.localize(end)
            
            Maintenance.objects.filter(id=id).update(
                                                     start=start,
                                                     end=end,
                                                     description=description,
                                                     impact=impact,
                                                     coordinator=coordinator,
                                                     started=started,
                                                     completed=completed
                                                    )

            # If an email update is being requested, send it
            if 'email' in request.POST:
                email = notify.email()
                email.maintenance(request.POST['id'],set_timezone,False)

            # All done so redirect to the maintenance detail page so
            # the new data can be seen.
            return HttpResponseRedirect('/m_detail?id=%s' % id)
    
        else:
            print 'Invalid form: UpdateMaintenanceForm: %s' % form.errors

    # Not a POST so create a blank form
    else:
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
        return return_error(request,'No incident ID given')

    # Make sure the ID is properly formed
    if not re.match(r'^\d+$', id):
        return return_error(request,'Improperly formatted ID: %s' % id)

    # See if the maintenance is completed
    status = Maintenance.objects.filter(id=id).values('started','completed')

    # Obtain all services
    services = Service.objects.values('id','service_name').order_by('service_name')

    # Obtain all services that this maintenance impacts
    a_services = Service_Maintenance.objects.filter(maintenance_id=id).values('service_name_id')

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

    # Obtain the details of this maintenance
    details = Maintenance.objects.filter(id=id).values('start','end','description','impact','coordinator','started','completed')

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

    # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
    jtz.activate(set_timezone)

    # Print the page
    return render_to_response(
       'main/m_update.html',
       {
          'title':'System Status Dashboard | Scheduled Maintenance Update',
          'details':details,
          'affected_services':affected_services,
          'id':id,
          'form':form,
          'status':status,
          's_date':s_date,
          's_time':s_time,
          'e_date':e_date,
          'e_time':e_time
       },
       context_instance=RequestContext(request)
    )


@login_required
@staff_member_required
def create(request):
    """Update Incident Page

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
                email.incident(incident_id[0]['id'],set_timezone,True)

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

    # Determine if we are showing the create incident help message
    if int(cv.value('display_create_incident_instr')):
        instr = cv.value('instr_create_incident')
    else:
        instr = None

    # Print the page
    return render_to_response(
       'main/create.html',
       {
          'title':'System Status Dashboard | Create Issue',
          'services':services,
          'form':form,
          'time_now':time_now,
          'instr':instr
       },
       context_instance=RequestContext(request)
    )


def escalation(request):
    """Escalation page

    Print an escalation page should a user want additional information
    on who to contact when incidents occur

    """

    # Instantiate the configuration value getter
    cv = config_value.config_value()

    # If this functionality is disabled in the admin, let the user know
    if int(cv.value('contacts_display')) == 0:
        return return_error(request,'Your system administrator has disabled this functionality')

    # Obtain the escalation message
    escalation = cv.value('escalation')
    
    # Print the page
    return render_to_response(
       'main/escalation.html',
       {
          'title':'SSD Escalation Path',
          'escalation':escalation
       },
       context_instance=RequestContext(request)
    )


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
            maintenance_id = Maintenance.objects.filter(
                                                        start=start,
                                                        end=end,
                                                        description=description,
                                                        impact=impact,
                                                        coordinator=coordinator,
                                                        user_id=user_id,
                                                        completed=0
                                                       ).values('id')
            if not maintenance_id:
                Maintenance(
                            start=start,
                            end=end,
                            description=description,
                            impact=impact,
                            coordinator=coordinator,
                            user_id=user_id,
                            completed=0,
                           ).save()

                maintenance_id = Maintenance.objects.filter(
                                                            start=start,
                                                            end=end,
                                                            description=description,
                                                            impact=impact,
                                                            coordinator=coordinator,
                                                            user_id=user_id,
                                                            completed=0
                                                           ).values('id')[0]['id']

                # Find out which services this impacts and save the data
                # Form validation confirms that there is at least 1
                for service_id in request.POST.getlist('service'):
                    # Should be number only -- can't figure out how to validate
                    # multiple checkboxes in the form
                    if re.match(r'^\d+$', service_id):
                        Service_Maintenance(service_name_id=service_id,maintenance_id=maintenance_id).save()

            # Send an email notification to the appropriate list
            # about this maintenance, if requested
            if 'email' in request.POST:
                email = notify.email()
                email.maintenance(maintenance_id,set_timezone,True)

            # Send them to the incident detail page for this newly created
            # maintenance
            return HttpResponseRedirect('/m_detail?id=%s' % maintenance_id)

        # Invalid Form
        else:
            print 'Invalid Form: AddMaintenanceForm'

    # Not a POST so create a blank form
    else:
        form = AddMaintenanceForm() 
    
    # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
    jtz.activate(set_timezone)
    
    # Obtain all services
    services = Service.objects.values('id','service_name').order_by('service_name')
    
    # Determine if we are showing the create maintenance help message
    if int(cv.value('display_sched_maint_instr')):
        instr = cv.value('instr_sched_maint')
    else:
        instr = None

    # Print the page
    return render_to_response(
       'main/maintenance.html',
       {
          'title':'System Status Dashboard | Scheduled Maintenance',
          'form':form,
          'instr':instr,
          'services':services
       },
       context_instance=RequestContext(request)
    )