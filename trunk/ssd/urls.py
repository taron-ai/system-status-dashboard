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
admin.autodiscover()

urlpatterns = patterns('',
   # User login
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),

    # User logout
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',{'next_page': '/'}),

    # Standard admin site
    url(r'^djadmin/',             include(admin.site.urls)),



    # Main
    url(r'^$',                  'ssd.main.views.main.index'),
    
    # Escalation
    url(r'^escalation$',        'ssd.main.views.escalation.escalation'),

    # Configuration
    url(r'^config$',            'ssd.main.views.config.config'),
    url(r'^contacts$',          'ssd.main.views.config.contacts'),
    url(r'^contacts_modify$',   'ssd.main.views.config.contacts_modify'),
    url(r'^email$',             'ssd.main.views.config.email'),
    url(r'^rm_email$',          'ssd.main.views.config.rm_email'),
    url(r'^rm_services$',       'ssd.main.views.config.rm_services'),
    url(r'^services$',          'ssd.main.views.config.services'),

    # Search
    #url(r'^search$',            'ssd.main.views.search.search'),
    url(r'^igsearch$',          'ssd.main.views.search.igsearch'),

    # Preferences
    url(r'^prefs/timezone$',    'ssd.main.views.prefs.timezone'),
    url(r'^prefs/jump$',        'ssd.main.views.prefs.jump'),

    # Incident Events
    url(r'^i_detail$',          'ssd.main.views.incidents.i_detail'),

    # Maintenance Events
    url(r'^m_detail$',          'ssd.main.views.maintenance.m_detail'),


    # -- from here down, it's all admin functionality -- #

    # SSD Admin Homepage
    url(r'^admin$',              'ssd.main.views.admin.index'),

    # Incident Events (admin functionality)
    url(r'^admin/incident$',          'ssd.main.views.incidents.incident'),
    url(r'^admin/i_delete$',          'ssd.main.views.incidents.i_delete'),
    url(r'^admin/i_update$',          'ssd.main.views.incidents.i_update'),
    
    # Maintenance Events (admin functionality)
    url(r'^admin/maintenance$',       'ssd.main.views.maintenance.maintenance'),
    url(r'^admin/m_delete$',          'ssd.main.views.maintenance.m_delete'),
    url(r'^admin/m_email$',           'ssd.main.views.maintenance.m_email'),
    url(r'^admin/m_update$',          'ssd.main.views.maintenance.m_update'),
    
    # Incident Reports
    url(r'^report$',            'ssd.main.views.report.report'),

)
