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


from django.conf.urls import patterns, include, url
from django.contrib import admin
from ssd.main.views import main
admin.autodiscover()

urlpatterns = patterns('',

    # Main Dashboard (cache this page for 60 seconds)
    url(r'^$',                              'ssd.main.views.main.index'),
    
    # Escalation Path
    url(r'^escalation$',                    'ssd.main.views.escalation.escalation'),

    # Configuration
    url(r'^config$',                        'ssd.main.views.config.config'),

    # Search
    #url(r'^search$',                       'ssd.main.views.search.search'),
    url(r'^gsearch$',                       'ssd.main.views.search.gsearch'),

    # Preferences
    url(r'^prefs/timezone$',                'ssd.main.views.prefs.timezone'),
    url(r'^prefs/jump$',                    'ssd.main.views.prefs.jump'),

    # Incident Events
    url(r'^i_detail$',                      'ssd.main.views.incidents.i_detail'),

    # Maintenance Events
    url(r'^m_detail$',                      'ssd.main.views.maintenance.m_detail'),

    # Incident Reports
    url(r'^ireport$',                       'ssd.main.views.ireport.ireport'),



    # -- from here down, it's all admin functionality -- #

   # User login
    url(r'^accounts/login/$',               'django.contrib.auth.views.login'),

    # User logout
    url(r'^accounts/logout/$',              'django.contrib.auth.views.logout',{'next_page': '/'}),

    # Standard Django admin site
    url(r'^djadmin/',                       include(admin.site.urls)),

    # SSD Admin Homepage
    url(r'^admin$',                         'ssd.main.views.admin.main'),

    # Incident Events (admin functionality)
    url(r'^admin/incident$',                'ssd.main.views.incidents.incident'),
    url(r'^admin/i_delete$',                'ssd.main.views.incidents.i_delete'),
    url(r'^admin/i_list$',                  'ssd.main.views.incidents.i_list'),
    url(r'^admin/i_update$',                'ssd.main.views.incidents.i_update'),
    
    # Maintenance Events (admin functionality)
    url(r'^admin/maintenance$',             'ssd.main.views.maintenance.maintenance'),
    url(r'^admin/m_delete$',                'ssd.main.views.maintenance.m_delete'),
    url(r'^admin/m_list$',                  'ssd.main.views.maintenance.m_list'),
    url(r'^admin/m_email$',                 'ssd.main.views.maintenance.m_email'),
    url(r'^admin/m_update$',                'ssd.main.views.maintenance.m_update'),

    # Email Configuration (admin functionality)
    url(r'^admin/email_config$',            'ssd.main.views.email.email_config'),
    url(r'^admin/email_delete$',            'ssd.main.views.email.email_delete'),
    url(r'^admin/email_recipients$',        'ssd.main.views.email.email_recipients'),
 
    # Services Configuration (admin functionality)
    url(r'^admin/services$',                'ssd.main.views.services.services'),
    url(r'^admin/services_delete$',         'ssd.main.views.services.services_delete'),

    # Messages Configuration (admin functionality)
    url(r'^admin/messages_config$',         'ssd.main.views.messages.messages_config'),

    # Logo Configuration (admin functionality)
    url(r'^admin/logo_config$',             'ssd.main.views.logo.logo_config'),

    # Url Configuration (admin functionality)
    url(r'^admin/systemurl_config$',        'ssd.main.views.systemurl.systemurl_config'),

    # Incident Reports (admin functionality)
    url(r'^admin/ireport_config$',          'ssd.main.views.ireport.ireport_config'),
    url(r'^admin/ireport_detail$',          'ssd.main.views.ireport.ireport_detail'),
    url(r'^admin/ireport_delete$',          'ssd.main.views.ireport.ireport_delete'),
    url(r'^admin/ireport_list$',            'ssd.main.views.ireport.ireport_list'),

    # Escalation
    url(r'^admin/escalation_config$',       'ssd.main.views.escalation.escalation_config'),
    url(r'^admin/escalation_contacts$',     'ssd.main.views.escalation.escalation_contacts'),
    url(r'^admin/escalation_modify$',       'ssd.main.views.escalation.escalation_modify'),
)
