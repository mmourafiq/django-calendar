# -*- coding: utf-8 -*-
'''
Created on Mar 20, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''
from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _
from calendars.models.cals import Occurrence


class OccurrenceForm(forms.ModelForm):
    start = forms.DateTimeField()
    end = forms.DateTimeField()
    
    class Meta:
        model = Occurrence
        exclude = ('original_start', 'original_end', 'event', 'cancelled')
        
    def clean_end(self):
        if self.cleaned_data['end'] <= self.cleaned_data['start']:
            raise forms.ValidationError(_("The end time must be later than start time."))
        return self.cleaned_data['end']
