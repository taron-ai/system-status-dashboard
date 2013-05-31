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


"""Views for the SSD project that pertain to setting user preferences only

"""


from django.http import HttpResponseRedirect
from ssd.main.forms import JumpToForm
from ssd.main.forms import UpdateTZForm


def timezone(request):
    """Process a form submit to set the timezone

    Supported timezones are from pytz

    """

    if request.method == 'POST':
        # Check the form elements
        form = UpdateTZForm(request.POST)

        if form.is_valid():
            # Obtain the cleaned data
            timezone = form.cleaned_data['timezone']

            # Set the timezone in a cookie and redirect to the homepage
            response = HttpResponseRedirect('/')
            response.set_cookie('timezone',
                                timezone,
                                max_age=157680000,
                                expires=157680000,
                                path='/',
                                domain=None,
                                secure=None,
                                httponly=False)
            return response

    # Either its not a POST, or the form was not valid
    # Redirect to the homepage and they'll get the server timezone if they
    # are not already cookied
    return HttpResponseRedirect('/')


def jump(request):
    """Process a form submit to jump to a specific date

    Any date can be processed

    """

    if request.method == 'POST':
        # Check the form elements
        form = JumpToForm(request.POST)

        if form.is_valid():
            # Obtain the cleaned data
            jump_to = form.cleaned_data['jump_to']

            # Send to the specified date
            return HttpResponseRedirect('/?ref=%s' % jump_to)

    # Either its not a POST, or the form was not valid
    # Redirect to the homepage and they'll get the standard view
    return HttpResponseRedirect('/')
