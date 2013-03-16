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


"""Models for the SSD Project

   Any models that will be displayed in the DJango admin will have unicode 
   methods to display them properly in the admin

"""


from django.db import models
import os
import time
import uuid


class Config(models.Model):
    """Configuration parameters

    The config_value and description need to be sufficiently large to accommodate
    enough help text to be useful
    """

    config_name = models.CharField(max_length=50, unique=True)
    friendly_name = models.CharField(max_length=50, unique=True)
    config_value = models.CharField(max_length=1000)
    description = models.CharField(max_length=500,blank=True)
    display = models.CharField(max_length=8,blank=False)

    # Represent the object as unicode
    def __unicode__(self):
        return self.config_name


class Service(models.Model):
    """Services that will be monitored"""

    service_name = models.CharField(max_length=50)

    # Represent the object as unicode
    def __unicode__(self):
        return self.service_name


class Incident(models.Model):
    """Incidents that have been logged"""

    date = models.DateTimeField(null=False,blank=False)
    closed = models.DateTimeField(null=True)
    detail = models.CharField(max_length=1000)

    # Represent the objects as unicode
    def __unicode__(self):
        return u'%s,%s' % (self.date,self.detail)


class Incident_Update(models.Model):
    """Updates to incidents"""

    date = models.DateTimeField(null=False,blank=False)
    incident = models.ForeignKey(Incident)
    detail = models.CharField(max_length=1000)

    # Represent the objects as unicode
    def __unicode__(self):
        return u'%s %s %s' % (self.date,self.incident,self.detail)


class Service_Issue(models.Model):
    """Used to tie services to issues so that one issue can impact multiple services"""

    service_name = models.ForeignKey(Service)
    incident = models.ForeignKey(Incident)

    # Represent the objects as unicode
    def __unicode__(self):
        return u'%s %s' % (self.service_name,self.incident)


class Maintenance(models.Model):
    """Maintenance that has been scheduled"""

    start = models.DateTimeField(null=False,blank=False)
    end = models.DateTimeField(null=False,blank=False)
    description = models.CharField(blank=False,max_length=1000)
    impact = models.CharField(blank=False,max_length=1000)
    coordinator = models.CharField(blank=False,max_length=1000)
    started = models.BooleanField()
    completed = models.BooleanField()

    # Represent the objects as unicode
    def __unicode__(self):
        return u'%s,%s' % (self.start,self.description)


class Maintenance_Update(models.Model):
    """Updates to incidents"""

    date = models.DateTimeField(null=False,blank=False)
    maintenance = models.ForeignKey(Maintenance)
    detail = models.CharField(max_length=1000)

    # Represent the objects as unicode
    def __unicode__(self):
        return u'%s %s %s' % (self.date,self.maintenance,self.detail)


class Service_Maintenance(models.Model):
    """Used to tie services to scheduled maintenance so that one maintenance can impact multiple services"""

    service_name = models.ForeignKey(Service)
    maintenance = models.ForeignKey(Maintenance)

    # Represent the objects as unicode
    def __unicode__(self):
        return u'%s %s' % (self.service_name,self.maintenance)


class Report(models.Model):
    """User reported issues"""

    def _upload_to(instance, filename):
        """Rename uploaded images to a random (standard) name"""

        # Setup the file path to be unique so we don't fill up directories
        file_path = time.strftime('%Y/%m/%d')

        # Create a unique filename
        #instance.uuid = uuid.uuid4().hex
        file_name = uuid.uuid4().hex

        # Save the original extension, if its there
        extension = os.path.splitext(filename)[1]

        # Return the path and file
        return 'screenshots/%s/%s%s' % (file_path,file_name,extension)

    date = models.DateTimeField(null=False,blank=False)
    name = models.CharField(null=False,blank=False,max_length=50)
    email = models.CharField(null=False,blank=False,max_length=50)
    description = models.CharField(null=False,blank=False,max_length=160)
    additional = models.CharField(blank=True,max_length=1000)
    screenshot1 = models.ImageField(upload_to=_upload_to)
    screenshot2 = models.ImageField(upload_to=_upload_to)
