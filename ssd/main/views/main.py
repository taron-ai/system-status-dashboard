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


import datetime
import pytz
import re
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.utils import timezone as jtz
from ssd.main.models import Incident
from ssd.main.models import Incident_Update
from ssd.main.models import Service
from ssd.main.models import Service_Issue
from ssd.main.models import Maintenance
from ssd.main.models import Maintenance_Update
from ssd.main.models import Service_Maintenance
from ssd.main.models import Escalation
from ssd.main.forms import DetailForm
from ssd.main import notify
from ssd.main import config_value


def system_message(request,status,message):
    """Error Page

    Return a system message
      - confirmation that something has happened
      - an error message
      - on error, write to the Apache log
      - on error, status should be set to True
    """

    # If its an error, print the error to the Apache log
    if status:
        print message

    # Create the response object
    response = render_to_response(
     'events/system_message.html',
      {
        'title':'System Status Dashboard | System Message',
        'status':status,
        'message':message
      },
      context_instance=RequestContext(request)
    )

    # Give the response back
    return response


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
    # (or the server timezone if its not set)
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
                                                                                            'incident__closed').order_by('id')

    maintenances = Service_Maintenance.objects.filter(maintenance__start__range=[dates[0],ref_q]).values('maintenance__start',
                                                                                                         'maintenance__end',
                                                                                                         'maintenance_id',
                                                                                                         'service_name_id__service_name',
                                                                                                         'maintenance__started',
                                                                                                         'maintenance__completed').order_by('id')

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


    # ------------------ #
    # Obtain a count of all incidents/maintenances/reports going back 30 days and forward 30 days (from the reference date) for the summary
    # graph
    
    # First populate all of the dates into an array so we can iterate through 
    graph_dates = []
    
    # The back dates (including today)
    counter = 30
    while counter >= 0:
        day = datetime.timedelta(days=counter)
        day = ref - day
        day = day.strftime("%Y-%m-%d")
        graph_dates.append(day)
        counter -= 1

    # Now the forward dates
    counter = 1
    while counter <= 30:
        day = datetime.timedelta(days=counter)
        day = ref + day
        day = day.strftime("%Y-%m-%d")
        graph_dates.append(day)
        counter += 1


    # Obtain the back and forward dates for the query    
    back = datetime.timedelta(days=30)
    back_date = ref - back
    forward = datetime.timedelta(days=30)
    forward_date = ref_q + forward
    
    # Obtain a count of incidents, per day
    incident_count = Incident.objects.filter(date__range=[back_date,forward_date]).values('date')
    
    # Obtain a count of maintenances, per day
    maintenance_count = Maintenance.objects.filter(start__range=[back_date,forward_date]).values('start')

    # Iterate through the graph_dates and find matching incidents/maintenances/reports
    # This data structure will look like this:
    # count_data = [
    #               {'date' : '2013-09-01', 'incidents':0, 'maintenances':0, 'reports':1}
    #              ]
    count_data = []

    for day in graph_dates:

        # Create a tuple to hold this data series
        t = {'date':day, 'incidents':0, 'maintenances':0, 'reports':0}

        # Check for incidents that match this date
        for row in incident_count:
            if row['date'].astimezone(pytz.timezone(set_timezone)).strftime("%Y-%m-%d") == day:
                t['incidents'] += 1

        # Check for maintenances that match this date
        for row in maintenance_count:
            if row['start'].astimezone(pytz.timezone(set_timezone)).strftime("%Y-%m-%d") == day:
                t['maintenances'] += 1

        # Add the tuple
        count_data.append(t)
    # ------------------ #


    # Obtain the alert text (if it's being shown)
    if int(cv.value('display_alert')):
        alert = cv.value('alert')
    else:
        alert = None

    # Obtain the information text
    information = cv.value('information_main')

    # Obtain all timezones
    timezones = pytz.all_timezones

    # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
    jtz.activate(set_timezone)

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
          'information':information,
          'count_data':count_data,
          'timezones':timezones
       },
       context_instance=RequestContext(request)
    )


def i_detail(request):
    """Incident Detail View

    Show all available information on an incident

    """

    form = DetailForm(request.GET)

    if form.is_valid():
        # Obtain the cleaned data
        id = form.cleaned_data['id']

    # Bad form
    else:
        return system_message(request,True,'Improperly formatted id: %s' % (request.GET['id']))

    # Instantiate the configuration value getter
    cv = config_value.config_value()

    # Which services were impacted
    services = Service_Issue.objects.filter(incident_id=id).values('service_name_id__service_name')

    # Obain the incident detail
    detail = Incident.objects.filter(id=id).values('date','closed','detail','email_address_id__email_address','user_id__first_name','user_id__last_name')

    # Obain any incident updates
    updates = Incident_Update.objects.filter(incident_id=id).values('id','date','detail','user_id__first_name','user_id__last_name').order_by('id')


    # See if the timezone is set, if not, give them the server timezone
    if request.COOKIES.get('timezone') == None:
        set_timezone = settings.TIME_ZONE
    else:
        set_timezone = request.COOKIES.get('timezone')

    # See if email notifications are enabled
    notifications = int(cv.value('notify'))

    # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
    jtz.activate(set_timezone)

    # Print the page
    return render_to_response(
       'main/i_detail.html',
       {
          'title':'System Status Dashboard | Incident Detail',
          'services':services,
          'id':id,
          'detail':detail,
          'updates':updates,
          'notifications':notifications
       },
       context_instance=RequestContext(request)
    )


def m_detail(request):
    """Maintenance Detail View

    Show all available information on a scheduled maintenance

    """

    form = DetailForm(request.GET)

    if form.is_valid():
        # Obtain the cleaned data
        id = form.cleaned_data['id']

    # Bad form
    else:
        return system_message(request,True,'Improperly formatted id: %s' % (request.GET['id']))

    # Instantiate the configuration value getter
    cv = config_value.config_value()

    # Obain the incident detail
    detail = Maintenance.objects.filter(id=id).values('start','end','description','impact','coordinator','started','completed','email_address_id__email_address')

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

    # See if email notifications are enabled
    notifications = int(cv.value('notify'))

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
          'updates':updates,
          'notifications':notifications
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
    if int(cv.value('escalation_display')) == 0:
        return system_message(request,True,'Your system administrator has disabled this functionality')

    # Obtain the escalation contacts
    contacts = Escalation.objects.filter(hidden=False).values('id','name','contact_details').order_by('order')

    # Help message
    help = cv.value('help_escalation')

    # Print the page
    return render_to_response(
       'main/escalation.html',
       {
          'title':'System Status Dashboard | Escalation Path',
          'contacts':contacts,
          'help':help
       },
       context_instance=RequestContext(request)
    )




    
   