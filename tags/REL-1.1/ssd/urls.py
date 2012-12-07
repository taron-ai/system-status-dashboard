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


from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/',          include(admin.site.urls)),
    url(r'^$',               'ssd.main.views.main.index'),
    url(r'^create$',         'ssd.main.views.main.create'),
    url(r'^detail$',         'ssd.main.views.main.detail'),
    url(r'^escalation$',     'ssd.main.views.main.escalation'),
    url(r'^report$',         'ssd.main.views.main.report'),
    url(r'^rsearch$',        'ssd.main.views.search.rsearch'),
    url(r'^search$',         'ssd.main.views.search.search'),
    url(r'^rsearch_recent$', 'ssd.main.views.search.rsearch_recent'),
    url(r'^update$',         'ssd.main.views.main.update'),
    url(r'^prefs/timezone$', 'ssd.main.views.prefs.timezone'),
    url(r'^prefs/jump$',     'ssd.main.views.prefs.jump'),
)
