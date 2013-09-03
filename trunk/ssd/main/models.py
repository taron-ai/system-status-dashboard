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

   Any models that will be displayed in the DJango admin will have unicode 
   methods to display them properly in the admin

"""


import os
import time
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from datetime import datetime


class Config(models.Model):
    """Configuration parameters

    The config_value and description need to be sufficiently large to accommodate
    enough help text to be useful
    """

    config_name = models.CharField(max_length=50, unique=True)
    friendly_name = models.CharField(max_length=50, unique=True)
    config_value = models.CharField(max_length=1000)
    description = models.CharField(max_length=500,blank=False)
    category = models.CharField(max_length=15,blank=False)
    display = models.CharField(max_length=8,blank=False)


class Service(models.Model):
    """Services that will be monitored"""

    service_name = models.CharField(max_length=50, unique=True,null=False,blank=False)


class Recipient(models.Model):
    """Email addresses that will be used for alerting"""

    email_address = models.CharField(max_length=100,unique=True,null=False,blank=False)


class Type(models.Model):
    """Event Types"""

    type = models.CharField(max_length=20)


class Event(models.Model):
    """Events that have been logged"""

    date = models.DateTimeField(null=False,blank=False)
    type = models.ForeignKey(Type)


class Event_Time(models.Model):
    """Event start/stop times"""

    start = models.DateTimeField(null=False,blank=False)
    end = models.DateTimeField(null=False,blank=False)
    event = models.ForeignKey(Event)


class Event_Update(models.Model):
    """Updates to incidents"""

    event = models.ForeignKey(Event)
    update = models.CharField(max_length=1000)
    

class Service_Issue(models.Model):
    """Used to tie services to issues so that one issue can impact multiple services"""

    service_name = models.ForeignKey(Service)
    incident = models.ForeignKey(Incident)


class Maintenance(models.Model):
    """Maintenance that has been scheduled"""

    start = models.DateTimeField(null=False,blank=False)
    end = models.DateTimeField(null=False,blank=False)
    description = models.CharField(blank=False,max_length=1000)
    impact = models.CharField(blank=False,max_length=1000)
    coordinator = models.CharField(blank=False,max_length=1000)
    email_address = models.ForeignKey(Recipient,null=True,blank=True)
    user = models.ForeignKey(User)
    started = models.BooleanField()
    completed = models.BooleanField()


class Maintenance_Update(models.Model):
    """Updates to incidents"""

    date = models.DateTimeField(default=datetime.now(),null=False,blank=False)
    maintenance = models.ForeignKey(Maintenance)
    user = models.ForeignKey(User)
    detail = models.CharField(max_length=1000)


class Service_Maintenance(models.Model):
    """Used to tie services to scheduled maintenance so that one maintenance can impact multiple services"""

    service_name = models.ForeignKey(Service)
    maintenance = models.ForeignKey(Maintenance)


class Report(models.Model):
    """User reported issues"""

    # Obtain the custom upload location
    fs = FileSystemStorage(Config.objects.filter(config_name='upload_path').values('config_value')[0]['config_value'])

    def _upload_to(instance, filename):
        """Rename uploaded images to a random (standard) name"""

        # Setup the file path to be unique so we don't fill up directories
        file_path = time.strftime('%Y/%m/%d')

        # Create a unique filename
        file_name = uuid.uuid4().hex

        # Save the original extension, if its there
        extension = os.path.splitext(filename)[1]

        # Return the path and file
        return 'uploads/screenshots/%s/%s%s' % (file_path,file_name,extension)

    date = models.DateTimeField(null=False,blank=False)
    name = models.CharField(null=False,blank=False,max_length=50)
    email = models.CharField(null=False,blank=False,max_length=50)
    detail = models.CharField(null=False,blank=False,max_length=160)
    extra = models.CharField(null=True,blank=True,max_length=1000)
    screenshot1 = models.ImageField(storage=fs,upload_to=_upload_to)
    screenshot2 = models.ImageField(storage=fs,upload_to=_upload_to)


class Escalation(models.Model):
    """Escalation Contacts"""

    order = models.PositiveIntegerField(null=False,blank=False)
    name = models.CharField(null=False,blank=False,max_length=50)
    contact_details = models.CharField(null=False,blank=False,max_length=160)
    hidden = models.BooleanField(blank=False)

    class Meta:
        unique_together = ['name','contact_details']
