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


"""Form and Form Field classes for the SSD project

   All fields should be defined first, with forms to follow.  Form fields
   have basic validation rules and DJango takes care of escaping anything
   dangerous automatically.

"""


import re
from django import forms
from django.conf import settings
from ssd.main.models import Config


### VALIDATORS ###

def file_size(value):
    """Ensure file size is below maximum allowed"""

    if value.size > settings.MAX_FILE_SIZE * 1024 * 1024:
        raise forms.ValidationError('File too large - please reduce the size of the upload to below %s MB' % settings.MAX_FILE_SIZE)


### FIELDS ###

class IdField(forms.Field):
    """A numeric ID field

       Requirements:
          - Must not be empty
          - Must be a number

    """

    def validate(self, value):
        if value is None or value == '':
            raise forms.ValidationError('No id selected')
        if not re.match(r'^\d+$', value):
            raise forms.ValidationError('Improperly formatted id')


class DateField(forms.Field):
    """A date field

       Requirements:
          - Must not be empty
          - Must be in SQL format (yyyy-mm-dd)

    """

    def validate(self, value):
        if value is None or value == '':
            raise forms.ValidationError('No date selected')
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', value):
            raise forms.ValidationError('Improperly formatted date')


class TimeField(forms.Field):
    """A time field

       Requirements:
          - Must not be empty
          - Must be in the following format (hh:mm)

    """

    def validate(self, value):
        if value is None or value == '':
            raise forms.ValidationError('No time selected')
        if not re.match(r'^\d{2}:\d{2}$', value):
            raise forms.ValidationError('Improperly formatted time')


class DetailField(forms.Field):
    """A generic text field

       Requirements:
          - Must not be empty

    """

    def validate(self, value):
        if value is None or value == '':
            raise forms.ValidationError('No description provided')


class MultipleServiceField(forms.Field):
    """Multiple checkbox field

       Requirements:
          - Must not be empty (at least one checkbox must be checked)

    """

    def validate(self, value):
        if value is None or value == '':
            raise forms.ValidationError('No services selected')


class TZField(forms.Field):
    """A timezone field, in a select

       Requirements:
          - Must not be empty
          - Must contain only alpha-numeric and '\-'

    """

    def validate(self, value):
        if value is None or value == '':
            raise forms.ValidationError('No timezone selected')
        if not re.match(r'^[0-9a-zA-Z/\-]+$', value):
            raise forms.ValidationError('Improperly formatted timezone')


class NameField(forms.Field):
    """Generic textfield for a user's name

       Requirements:
          - Must not be empty
          - Must contain only alpha-numeric

    """

    def validate(self, value):
        if value is None or value == '':
            raise forms.ValidationError('No data entered')
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise forms.ValidationError('Invalid characters entered')


class DescriptionField(forms.Field):
    """Generic textarea for the incident description

       Requirements:
          - Must not be empty
          - Must not be greater than 160 characters

    """

    def validate(self, value):
        if len(value) > 160:
            raise forms.ValidationError('Data entered is greater than 160 characters')

        if value is None or value == '':
            raise forms.ValidationError('No data entered')


class AdditionalDescriptionField(forms.Field):
    """Generic textarea for additional information about the incident

       Requirements:
          - Must not be empty
          - Must not be greater than 1000 characters

    """

    def validate(self, value):
        if len(value) > 1000:
            raise forms.ValidationError('Data entered is greater than 1000 characters')


class SearchField(forms.Field):
    """Generic textarea search text

       Requirements:
          - Must not be greater than 100 characters

    """

    def validate(self, value):
        if len(value) > 100:
            raise forms.ValidationError('Data entered is greater than 100 characters')


### FORMS ###


class AddIncidentForm(forms.Form):
    """Form for adding a new incident (by an administrator)"""

    date = DateField()
    time = TimeField()
    detail = DetailField()
    service = MultipleServiceField()


class UpdateIncidentForm(forms.Form):
    """Form for updating an existing incident"""

    date = DateField()
    time = TimeField()
    detail = DetailField()
    id = IdField()
    service = MultipleServiceField()


class UpdateTZForm(forms.Form):
    """Form for setting or updating the timezone"""

    timezone = TZField()


class JumpToForm(forms.Form):
    """Form for setting the calendar view date"""

    jump_to = DateField()


class ReportIncidentForm(forms.Form):
    """Form for reporting an incident (by a user)"""

    name = NameField()
    email = forms.EmailField()
    description = DescriptionField()
    additional = AdditionalDescriptionField()
    screenshot1 = forms.ImageField(required=False,validators=[file_size])
    screenshot2 = forms.ImageField(required=False,validators=[file_size])


class SearchForm(forms.Form):
    """Form for searching through incidents
       This form will be used by incident searches and report searches
       so only dates are mandatory

    """

    date_from = DateField()
    date_to = DateField()


class ConfigAdminForm(forms.ModelForm):
    """DJango form for creating a larger textarea to make it easier
       to create/edit the configs

    """

    config_value = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Config


class ConfigForm(forms.Form):
    """Form for updating configs"""

    company = forms.CharField(required=False)
    greeting_new = forms.CharField(required=False)
    greeting_update = forms.CharField(required=False)
    email_to = forms.EmailField(required=False)
    email_from = forms.EmailField(required=False)
    email_subject = forms.CharField(required=False)
    maintenance = forms.CharField(required=False)
    page_to = forms.EmailField(required=False)
    message_success = forms.CharField(required=False)
    message_error = forms.CharField(required=False)
    escalation = forms.CharField(required=False)
    report_incident_help = forms.CharField(required=False)
    create_incident_help = forms.CharField(required=False)
    logo_display = forms.IntegerField(required=False)
    logo_url = forms.CharField(required=False)
    nav_display = forms.IntegerField(required=False)
    contacts_display = forms.IntegerField(required=False)
    report_incident_display = forms.IntegerField(required=False)


class AddMaintenanceForm(forms.Form):
    """Form for adding maintenance"""

    s_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    s_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    e_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    e_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    description = forms.CharField(required=True)
    impact = forms.CharField(required=True)
    coordinator = forms.CharField(required=True)
    service = MultipleServiceField()
    

class UpdateMaintenanceForm(forms.Form):
    """Form for updating maintenance"""

    s_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    s_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    e_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    e_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    description = forms.CharField(required=True)
    impact = forms.CharField(required=True)
    coordinator = forms.CharField(required=True)
    update = forms.CharField(required=False)
    service = MultipleServiceField()
    id = forms.IntegerField(required=True)
    started = forms.CharField(required=False)
    completed = forms.CharField(required=False)

    # Override the form clean method - there is some special logic to 
    # starting/completing maintenances and we need access to multiple values
    # to do it.
    #
    # Logic:
    #  - Maintenance can be started and completed
    #  - Maintenance cannot be completed if its not also started
    def clean(self):
        cleaned_data = super(UpdateMaintenanceForm, self).clean()
        started = cleaned_data.get("started")
        completed = cleaned_data.get("completed")

        if completed and not started:
            
            # Set custom error messages
            self._errors["started"] = self.error_class(['Maintenance cannot be completed if not started'])
            self._errors["completed"] = self.error_class(['Maintenance cannot be completed if not started'])
            
        # Return the full collection of cleaned data
        return cleaned_data