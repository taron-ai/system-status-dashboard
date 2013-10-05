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


"""Email class for SSD

   This class handles the sending of emails and pages to the appropriate recipients

"""

import logging
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context
from django.utils import timezone as jtz
from ssd.main.models import Email
from ssd.main.models import Event
from ssd.main.models import Config_Email


# Get an instance of the ssd logger
logger = logging.getLogger(__name__)


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
        Send a short text message/page in text format
        The required format of EmailMessage is as follows:
          - EmailMessage(subject,body,from_email,[to_email],[bcc_email],headers,[cc_email]
          - If there is an error, the user will be notified and an Apache error log will be generated
          
        """

        # Obtain the recipient email address
        text_pager = Config_Email.objects.filter(id=Config_Email.objects.values('id')[0]['id']).values('text_pager')[0]['text_pager']

        # Obtain the sender email address and instantiate the message
        from_address = Config_Email.objects.filter(id=Config_Email.objects.values('id')[0]['id']).values('from_address')[0]['from_address']
        pager = EmailMessage('Incident Alert',message,from_address,[text_pager],None,None,None)

        # If there is an issue, the user will be notified
        try:
            pager.send()
        except Exception, e:
            # Log to the error log and return the error to the caller
            logger.error('Error sending text page: %s' % e)
        
    
    def incident(self,id,email_id,set_timezone,new):
        """
        Send an email message in HTML format about a new or existing incident
           - If there is an error, the user will not be notified but an Apache error log will be generated
        """


        # Obain the incident detail
        detail = Event.objects.filter(id=id).values(
                                                    'event_time__start',
                                                    'event_time__end',
                                                    'event_description__description',
                                                    'event_email__email__email',
                                                    'event_user__user__first_name',
                                                    'event_user__user__last_name'
                                                    )

        # Which services were impacted
        services = Event.objects.filter(id=id).values('event_service__service__service_name')

        # Obain any incident updates
        updates = Event.objects.filter(id=id).values(
                                                    'event_update__id',
                                                    'event_update__date',
                                                    'event_update__update',
                                                    'event_update__user__first_name',
                                                    'event_update__user__last_name'
                                                    ).order_by('event_update__id')

        # Obtain the recipient email address
        recipient_incident = Email.objects.filter(id=email_id).values('email')[0]['email']

        # Obtain the sender email address
        email_from = Config_Email.objects.filter(id=Config_Email.objects.values('id')[0]['id']).values('from_address')[0]['from_address']

        # Obtain the ssd url
        ssd_url = Config_Systemurl.objects.filter(id=Config_Systemurl.objects.values('id')[0]['id']).values('url')[0]['url']

        # HTML (true) or text (false) formatting
        format = Config_Email.objects.filter(id=Config_Email.objects.values('id')[0]['id']).values('email_format')[0]['email_format']

        # Obtain the greeting
        if new == True:
            greeting = Config_Email.objects.filter(id=Config_Email.objects.values('id')[0]['id']).values('incident_greeting')[0]['incident_greeting']
            email_subject_incident = 'Incident Notification'
        else:
            greeting = Config_Email.objects.filter(id=Config_Email.objects.values('id')[0]['id']).values('incident_update')[0]['incident_update']
            email_subject_incident = 'Incident Update'

        # Interpolate values for the template
        d = Context({ 
                     'detail':detail,
                     'greeting':greeting,
                     'services':services,
                     'updates':updates,
                     'ssd_url':ssd_url,
                    })

        if format:
            # Its HTML
            template = get_template('email/incident.html')
        else:
            # Its text
            template = get_template('email/incident.txt')

        # Render the template
        rendered_template = template.render(d)

        try:
            msg = EmailMessage(
                                email_subject_incident, 
                                rendered_template, 
                                email_from, 
                                [recipient_incident],None,None,None
                              )

            # Change the content type to HTML, if requested
            if format:
                msg.content_subtype = 'html'
            
            # Send it
            msg.send()
        except Exception, e:
            # Log to the error log and return the error to the caller
            print e
            return e

        # All good
        return 'success'


    def maintenance(self,id,email_id,set_timezone,new):
        """
        Send an email message in HTML format about a new or existing maintenance
           - If there is an error, the user will not be notified but an Apache error log will be generated
        """

        # Obain the incident detail
        detail = Event.objects.filter(id=id).values(
                                                    'event_time__start',
                                                    'event_time__end',
                                                    'event_description__description',
                                                    'event_impact__impact',
                                                    'event_coordinator__coordinator',
                                                    'event_status__status'
                                                    )

        # Which services were impacted
        services = Event.objects.filter(id=id).values('event_service__service__service_name')

        # Obain any incident updates
        updates = Event.objects.filter(id=id).values(
                                                    'event_update__id',
                                                    'event_update__date',
                                                    'event_update__update',
                                                    'event_update__user__first_name',
                                                    'event_update__user__last_name'
                                                    ).order_by('event_update__id')

        # Obtain the recipient email address
        recipient_incident = Email.objects.filter(id=email_id).values('email')[0]['email']

        # Obtain the sender email address
        email_from = Config_Email.objects.filter(id=Config_Email.objects.values('id')[0]['id']).values('from_address')[0]['from_address']

        # Obtain the ssd url
        ssd_url = Config_Systemurl.objects.filter(id=Config_Systemurl.objects.values('id')[0]['id']).values('url')[0]['url']

        # HTML (true) or text (false) formatting
        format = Config_Email.objects.filter(id=Config_Email.objects.values('id')[0]['id']).values('email_format')[0]['email_format']

        # Obtain the greeting
        if new == True:
            greeting = Config_Email.objects.filter(id=Config_Email.objects.values('id')[0]['id']).values('maintenance_greeting')[0]['maintenance_greeting']
            email_subject_incident = 'Maintenance Notification'
        else:
            greeting = Config_Email.objects.filter(id=Config_Email.objects.values('id')[0]['id']).values('maintenance_update')[0]['incident_update']
            email_subject_incident = 'Maintenance Update'

        # Interpolate the values
        d = Context({ 
                     'detail':detail,
                     'greeting':greeting,
                     'services':services,
                     'updates':updates,
                     'ssd_url':ssd_url,
                    })

        if format:
            # Its HTML
            template = get_template('email/maintenance.html')
        else:
            # Its text
            template = get_template('email/maintenance.txt')

        # Render the template
        rendered_template = template.render(d)

        try:
            msg = EmailMessage(
                                email_subject_maintenance, 
                                rendered_template, 
                                email_from, 
                                [recipient_maintenance],None,None,None
                              )

            # Change the content type to HTML, if requested
            if format:
                msg.content_subtype = 'html'
            
            # Send it
            msg.send()
        except Exception, e:
            # Log to the error log and return the error to the caller
            print e
            return e

        # All good
        return 'success'

