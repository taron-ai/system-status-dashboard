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


"""Views for the SSD Project that pertain to search functionality only

"""


import datetime
import pytz
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from ssd.main.models import Event
from ssd.main.forms import SearchForm, GSearchForm, ListForm


def gsearch(request):
    """Event Search View (Graph)

    Show events for a specific date, when clicked through from the summary graph

    """

    form = GSearchForm(request.GET)

    if form.is_valid():
        # Obtain the cleaned data (only validate the dates)
        date = form.cleaned_data['date']
        type = form.cleaned_data['type']

        # Combine the dates and times into datetime objects
        start = datetime.datetime.combine(date, datetime.datetime.strptime('00:00:00','%H:%M:%S').time())
        end = datetime.datetime.combine(date, datetime.datetime.strptime('23:59:59','%H:%M:%S').time())

        # Set the timezone
        tz = pytz.timezone(request.timezone)
        start = tz.localize(start)
        end = tz.localize(end)

        results = Event.objects.filter(type__type=type,start__range=[start,end]
                                              ).values('id','type__type','start','end','description',
                                              ).distinct().order_by('-start')

        # Print the page
        return render_to_response(
           'search/search_results.html',
           {
              'title':'System Status Dashboard | Event Search',
              'results':results
           },
           context_instance=RequestContext(request)
        )
    
    # Invalid form
    else:
        messages.add_message(request, messages.ERROR, 'Invalid graph search query')
        return HttpResponseRedirect('/') 


def search(request):
    """Event Search View 

    Permit simple searching of events

    """

    return HttpResponseRedirect('/') 


def events(request):
    """Event List View 

    Show a listing of all events

    """

    form = ListForm(request.GET)

    # Check the params
    if form.is_valid():

        page = form.cleaned_data['page']

        # Obtain all incidents
        events_all = Event.objects.values('id','status__status','type__type','start','end','description').order_by('-id')

        # Create a paginator and paginate the list w/ 10 messages per page
        paginator = Paginator(events_all, 10)

        # Paginate them
        try:
            events = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, or is not given deliver first page.
            events = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            events = paginator.page(paginator.num_pages)

        # Print the page
        return render_to_response(
           'search/list.html',
           {
              'title':'System Status Dashboard | List Events',
              'events':events,
           },
           context_instance=RequestContext(request)
        )


    return HttpResponseRedirect('/') 