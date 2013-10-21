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


import logging
import datetime
import pytz
import re
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from ssd.dashboard.models import Event, Service, Config_Message


# Get an instance of the ssd logger
logger = logging.getLogger(__name__)


def index(request):
    """Index Page View

    Show the calendar view with 7 days of information on all services

    """
    
    logger.debug('%s view being executed.' % 'main.index')

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
        ref = ref.astimezone(pytz.timezone(request.timezone))

        # Format for just the year, month, day.  We'll add the entire day later
        ref = ref.strftime("%Y-%m-%d")

    # The reference date we use in the query to find relevant incidents
    # is different than the reference date we use for the calendar
    # because the query needs to go through 23:59:59
    ref_q = ref + ' 23:59:59'
    # If the reference date is not in the proper form, provide an error and redirect to the 
    # standard homepage
    try:
        ref_q = datetime.datetime.strptime(ref_q,'%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        # Set an error message
        messages.add_message(request, messages.ERROR, 'Improperly formatted reference date.')
        # Redirect to the homepage
        return HttpResponseRedirect('/') 
    ref_q = pytz.timezone(request.timezone).localize(ref_q)

    # The reference date is the last date displayed in the calendar
    # so add that and create a datetime object in the user's timezone
    # (or the server timezone if its not set)
    ref += ' 00:00:00'
    ref = datetime.datetime.strptime(ref,'%Y-%m-%d %H:%M:%S') 
    ref = pytz.timezone(request.timezone).localize(ref)

    # Obtain the current 7 days
    dates = []
    headings = ['Status','Service']
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

    # Determine if there are any active events (incidents or maintenances), regardless of the time range
    # This will be used to set the main service status

    # Active Incidents
    try:
        active_incidents = cache.get('active_incidents')
    except Exception as e:
        logger.error('Exception getting active_incidents from cache: %s' % e)
        active_incidents = None
    if active_incidents == None:
        active_incidents = Event.objects.filter(type__type='incident',status__status='open').values('event_service__service__service_name')
        cache.set('active_incidents', active_incidents)

    # Active Maintenances
    try:
        active_maintenances = cache.get('active_maintenances')
    except Exception as e:
        logger.error('Exception getting active_maintenances from cache: %s' % e)
        active_maintenances = None 
    if active_maintenances == None:
        active_maintenances = Event.objects.filter(type__type='maintenance',status__status='started').values('event_service__service__service_name')
        cache.set('active_maintenances', active_maintenances)

    # Create an easy lookup table for later
    events_lookup = {
        'incident':{},
        'maintenance':{}
    }
    if active_incidents:
        for incident in active_incidents:
            events_lookup['incident'][incident['event_service__service__service_name']] = ''
    if active_maintenances:
        for maintenance in active_maintenances:
            events_lookup['maintenance'][maintenance['event_service__service__service_name']] = ''


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

    # Grab all services
    services = cache.get('services')
    if services == None:
        services = Service.objects.values('service_name').order_by('service_name')
        cache.set('services', services)

    # Grab all events within the time range requested
    try:
        events = cache.get('events')
    except Exception as e:
        logger.error('Exception getting events from cache: %s' % e)
        events = None 
    if events == None:
        events = Event.objects.filter(start__range=[dates[0],ref_q]).values('id',
                                                                            'type__type',
                                                                            'description',
                                                                            'start',
                                                                            'end',
                                                                            'event_service__service__service_name',
                                                                            'status__status'
                                                                            ).order_by('id')
        cache.set('events', events)

    # Run through each service and see if it had an incident during the time range
    for service in services:
        # Make a row for this service, which looks like this:
        # {service:www.domain1.com,status:0},['green'],[{'id':foo, 'description':foo,'open':foo,'closed':foo,'type':foo}]
        # The service will initially be green and incidents trump maintenances
        # Statuses are as follows:
        #   - 0 = green
        #   - 1 = active incident
        #   - 2 = active maintenance
        row = [{'service':service['service_name'],'status':0}]

        # Set the status from our lookup table first
        # Incidents over-ride everything for setting the status of the service
        if service['service_name'] in events_lookup['incident']:
            row[0]['status'] = 1
        elif service['service_name'] in events_lookup['maintenance']:
            row[0]['status'] = 2

        # Run through each date for each service
        for date in dates:

            # Check each event to see if there is a match
            # There could be more than one event per day
            row_event = []

            # First the incidents
            for event in events:
                if service['service_name'] == event['event_service__service__service_name']:

                    # This event affected our service
                    # Convert to the requested timezone
                    event_date = event['start']
                    event_date = event_date.astimezone(pytz.timezone(request.timezone))

                    # If the event closed date is there, make sure the time zone is correct
                    end_date = event['end']
                    if event['end']:
                        end_date = end_date.astimezone(pytz.timezone(request.timezone))

                    # If this is our date, add it
                    if date.date() == event_date.date():
                        # This is our date so add the incident information
                        e = {
                                 'id':event['id'],
                                 'type':event['type__type'],
                                 'description':event['description'],
                                 'open':event_date,
                                 'closed':end_date,
                                 'status':event['status__status']
                                 }
                        row_event.append(e)
            
            # If the row_event is empty, this indicates there were no incidents so mark this date/service as green
            if not row_event:
                row_event.append('green')
                

            # Add the event row to the main row
            row.append(row_event)

        # Add the main row to our data dict
        data.append(row)


    # ------------------ #
    # Obtain a count of all incidents/maintenances going back 15 days and forward 15 days (from the reference date) for the summary
    # graph
    
    # First populate all of the dates into an array so we can iterate through 
    graph_dates = []
    
    # The back dates (including today)
    day_range = 15
    counter = day_range
    while counter >= 0:
        day = datetime.timedelta(days=counter)
        day = ref - day
        day = day.strftime("%Y-%m-%d")
        graph_dates.append(day)
        counter -= 1

    # Now the forward dates
    counter = 1
    while counter <= day_range:
        day = datetime.timedelta(days=counter)
        day = ref + day
        day = day.strftime("%Y-%m-%d")
        graph_dates.append(day)
        counter += 1


    # Obtain the back and forward dates for the query    
    back = datetime.timedelta(days=day_range)
    back_date = ref - back
    forward = datetime.timedelta(days=day_range)
    forward_date = ref_q + forward
    
    # Obtain a count of incidents, per day
    incident_count = cache.get('incident_count')
    if incident_count == None:
        incident_count = Event.objects.filter(start__range=[back_date,forward_date],type__type='incident').values('start')
        cache.set('incident_count', incident_count)

    # Obtain a count of maintenances, per day
    maintenance_count = cache.get('maintenance_count')
    if maintenance_count == None:
        maintenance_count = Event.objects.filter(start__range=[back_date,forward_date],type__type='maintenance').values('start')
        cache.set('maintenance_count', maintenance_count)

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
            if row['start'].astimezone(pytz.timezone(request.timezone)).strftime("%Y-%m-%d") == day:
                t['incidents'] += 1
                show_graph = True

        # Check for maintenances that match this date
        for row in maintenance_count:
            if row['start'].astimezone(pytz.timezone(request.timezone)).strftime("%Y-%m-%d") == day:
                t['maintenances'] += 1
                show_graph = True

        # Add the tuple
        count_data.append(t)
    # End counts
    # ------------------ #


    # ------------------ #
    # Obtain the incident (open) and maintenance (started) timelines
    incident_timeline = cache.get('incident_timeline')
    if incident_timeline == None:
        incident_timeline = Event.objects.filter(status__status='open',type__type='incident').values('id','start','description').order_by('-id')
        cache.set('incident_timeline', incident_timeline)

    maintenance_timeline = cache.get('maintenance_timeline')
    if maintenance_timeline == None:
        maintenance_timeline = Event.objects.filter(status__status='started',type__type='maintenance').values('id','start','description').order_by('-id')
        cache.set('maintenance_timeline', maintenance_timeline)
    # End timelines
    # ------------------ #


    # ------------------ #
    # Alert and information text
    alerts = cache.get('alerts')
    if alerts == None:
        alerts = Config_Message.objects.filter(id=Config_Message.objects.values('id')[0]['id']).values('alert_enabled','alert','main_enabled','main')
        cache.set('alerts', alerts)

    # If we are showing the alert, obtain the alert text
    if alerts[0]['alert_enabled'] == 1:
        alert = alerts[0]['alert']
    else:
        alert = None

    # If we are showing the information message, obtain the text
    if alerts[0]['main_enabled'] == 1:
        information = alerts[0]['main']
    else:
        information = None
    # End alert and information text
    # ------------------ #

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
          'incident_timeline':incident_timeline,
          'maintenance_timeline':maintenance_timeline,
          'show_graph':show_graph
       },
       context_instance=RequestContext(request)
    )
    
   