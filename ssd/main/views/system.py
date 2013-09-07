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


"""This module contains generic system functionality for the SSD project

"""


from django.shortcuts import render_to_response
from django.template import RequestContext



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
     'system/system_message.html',
      {
        'title':'System Status Dashboard | System Message',
        'status':status,
        'message':message
      },
      context_instance=RequestContext(request)
    )

    # Give the response back
    return response