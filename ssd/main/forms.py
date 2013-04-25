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


class IncidentDetailField(forms.Field):
    """An incident detail text field

       Requirements:
          - Must not be empty
          - Must not contain the default text for this field

    """

    def validate(self, value):

        # Is it empty?
        if value is None or value == '':
            raise forms.ValidationError('No description provided')

        # Is it the default text?
        default = Config.objects.filter(config_name='instr_incident_description').values('config_value')[0]['config_value']
        if value == default:
            raise forms.ValidationError('No description provided')


class MaintenanceDescriptionField(forms.Field):
    """A maintenance description text field

       Requirements:
          - Must not be empty
          - Must not contain the default text for this field

    """

    def validate(self, value):

        # Is it empty?
        if value is None or value == '':
            raise forms.ValidationError('No description provided')

        # Is it the default text?
        default = Config.objects.filter(config_name='instr_maintenance_description').values('config_value')[0]['config_value']
        if value == default:
            raise forms.ValidationError('No description provided')


class MaintenanceImpactField(forms.Field):
    """A maintenance impact analysis text field

       Requirements:
          - Must not be empty
          - Must not contain the default text for this field

    """

    def validate(self, value):

        # Is it empty?
        if value is None or value == '':
            raise forms.ValidationError('No description provided')

        # Is it the default text?
        default = Config.objects.filter(config_name='instr_maintenance_impact').values('config_value')[0]['config_value']
        if value == default:
            raise forms.ValidationError('No impact provided')


class MaintenanceCoordinatorField(forms.Field):
    """A maintenance coordinator text field

       Requirements:
          - Must not be empty
          - Must not contain the default text for this field

    """

    def validate(self, value):

        # Is it empty?
        if value is None or value == '':
            raise forms.ValidationError('No description provided')

        # Is it the default text?
        default = Config.objects.filter(config_name='instr_maintenance_coordinator').values('config_value')[0]['config_value']
        if value == default:
            raise forms.ValidationError('No coordinator provided')


class UpdateField(forms.Field):
    """An incident update text field

       Requirements:
          - Must not be empty
          - Must not contain the default text for this field

    """

    def validate(self, value):

        # Is it empty?
        if value is None or value == '':
            raise forms.ValidationError('No update provided')

        # Is it the default text?
        default = Config.objects.filter(config_name='instr_incident_update').values('config_value')[0]['config_value']
        if value == default:
            raise forms.ValidationError('No update provided')


class MultipleServiceField(forms.Field):
    """Multiple service checkbox/input field

       Requirements:
          - Must not be empty (at least one service must be provided)

    """

    def validate(self, value):
        if value is None or value == '':
            raise forms.ValidationError('No service entered')


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

    date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    time = forms.TimeField(required=True,input_formats=['%H:%M'])
    detail = IncidentDetailField()
    service = MultipleServiceField()
    broadcast = forms.BooleanField(required=False)
    recipient_id = forms.IntegerField(required=False)

    # Override the form clean method - there is some special logic to 
    # creating an incident and we need access to multiple values
    # to do it.
    #
    # Logic:
    #  - If broadcast email is being requested, an email address must be provided
    def clean(self):
        cleaned_data = super(AddIncidentForm, self).clean()
        broadcast = cleaned_data.get("broadcast")
        recipient_id = cleaned_data.get("recipient_id")

        if broadcast and not recipient_id:
            
            # Set custom error messages
            self._errors["broadcast"] = self.error_class(['Cannot broadcast if no address selected'])
            
        # Return the full collection of cleaned data
        return cleaned_data


class UpdateIncidentForm(forms.Form):
    """Form for updating an existing incident"""

    date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    time = forms.TimeField(required=True,input_formats=['%H:%M'])
    update = UpdateField()
    service = MultipleServiceField()
    broadcast = forms.BooleanField(required=False)
    closed = forms.BooleanField(required=False)
    recipient_id = forms.IntegerField(required=False)
    id = forms.IntegerField()

    # Override the form clean method - there is some special logic to 
    # creating an incident and we need access to multiple values
    # to do it.
    #
    # Logic:
    #  - If broadcast email is being requested, an email address must be provided
    def clean(self):
        cleaned_data = super(UpdateIncidentForm, self).clean()
        broadcast = cleaned_data.get("broadcast")
        recipient_id = cleaned_data.get("recipient_id")

        if broadcast and not recipient_id:
            
            # Set custom error messages
            self._errors["broadcast"] = self.error_class(['Cannot broadcast if no address selected'])
            
        # Return the full collection of cleaned data
        return cleaned_data


class DeleteIncidentForm(forms.Form):
    """Form for deleting an existing incident"""

    id = forms.IntegerField()


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

    recipient_name = forms.CharField(required=False)
    
    greeting_incident_new = forms.CharField(required=False)
    greeting_incident_update = forms.CharField(required=False)
    greeting_maintenance_new = forms.CharField(required=False)
    greeting_maintenance_update = forms.CharField(required=False)
    email_from = forms.EmailField(required=False)
    email_subject_incident = forms.CharField(required=False)
    email_subject_maintenance = forms.CharField(required=False)
    alert = forms.CharField(required=False)
    display_alert = forms.CharField(required=False)
    recipient_pager = forms.EmailField(required=False)
    message_success = forms.CharField(required=False)
    message_error = forms.CharField(required=False)
    escalation = forms.CharField(required=False)
    logo_display = forms.IntegerField(required=False)
    logo_url = forms.CharField(required=False)
    ssd_url = forms.CharField(required=False)
    nav_display = forms.IntegerField(required=False)
    contacts_display = forms.IntegerField(required=False)
    report_incident_display = forms.IntegerField(required=False)
    instr_sched_maint = forms.CharField(required=False)
    display_sched_maint_instr = forms.IntegerField(required=False)
    instr_report_incident = forms.CharField(required=False)
    display_report_incident_instr = forms.IntegerField(required=False)
    instr_create_incident = forms.CharField(required=False)
    display_create_incident_instr = forms.IntegerField(required=False)
    enable_uploads = forms.IntegerField(required=False)
    upload_path = forms.CharField(required=False)
    file_upload_size = forms.IntegerField(required=False)
    instr_incident_description = forms.CharField(required=False)
    instr_incident_update = forms.CharField(required=False)
    instr_maintenance_description = forms.CharField(required=False)
    instr_maintenance_impact = forms.CharField(required=False)
    instr_maintenance_coordinator = forms.CharField(required=False)
    email_format_incident = forms.IntegerField(required=False)
    email_format_maintenance = forms.IntegerField(required=False)


class AddMaintenanceForm(forms.Form):
    """Form for adding maintenance"""

    s_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    s_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    e_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    e_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    description = MaintenanceDescriptionField()
    impact = MaintenanceImpactField()
    coordinator = MaintenanceCoordinatorField()
    service = MultipleServiceField()
    broadcast = forms.BooleanField(required=False)
    recipient_id = forms.IntegerField(required=False)

    # Override the form clean method - there is some special logic to 
    # scheduling a maintenance and we need access to multiple values
    # to do it.
    #
    # Logic:
    #  - If broadcast email is being requested, an email address must be provided
    def clean(self):
        cleaned_data = super(AddMaintenanceForm, self).clean()
        broadcast = cleaned_data.get("broadcast")
        recipient_id = cleaned_data.get("recipient_id")

        if broadcast and not recipient_id:
            
            # Set custom error messages
            self._errors["broadcast"] = self.error_class(['Cannot broadcast if no address selected'])
            
        # Return the full collection of cleaned data
        return cleaned_data


class AddRecipientForm(forms.Form):
    """Form for adding email addresses"""

    recipient = forms.EmailField(required=True)


class AddServiceForm(forms.Form):
    """Form for adding services"""

    service = MultipleServiceField()


class RemoveServiceForm(forms.Form):
    """Form for removing services"""

    id = MultipleServiceField()


class RemoveRecipientForm(forms.Form):
    """Form for removing recipients"""

    id = MultipleServiceField()


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