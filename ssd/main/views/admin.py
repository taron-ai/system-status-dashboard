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
from django.conf import settings
from django.core.cache import cache, get_cache
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


    # -- MEMCACHED INFORMATION --#

    m_stats = []

    # Table Headings, will look like this:
    # ['Statistic','Server1','Server2','Server3']
    headings = ['Statistic']
    # Table rows, will look like this:
    # {
    #   'auth_cmd':[2,3,4],
    #   'curr_connections':[7,3,2]
    # }
    rows = {}
    m_stats = [headings,rows]

    cache_settings = None
    # Note, headings and rows should have the same number of elements
    # or something is wrong
    if hasattr(settings, 'CACHES'):
        cache_settings = settings.CACHES
        try:
            for c in settings.CACHES:
                stats = get_cache(c)._cache.get_stats()
  
                for server_cache in stats:
                    server = server_cache[0]
                    current_stats = server_cache[1]

                    # Add the server to the headings
                    headings.append(server)

                    # Iterate over the stats and add to the rows dict
                    for key,value in current_stats.items():
                        # If the relevant list does not exist yet, create it
                        if not key in rows:
                            rows[key] = []

                        rows[key].append(value)

        except Exception as e:
            logger.error('Cannot obtain memcached settings: %s' % e)
    else:
        logger.debug('No memcached caches are defined.')


    # Print the page
    return render_to_response(
       'admin/main.html',
       {
          'title':'System Status Dashboard | Admin',
          'version':get_version,
          'cache_settings':cache_settings,
          'm_stats':m_stats,
          'breadcrumbs':{'Admin':'/admin'}
       },
       context_instance=RequestContext(request)
    )

