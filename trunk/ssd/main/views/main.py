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
from django.utils import timezone as jtz
from ssd.main.models import Event
from ssd.main.models import Service
from ssd.main import notify
from ssd.main import config_value


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

    # We'll print 7 days of dates at any time
    # Construct a dictionary like this to pass to the template
    # [
    #  [service][2012-10-11][2012-10-12],
    #  [{service:www.domain.com,status:1},['green'],['green']],
    #  [{service:www.domain1.com,status:0},['green'],[{'open':,'closed':,'type':,'id':}]]
    # ]

    # Put together the first row, which are the headings
    data = []
    data.append(headings)
    services = Service.objects.values('service_name').order_by('service_name')
    events = Event.objects.filter(event_time__start__range=[dates[0],ref_q]).values('id',
                                                                                    'type',
                                                                                    'event_time__start',
                                                                                    'event_time__end',
                                                                                    'event_service__service__service_name',
                                                                                    'event_status__status').order_by('id')

    # Run through each service and see if it had an incident during the time range
    for service in services:
        # Make a row for this service, which looks like this:
        # {service:www.domain1.com,status:0},['green'],[{'open':,'closed':,'type':,'id':}]
        # The service will initially be green and incidents trump maintenances
        # Statuses are as follows:
        #   - 0 = green
        #   - 1 = active incident
        #   - 2 = active maintenance
        row = [{'service':service['service_name'],'status':0}]

        # Run through each date for each service
        for date in dates:

            # If there is a match, append it, otherwise leave blank
            match = False

            # Check each event to see if there is a match
            # There could be more than one event per day
            row_event = []

            # First the incidents
            for event in events:
                if service['service_name'] == event['event_service__service__service_name']:

                    # This event affected our service
                    # Convert to the requested timezone
                    event_date = event['event_time__start']
                    event_date = event_date.astimezone(pytz.timezone(set_timezone))

                    # If the event closed date is there, make sure the time zone is correct
                    end_date = event['event_time__end']
                    if event['event_time__end']:
                        end_date = end_date.astimezone(pytz.timezone(set_timezone))

                    if date.date() == event_date.date():
                        # This is our date so add the incident ID
                        match = True
                        e = {
                                 'type':event['type'],
                                 'id':event['id'],
                                 'open':event_date,
                                 'closed':end_date,
                                 'status':event['event_status__status']
                                 }
                        row_event.append(e)
            
                    # If this is an incident and it's still open, set the status
                    # Incidents over-ride everything for setting the status of the service
                    if event['type'] == 1 and event['event_status__status'] == 1:
                        row[0]['status'] = 1

                    # If it's a maintenance and it's still open, and there is no active incident,
                    # set the status
                    if event['type'] == 2 and event['event_status__status'] == 1 and not row[0]['event_status__status'] == 1:
                        row[0]['status'] = 2

            if match == False:
                row_event.append('green')

            # Add the event row to the main row
            row.append(row_event)

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
    incident_count = Event.objects.filter(event_time__start__range=[back_date,forward_date],type=1).values('event_time__start')
    
    # Obtain a count of maintenances, per day
    maintenance_count = Event.objects.filter(event_time__start__range=[back_date,forward_date],type=2).values('event_time__start')

    # Iterate through the graph_dates and find matching incidents/maintenances/reports
    # This data structure will look like this:
    # count_data = [
    #               {'date' : '2013-09-01', 'incidents':0, 'maintenances':0, 'reports':1}
    #              ]
    count_data = []

    # Boolean which turns true if we have maintenances or incidents
    # If not, the graph on the home page will not be shown
    show_graph = False

    for day in graph_dates:

        # Create a tuple to hold this data series
        t = {'date':day, 'incidents':0, 'maintenances':0, 'reports':0}

        # Check for incidents that match this date
        for row in incident_count:
            if row['event_time__start'].astimezone(pytz.timezone(set_timezone)).strftime("%Y-%m-%d") == day:
                t['incidents'] += 1
                show_graph = True

        # Check for maintenances that match this date
        for row in maintenance_count:
            if row['event_time__start'].astimezone(pytz.timezone(set_timezone)).strftime("%Y-%m-%d") == day:
                t['maintenances'] += 1
                show_graph = True

        # Add the tuple
        count_data.append(t)
    # ------------------ #


    # ------------------ #
    # Obtain the incident and maintenance timelines (open incidents)
    incident_timeline = Event.objects.filter(event_status__status=1,type=1).values('id',
                                                                                   'event_time__start',
                                                                                   'event_description__description',
                                                                                   ).order_by('-id')
    
    maintenance_timeline = Event.objects.filter(event_status__status=1,type=2).values('id',
                                                                                      'event_time__start',
                                                                                      'event_description__description',
                                                                                     ).order_by('-id')
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

    # Set the timezone to the user's requested timezone (otherwise TIME_ZONE will be used)
    jtz.activate(set_timezone)

    # Print the page
    return render_to_response(
       'main/index.html',
       {
          'title':'System Status Dashboard | Home',
          'data':data,
          'backward_link':backward_link,
          'forward_link':forward_link,
          'alert':alert,
          'information':information,
          'count_data':count_data,
          'timezones':timezones,
          'incident_timeline':incident_timeline,
          'maintenance_timeline':maintenance_timeline,
          'show_graph':show_graph
       },
       context_instance=RequestContext(request)
    )
    
   