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


class Config(models.Model):
    """Configuration parameters"""

    config_name = models.CharField(max_length=50);
    config_value = models.CharField(max_length=1000);

    # Represent the object as unicode
    def __unicode__(self):
        return u'%s %s' % (self.config_name,self.config_value)


class Service(models.Model):
    """Services that will be monitored"""

    service_name = models.CharField(max_length=50);

    # Represent the object as unicode
    def __unicode__(self):
        return self.service_name


class Incident(models.Model):
    """Incidents that have been logged"""

    date = models.DateTimeField(null=False,blank=False)
    closed = models.DateTimeField(null=True)
    detail = models.CharField(max_length=1000);

    # Represent the objects as unicode
    def __unicode__(self):
        return u'%s,%s' % (self.date,self.detail)


class Incident_Update(models.Model):
    """Updates to incidents"""

    date = models.DateTimeField(null=False,blank=False)
    incident = models.ForeignKey(Incident)
    detail = models.CharField(max_length=1000);

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


class Report(models.Model):
    """User reported issues"""

    date = models.DateTimeField(null=False,blank=False)
    name = models.CharField(null=False,blank=False,max_length=50);
    email = models.CharField(null=False,blank=False,max_length=50);
    description = models.CharField(null=False,blank=False,max_length=160);
    additional = models.CharField(blank=True,max_length=1000);
