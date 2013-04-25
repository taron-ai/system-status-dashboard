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
from ssd.main.models import Maintenance
from ssd.main.models import Maintenance_Update
from ssd.main.models import Service_Maintenance
from django.core.mail import EmailMessage
from ssd.main.models import Recipient
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
        Send a short text message/page in text format
        The required format of EmailMessage is as follows:
          - EmailMessage(subject,body,from_email,[to_email],[bcc_email],headers,[cc_email]
          - If there is an error, the user will be notified and an Apache error log will be generated
          
        """

        # Instantiate the configuration value getter
        cv = config_value.config_value()

        # Obtain the recipient email address
        recipient_pager = cv.value('recipient_pager')

        # Obtain the sender email address and instantiate the message
        email_from = cv.value('email_from')
        pager = EmailMessage('Incident Alert',message,email_from,[recipient_pager],None,None,None)

        # If there is an issue, the user will be notified
        try:
            pager.send()
        except Exception, e:
            # Log to the error log and return the error to the caller
            print e
            return e
        return 'success'

    
    def incident(self,id,recipient_id,set_timezone,new):
        """
        Send an email message in HTML format about a new or existing incident
           - If there is an error, the user will not be notified but an Apache error log will be generated
        """

        # Instantiate the configuration value getter
        cv = config_value.config_value()

        # Incident detail
        detail = Incident.objects.filter(id=id).values('date','closed','detail')

        # Which services were impacted
        services = Service_Issue.objects.filter(incident_id=id).values('service_name_id__service_name')

        # Obain any incident updates
        updates = Incident_Update.objects.filter(incident_id=id).values('id','date','detail').order_by('id')

        # Obtain the recipient name
        recipient_name = cv.value('recipient_name')

        # Obtain the recipient email address
        recipient_incident = Recipient.objects.filter(id=recipient_id).values('email_address')[0]['email_address']

        # Obtain the sender email address
        email_from = cv.value('email_from')

        # Obtain the email subject
        email_subject_incident = cv.value('email_subject_incident')

        # Obtain the ssd url
        ssd_url = cv.value('ssd_url')

        # HTML (true) or text (false) formatting
        format = int(cv.value('email_format_incident'))

        # Obtain the greeting
        if new == True:
            greeting = cv.value('greeting_incident_new')
        else:
            greeting = cv.value('greeting_incident_update')

        # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
        jtz.activate(set_timezone)

        # Interpolate values for the template
        d = Context({ 
                     'detail':detail,
                     'recipient_name':recipient_name,
                     'greeting':greeting,
                     'services':services,
                     'updates':updates,
                     'ssd_url':ssd_url,
                     'timezone':set_timezone
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
            # Log to the error log
            print e


    def maintenance(self,id,recipient_id,set_timezone,new):
        """
        Send an email message in HTML format about a new or existing maintenance
           - If there is an error, the user will not be notified but an Apache error log will be generated
        """

        # Instantiate the configuration value getter
        cv = config_value.config_value()

        # Obain the incident detail
        detail = Maintenance.objects.filter(id=id).values('start','end','description','impact','coordinator','started','completed')

        # Which services were impacted
        services = Service_Maintenance.objects.filter(maintenance_id=id).values('service_name_id__service_name')

        # Obain any incident updates
        updates = Maintenance_Update.objects.filter(maintenance_id=id).values(
                                                                              'id',
                                                                              'date',
                                                                              'user_id__first_name',
                                                                              'user_id__last_name',
                                                                              'detail'
                                                                             ).order_by('id')

        # Obtain the recipient name
        recipient_name = cv.value('recipient_name')

        # Obtain the recipient email address
        recipient_maintenance = Recipient.objects.filter(id=recipient_id).values('email_address')[0]['email_address']

        # Obtain the sender email address
        email_from = cv.value('email_from')

        # Obtain the email subject
        email_subject_maintenance = cv.value('email_subject_maintenance')

        # Obtain the ssd url
        ssd_url = cv.value('ssd_url')

        # HTML (true) or text (false) formatting
        format = int(cv.value('email_format_maintenance'))

        # Obtain the greeting
        if new == True:
            greeting = cv.value('greeting_maintenance_new')
        else:
            greeting = cv.value('greeting_maintenance_update')

        # Set the timezone to the user's timezone (otherwise TIME_ZONE will be used)
        jtz.activate(set_timezone)

        # Interpolate the values
        d = Context({ 
                     'detail':detail,
                     'recipient_name':recipient_name,
                     'greeting':greeting,
                     'services':services,
                     'updates':updates,
                     'ssd_url':ssd_url,
                     'timezone':set_timezone
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
            # Log to the error log
            print e

