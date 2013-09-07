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


from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from ssd.main.models import Escalation
from ssd.main import config_value


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
       'escalation/escalation.html',
       {
          'title':'System Status Dashboard | Escalation Path',
          'contacts':contacts,
          'help':help
       },
       context_instance=RequestContext(request)
    )