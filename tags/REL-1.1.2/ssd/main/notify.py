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
from django.core.mail import EmailMultiAlternatives
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context
from django.utils import timezone as jtz


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

        # Obtain the recipient email address
        page_to = Config.objects.filter(config_name='page_to').values('config_value')

        # Obtain the sender email address and instantiate the message
        email_from = Config.objects.filter(config_name='email_from').values('config_value')
        pager = EmailMessage('Incident Alert',message,email_from[0]['config_value'],[page_to[0]['config_value']],None,None,None)

        # If there is an issue, the user will be notified
        try:
            pager.send()
        except Exception, e:
            # Log to the error log
            print e
            return e
        return 'success'

    def send(self,id,ssd_url,set_timezone,new):
        """
        Send an email
        If there is an error, the user will not be notified but this will log to Apache error log
        """

        # Incident detail
        detail = Incident.objects.filter(id=id).values('date','closed','detail')

        # Which services were impacted
        services = Service_Issue.objects.filter(incident_id=id).values('service_name_id__service_name')

        # Obain any incident updates
        updates = Incident_Update.objects.filter(incident_id=id).values('id','date','detail').order_by('id')

        # Create the messages
        text_template = get_template('email/notify.txt')
        html_template = get_template('email/notify.html')

        # Obtain the company name
        company = Config.objects.filter(config_name='company').values('config_value')

        # Obtain the recipient email address
        email_to = Config.objects.filter(config_name='email_to').values('config_value')

        # Obtain the sender email address
        email_from = Config.objects.filter(config_name='email_from').values('config_value')

        # Obtain the email subject
        email_subject = Config.objects.filter(config_name='email_subject').values('config_value')

        # Obtain the greeting
        if new == True:
            greeting = Config.objects.filter(config_name='greeting_new').values('config_value')
        else:
            greeting = Config.objects.filter(config_name='greeting_update').values('config_value')

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
        text = text_template.render(d)

        try:
            msg = EmailMultiAlternatives(
                                         email_subject[0]['config_value'], 
                                         text, 
                                         email_from[0]['config_value'], 
                                         [email_to[0]['config_value']]
                                        )
            msg.attach_alternative(html, "text/html")
            msg.send()
        except Exception, e:
            # Log to the error log
            print e


