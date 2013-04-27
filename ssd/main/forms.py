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


class MultipleServiceField(forms.Field):
    """Multiple service checkbox/input field

       Requirements:
          - Must not be empty (at least one service must be provided)

    """

    def validate(self, value):
        if value is None or value == '':
            raise forms.ValidationError('No service entered')


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


class DeleteEventForm(forms.Form):
    """Form for deleting an existing event (incident or maintenance)"""

    id = forms.IntegerField()


class UpdateTZForm(forms.Form):
    """Form for setting or updating the timezone"""

    timezone = forms.CharField(required=True)


class JumpToForm(forms.Form):
    """Form for setting the calendar view date"""

    jump_to = forms.DateField(required=True,input_formats=['%Y-%m-%d'])


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

    s_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    s_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    e_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    e_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    status = forms.CharField(required=False)
    text = forms.CharField(required=False)


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
    instr_maintenance_update = forms.CharField(required=False)
    email_format_incident = forms.IntegerField(required=False)
    email_format_maintenance = forms.IntegerField(required=False)

    # Override the form clean method - there is some special logic to validate 
    # scheduling a maintenance and we need access to multiple values    # Logic:
    def clean(self):
        cleaned_data = super(ConfigForm, self).clean()
        enable_uploads = cleaned_data.get('enable_uploads')
        upload_path = cleaned_data.get('upload_path')
        file_upload_size = cleaned_data.get('file_upload_size')

        # File uploads must be at least 100
        if file_upload_size < 100:
            self._errors["file_upload_size"] = self.error_class(['Size must be at least 100'])

        # If uploads are enabled, so must be the upload_path and file_upload_size
        if enable_uploads and not upload_path:
            self._errors["upload_path"] = self.error_class(['You must set a file upload path'])
            
        # Return the full collection of cleaned data
        return cleaned_data


class AddIncidentForm(forms.Form):
    """Form for adding a new incident (by an administrator)"""

    date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    time = forms.TimeField(required=True,input_formats=['%H:%M'])
    detail = forms.CharField(required=True)
    service = MultipleServiceField()
    broadcast = forms.BooleanField(required=False)
    recipient_id = forms.IntegerField(required=False)

    # Override the form clean method - there is some special logic to 
    # adding an incident and we need access to multiple values
    # to do it.

    def clean(self):
        cleaned_data = super(AddIncidentForm, self).clean()
        detail = cleaned_data.get('detail')
        broadcast = cleaned_data.get('broadcast')
        recipient_id = cleaned_data.get('recipient_id')

        # If an email broadcast is requested, an email address must accompany it
        if broadcast and not recipient_id:
            self._errors["broadcast"] = self.error_class(['Cannot broadcast if no address selected'])
        
        # Is the detail field the default text?
        d_detail = Config.objects.filter(config_name='instr_incident_description').values('config_value')[0]['config_value']
        if detail == d_detail:
            self._errors["detail"] = self.error_class(['Please provide a description'])

        # Return the full collection of cleaned data
        return cleaned_data


class UpdateIncidentForm(forms.Form):
    """Form for updating an existing incident"""

    date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    time = forms.TimeField(required=True,input_formats=['%H:%M'])
    update = forms.CharField(required=True)
    service = MultipleServiceField()
    broadcast = forms.BooleanField(required=False)
    closed = forms.BooleanField(required=False)
    recipient_id = forms.IntegerField(required=False)
    id = forms.IntegerField()

    # Override the form clean method - there is some special logic to 
    # creating an incident and we need access to multiple values
    # to do it.

    def clean(self):
        cleaned_data = super(UpdateIncidentForm, self).clean()
        update = cleaned_data.update('update')
        broadcast = cleaned_data.get('broadcast')
        recipient_id = cleaned_data.get('recipient_id')

        # If an email broadcast is requested, an email address must accompany it
        if broadcast and not recipient_id:
            self._errors["broadcast"] = self.error_class(['Cannot broadcast if no address selected'])
        
        # Is it the default text?
        d_update = Config.objects.filter(config_name='instr_incident_update').values('config_value')[0]['config_value']
        if update == d_update:
            self._errors["update"] = self.error_class(['Please provide an update'])

        # Return the full collection of cleaned data
        return cleaned_data


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
    broadcast = forms.BooleanField(required=False)
    recipient_id = forms.IntegerField(required=False)

    # Override the form clean method - there is some special logic to 
    # scheduling a maintenance and we need access to multiple values
    # to do it.

    def clean(self):
        cleaned_data = super(AddMaintenanceForm, self).clean()
        impact = cleaned_data.get('impact')
        coordinator = cleaned_data.get('coordinator')
        description = cleaned_data.get('description')
        broadcast = cleaned_data.get('broadcast')
        recipient_id = cleaned_data.get('recipient_id')

        # If email broadcast is selected, an email address also must be
        if broadcast and not recipient_id:
            self._errors["broadcast"] = self.error_class(['Cannot broadcast if no address selected'])
        
        # Is the description field the default text?
        d_description = Config.objects.filter(config_name='instr_maintenance_description').values('config_value')[0]['config_value']
        if description == d_description:
            self._errors["description"] = self.error_class(['Please provide a maintenance description'])

        # Is the impact field the default text?
        d_impact = Config.objects.filter(config_name='instr_maintenance_impact').values('config_value')[0]['config_value']
        if impact == d_impact:
            self._errors["impact"] = self.error_class(['Please provide an impact analysis'])

        # Is the coordinator field the default text?
        d_coordinator = Config.objects.filter(config_name='instr_maintenance_coordinator').values('config_value')[0]['config_value']
        if coordinator == d_coordinator:
            self._errors["coordinator"] = self.error_class(['Please provide a maintenance coordinator'])
            
        # Return the full collection of cleaned data
        return cleaned_data


class UpdateMaintenanceForm(forms.Form):
    """Form for updating maintenance"""

    s_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    s_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    e_date = forms.DateField(required=True,input_formats=['%Y-%m-%d'])
    e_time = forms.TimeField(required=True,input_formats=['%H:%M'])
    description = forms.CharField(required=True)
    impact = forms.CharField(required=True)
    coordinator = forms.CharField(required=True)
    update = forms.CharField(required=True)
    service = MultipleServiceField()
    id = forms.IntegerField(required=True)
    started = forms.CharField(required=False)
    completed = forms.CharField(required=False)
    broadcast = forms.BooleanField(required=False)
    recipient_id = forms.IntegerField(required=False)
    

    # Override the form clean method - to validate the special logic in this form

    def clean(self):
        cleaned_data = super(UpdateMaintenanceForm, self).clean()
        broadcast = cleaned_data.get("broadcast")
        recipient_id = cleaned_data.get("recipient_id")
        started = cleaned_data.get('started')
        completed = cleaned_data.get('completed')
        description = cleaned_data.get('description')
        impact = cleaned_data.get('impact')
        coordinator = cleaned_data.get('coordinator')
        update = cleaned_data.get('update')

        # If an email broadcast is requested but no email address is selected, error
        if broadcast and not recipient_id:
            # Set custom error messages
            self._errors["broadcast"] = self.error_class(['Cannot broadcast if no address selected'])
        
        # If its completed, make sure its started
        if completed and not started:
            # Set custom error messages
            self._errors['started'] = self.error_class(['Maintenance cannot be completed if not started'])
            self._errors['completed'] = self.error_class(['Maintenance cannot be completed if not started'])

        # Make sure the description field is not default text
        d_description = Config.objects.filter(config_name='instr_maintenance_description').values('config_value')[0]['config_value']
        if description == d_description:
            self._errors['description'] = self.error_class(['You must enter a description (reset to previous value)'])

        # Make sure the impact field is not default text
        d_impact = Config.objects.filter(config_name='instr_maintenance_impact').values('config_value')[0]['config_value']
        if impact == d_impact:
            self._errors['impact'] = self.error_class(['You must enter an impact analysis (reset to previous value)'])

        # Make sure the coordinator field is not default text
        d_coordinator = Config.objects.filter(config_name='instr_maintenance_coordinator').values('config_value')[0]['config_value']
        if coordinator == d_coordinator:
            self._errors['coordinator'] = self.error_class(['You must enter a maintenance coordinator (reset to previous value)'])

        # Make sure the update field is not default text
        d_update = Config.objects.filter(config_name='instr_maintenance_update').values('config_value')[0]['config_value']
        if update == d_update:
            self._errors['update'] = self.error_class(['You must enter an update'])
            
        # Return the full collection of cleaned data
        return cleaned_data