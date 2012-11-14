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


class EmailField(forms.Field):
    """Generic textfield for a user's email address

       Requirements:
          - Must not be empty
          - Must contain only alpha-numeric and '@.-'

    """

    def validate(self, value):
        if value is None or value == '':
            raise forms.ValidationError('No data entered')
        if not re.match(r'^[0-9a-zA-Z@\.\-]+$', value):
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
    email = EmailField()
    description = DescriptionField()
    additional = AdditionalDescriptionField()

class SearchForm(forms.Form):
    """Form for searching through incidents
       This form will be used by incident searches and report searches
       so only dates are mandatory

    """

    date_from = DateField()
    date_to = DateField()
