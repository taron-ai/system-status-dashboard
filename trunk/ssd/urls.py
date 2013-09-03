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

    # SSD Admin Site
    url(r'^admin',              'ssd.main.views.admin.index'),

    # Main
    url(r'^$',                  'ssd.main.views.main.index'),
    url(r'^i_detail$',          'ssd.main.views.main.i_detail'),
    url(r'^escalation$',        'ssd.main.views.main.escalation'),
    url(r'^m_detail$',          'ssd.main.views.main.m_detail'),

    # Configuration
    url(r'^config$',            'ssd.main.views.config.config'),
    url(r'^contacts$',          'ssd.main.views.config.contacts'),
    url(r'^contacts_modify$',   'ssd.main.views.config.contacts_modify'),
    url(r'^recipients$',        'ssd.main.views.config.recipients'),
    url(r'^rm_recipients$',     'ssd.main.views.config.rm_recipients'),
    url(r'^rm_services$',       'ssd.main.views.config.rm_services'),
    url(r'^services$',          'ssd.main.views.config.services'),

    # Search
    url(r'^events$',            'ssd.main.views.search.events'),
    url(r'^isearch$',           'ssd.main.views.search.isearch'),
    url(r'^igsearch$',          'ssd.main.views.search.igsearch'),
    url(r'^mrusearch$',         'ssd.main.views.search.mrusearch'),
    url(r'^msearch$',           'ssd.main.views.search.msearch'),
    url(r'^rsearch$',           'ssd.main.views.search.rsearch'),
    url(r'^rsearch_recent$',    'ssd.main.views.search.rsearch_recent'),

    # Preferences
    url(r'^prefs/timezone$',    'ssd.main.views.prefs.timezone'),
    url(r'^prefs/jump$',        'ssd.main.views.prefs.jump'),

    # Events
    url(r'^i_delete$',          'ssd.main.views.events.i_delete'),
    url(r'^i_update$',          'ssd.main.views.events.i_update'),
    url(r'^incident$',          'ssd.main.views.events.incident'),
    url(r'^m_delete$',          'ssd.main.views.events.m_delete'),
    url(r'^m_email$',           'ssd.main.views.events.m_email'),
    url(r'^m_update$',          'ssd.main.views.events.m_update'),
    url(r'^maintenance$',       'ssd.main.views.events.maintenance'),
    url(r'^report$',            'ssd.main.views.events.report'),

)
