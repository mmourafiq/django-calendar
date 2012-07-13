# -*- coding: utf-8 -*-
'''
Created on Mar 20, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''

from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _
from calendars.settings import *

class RecursionForm(forms.Form):
    """A form for defining recursion detail"""
    add_recursion = forms.BooleanField(widget=forms.CheckboxInput, initial=False, required=False, label=_('Repetition'))
    recursion_frequency = forms.ChoiceField(widget=forms.Select(), choices=freqs,
                                            required=False, label=_('Frequency'))
    recursion_interval = forms.IntegerField(required=False)
    recursion_count = forms.IntegerField(required=False, widget=forms.HiddenInput, label=_('Count'))
    recursion_byweekday = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                        choices=PERIOD_DAY, required=False, label=_('By weekday'))
    recursion_bymonthday = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                        choices=PERIOD_DAY, required=False, label=_('By monthday'))    
    
    def __init__(self, *args, **kwargs):
        """ define the a recursion class for this form fields"""
        super(RecursionForm, self).__init__(*args, **kwargs)    
        self.fields['add_recursion'].widget.attrs['class'] = 'recursion_check'        
        self.fields['recursion_frequency'].widget.attrs['class'] = 'recursion'        
        self.fields['recursion_count'].widget.attrs['class'] = 'recursion'
        self.fields['recursion_byweekday'].widget.attrs['class'] = 'recursion'
        self.fields['recursion_bymonthday'].widget.attrs['class'] = 'recursion'

    def clean_recursion_interval(self):
        """return the recursion interval 
            ->'the event will be repeated every recursion interval
            The interval between each freq iteration. For example, 
            when using YEARLY, an interval of 2 means once every two years, but with HOURLY, 
            it means once every two hours. The default interval is 1. '
        """
        interval = self.cleaned_data['recursion_interval']
        if interval:
            return "interval:%s;" % interval
        return ''
    
    def clean_recursion_count(self):
        """ return the recursion count
            ->'How many occurrences will be generated. '
        """
        count = self.cleaned_data['recursion_count']
        if count:
            return "count:%s;" % count
        return ''
        
    def clean_recursion_byweekday(self):
        """Return the day list on which we should be applying the recursion"""              
        weekdays = self.cleaned_data['recursion_byweekday']
        if weekdays: 
            days = "byweekday:" 
            for day in weekdays:
                days += day + ','
            return days[:-1] + ';'        
        return ''
    
    def clean_recursion_bymonthday(self):
        """Return the day list on which we should be applying the recursion"""              
        monthdays = self.cleaned_data['recursion_bymonthday']
        if monthdays: 
            days = "bymonthday:" 
            for day in monthdays:
                days += day + ','
            return days[:-1] + ';'        
        return ''    
