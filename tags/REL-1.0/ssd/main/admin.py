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


"""DJango admin configuration for the SSD Project

   Any models that need to be manipulated in the SSD DJango web admin pages 
   will need specific configurations listed below (this is not required).
   They will also need to be registered with the admin

"""


from ssd.main.models import Config
from ssd.main.models import Service
from ssd.main.models import Incident
from ssd.main.models import Incident_Update
from ssd.main.models import Service_Issue
from django.contrib import admin


class ConfigAdmin(admin.ModelAdmin):
    """Configuration parameters administration"""

    fieldsets = [
       ('Configuration Option',{'fields':['config_name','config_value']})
    ]

    list_display = ('config_name','config_value')


class ServiceAdmin(admin.ModelAdmin):
    """Services administration"""

    fieldsets = [
       ('Service',{'fields':['service_name']})
    ]


class IncidentAdmin(admin.ModelAdmin):
    """Incident administration"""

    fieldsets = [
       ('Incident',{'fields':['date','detail','closed']})
    ]

    list_display = ('date','detail','closed')


class IncidentUpdateAdmin(admin.ModelAdmin):
    """Incident updates administration"""

    fieldsets = [
       ('Incident Update',{'fields':['date','incident','detail']})
    ]

    list_display = ('date','incident','detail')


class ServiceIssueAdmin(admin.ModelAdmin):
    """Service issues administration"""


    fieldsets = [
       ('Service Issue',{'fields':['service_name','incident']})
    ]

    list_display = ('service_name','incident')


# Register the classes with the admin
admin.site.register(Config,ConfigAdmin)
admin.site.register(Service,ServiceAdmin)
admin.site.register(Incident,IncidentAdmin)
admin.site.register(Incident_Update,IncidentUpdateAdmin)
admin.site.register(Service_Issue,ServiceIssueAdmin)
