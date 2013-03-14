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


"""Email class for SSD

   This class handles the sending of emails and pages to the appropriate recipients

"""


from ssd.main.models import Config
from ssd.main.models import Incident
from ssd.main.models import Service_Issue
from ssd.main.models import Incident_Update
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context
from django.utils import timezone as jtz
from ssd.main import config_value


class email:

    """
    Email and Pager helper class for SSD
    """

    def __init__(self):
        """
        Constructor

        """

    def page(self,message):
        """
        Send a short text message/page
        The required format of EmailMessage is as follows:
        EmailMessage(subject,body,from_email,[to_email],[bcc_email],headers,[cc_email]
        """

        # Instantiate the configuration value getter
        cv = config_value.config_value()

        # Obtain the recipient email address
        page_to = cv.value('page_to')

        # Obtain the sender email address and instantiate the message
        email_from = cv.value('email_from')
        pager = EmailMessage('Incident Alert',message,email_from,[page_to],None,None,None)

        # If there is an issue, the user will be notified
        try:
            pager.send()
        except Exception, e:
            # Log to the error log and return the error to the caller
            print e
            return e
        return 'success'

    
    def send(self,id,ssd_url,set_timezone,new):
        """
        Send an email
        If there is an error, the user will not be notified but this will log to the Apache error log
        """

        # Instantiate the configuration value getter
        cv = config_value.config_value()

        # Incident detail
        detail = Incident.objects.filter(id=id).values('date','closed','detail')

        # Which services were impacted
        services = Service_Issue.objects.filter(incident_id=id).values('service_name_id__service_name')

        # Obain any incident updates
        updates = Incident_Update.objects.filter(incident_id=id).values('id','date','detail').order_by('id')

        # Get the template
        html_template = get_template('email/notify.html')

        # Obtain the company name
        company = cv.value('company')

        # Obtain the recipient email address
        email_to = cv.value('email_to')

        # Obtain the sender email address
        email_from = cv.value('email_from')

        # Obtain the email subject
        email_subject = cv.value('email_subject')

        # Obtain the greeting
        if new == True:
            greeting = cv.value('greeting_new')
        else:
            greeting = cv.value('greeting_update')

        # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
        jtz.activate(set_timezone)

        d = Context({ 
                     'detail':detail,
                     'company':company,
                     'greeting':greeting,
                     'services':services,
                     'updates':updates,
                     'link':ssd_url,
                     'timezone':set_timezone
                    })

        html = html_template.render(d)
        
        try:
            msg = EmailMessage(
                                email_subject, 
                                html, 
                                email_from, 
                                [email_to],None,None,None
                              )
            msg.send()
        except Exception, e:
            # Log to the error log
            print e


