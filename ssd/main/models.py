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


"""Models for the SSD Project

    General Notes:
        - All non-char/text fields will be stored as null in the DB when blank (null=True)
        - All fields will be allowed to be blank (blank=true).  Form validation will confirm if the field is required

"""


import os
import time
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from datetime import datetime


class Service(models.Model):
    """Services that will be monitored"""

    service_name = models.CharField(max_length=50, unique=True,null=False,blank=False)


class Email(models.Model):
    """Email addresses that will be used for alerting"""

    email = models.CharField(max_length=100,unique=True,null=False,blank=False)


class Type(models.Model):
    """Event Types

        Current Types:
        - incident
        - maintenance
    """

    type = models.CharField(max_length=15, unique=True)


class Status(models.Model):
    """Event Status

        Current Statuses:
        - planning (maintenance only, when a maintenance is being planned but it's not started or completed)
        - open (incident only)
        - closed (incident only)
        - started (maintenance only)
        - completed (maintenance only)

    """
    
    status = models.CharField(max_length=10, unique=True)


class Event(models.Model):
    """Events that have been logged"""

    type = models.ForeignKey(Type)
    date = models.DateTimeField(null=False,blank=False,auto_now=True)
    description = models.CharField(blank=False,max_length=1000)
    start = models.DateTimeField(null=False)
    end = models.DateTimeField(null=True)
    status = models.ForeignKey(Status)
    user = models.ForeignKey(User)


class Event_Service(models.Model):
    """Tie services to events"""

    event = models.ForeignKey(Event)
    service = models.ForeignKey(Service)


class Event_Impact(models.Model):
    """Event Impact Analysis (maintenance specific)
        - only one entry allowed per event

    """

    event = models.ForeignKey(Event, unique=True)
    impact = models.CharField(max_length=1000)


class Event_Coordinator(models.Model):
    """Event Coordinator (maintenance specific)
        - only one entry allowed per event

    """

    event = models.ForeignKey(Event, unique=True)
    coordinator = models.CharField(max_length=1000)


class Event_Email(models.Model):
    """Event Email Recipient
        - only one entry allowed per event

    """

    event = models.ForeignKey(Event, unique=True)
    email = models.ForeignKey(Email)


class Event_Update(models.Model):
    """Updates to Events"""

    event = models.ForeignKey(Event)
    date = models.DateTimeField(null=False,blank=False,auto_now=True)
    update = models.CharField(max_length=1000)
    user = models.ForeignKey(User)


class Escalation(models.Model):
    """Escalation Contacts"""

    order = models.PositiveIntegerField(null=False,blank=False)
    name = models.CharField(null=False,blank=False,max_length=50)
    contact_details = models.CharField(null=False,blank=False,max_length=160)
    hidden = models.BooleanField(blank=False)

    class Meta:
        unique_together = ['name','contact_details']



#-- Configuration Models -- #

class Config_Email(models.Model):
    """Email Configuration
        Email Format:
            0 = text
            1 = html

    """

    enabled = models.BooleanField(blank=False)
    email_format = models.BooleanField(blank=False)
    from_address = models.CharField(null=False,blank=False,max_length=100)
    text_pager = models.CharField(null=False,blank=False,max_length=100)
    incident_greeting = models.CharField(null=False,blank=False,max_length=1000)
    incident_update = models.CharField(null=False,blank=False,max_length=1000)
    maintenance_greeting = models.CharField(null=False,blank=False,max_length=1000)
    maintenance_update = models.CharField(null=False,blank=False,max_length=1000)


class Config_Message(models.Model):
    """System Message Configuration

    """

    main = models.CharField(null=False,blank=False,max_length=1000)
    main_enabled = models.BooleanField(blank=False)
    alert = models.CharField(null=False,blank=False,max_length=1000)
    alert_enabled = models.BooleanField(blank=False)


class Config_Logo(models.Model):
    """System Logo Configuration

    """

    url = models.CharField(null=False,blank=False,max_length=1000)
    logo_enabled = models.BooleanField(blank=False)


class Config_Escalation(models.Model):
    """Escalation Path Configuration

    """

    enabled = models.BooleanField(blank=False)
    instructions = models.CharField(null=False,blank=False,max_length=1000)


class Config_Systemurl(models.Model):
    """System Url Configuration

    """

    url = models.CharField(null=False,blank=False,max_length=1000)
    url_enabled = models.BooleanField(blank=False)


class Config_Ireport(models.Model):
    """System Incident Report Configuration

    """

    enabled = models.BooleanField(blank=False)
    email_enabled = models.BooleanField(blank=False)
    instructions = models.CharField(null=False,blank=False,max_length=500)
    submit_message = models.CharField(null=False,blank=False,max_length=500)
    upload_enabled = models.BooleanField(blank=False)
    upload_path = models.CharField(null=False,blank=True,max_length=500)
    file_size = models.IntegerField(null=False,blank=True,max_length=5)


class Ireport(models.Model):
    """User reported issues"""

    # Obtain the user defined upload location
    # This needs to match the wsgi.conf staticly served location or else images will not be viewable
    fs = FileSystemStorage(Config_Ireport.objects.filter(id=Config_Ireport.objects.values('id')[0]['id']).values('upload_path')[0]['upload_path'])

    def _upload_to(instance, filename):
        """Rename uploaded images to a random (standard) name"""

        # Setup the file path to be unique so we don't fill up directories
        file_path = time.strftime('%Y/%m/%d')

        # Create a unique filename
        file_name = uuid.uuid4().hex

        # Save the original extension, if its there
        extension = os.path.splitext(filename)[1]

        # Return the path and file
        return '%s/%s%s' % (file_path,file_name,extension)

    date = models.DateTimeField(null=False,blank=False)
    name = models.CharField(null=False,blank=False,max_length=50)
    email = models.CharField(null=False,blank=False,max_length=50)
    detail = models.CharField(null=False,blank=False,max_length=160)
    extra = models.CharField(null=True,blank=True,max_length=1000)
    screenshot1 = models.ImageField(storage=fs,upload_to=_upload_to)
    screenshot2 = models.ImageField(storage=fs,upload_to=_upload_to)

    