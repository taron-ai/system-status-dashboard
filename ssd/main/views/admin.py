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


"""This module contains all of the admin functions of ssd"""


import logging
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django import get_version
from ssd.main.models import Config_Email


# Get an instance of the ssd logger
logger = logging.getLogger(__name__)


@login_required
@staff_member_required
def main(request):
    """Main admin index view
 
    """

    logger.debug('%s view being executed.' % 'admin.main')

    # Print the page
    return render_to_response(
       'admin/main.html',
       {
          'title':'System Status Dashboard | Admin',
          'version':get_version,
          'breadcrumbs':{'Admin':'/admin'}
       },
       context_instance=RequestContext(request)
    )

