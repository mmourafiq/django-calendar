# -*- coding: utf-8 -*-
'''
Created on Mar 20, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''
from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _
import datetime
from calendars.models.cals import Event 
from calendars.fields import CommaSeparatedUserField
from calendars.forms.recursion import RecursionForm
from calendars.settings import *

#@TODO: need to add the cal_place, cal_tips to caleventsform
#@TODO: need to add the forcal_percents to the forcalform

calendar_widget = forms.widgets.DateInput(attrs={'class': 'date-pick'}, format='%m/%d/%Y')
time_widget = forms.widgets.TimeInput(attrs={'class': 'time-pick'})
valid_time_formats = ['%H:%M', '%I:%M%p', '%I:%M %p']

class InviteEventForm(forms.Form):
    """A form to change the invite list for this with cal"""
    invite = CommaSeparatedUserField(label=_(u"Invite"), required=False)
    min_number_guests = forms.IntegerField(initial=0,)
    max_number_guests = forms.IntegerField(initial=0)
    close = forms.BooleanField(required=False, label=_('Friends only'))

class BaseEventForm(RecursionForm, InviteEventForm):  
    start_date = forms.DateField(widget=calendar_widget)
    start_time = forms.TimeField(required=False, widget=time_widget, help_text='ex: 10:30AM', input_formats=valid_time_formats)            
    check_whole_day = forms.BooleanField(initial=False, required=False, label=_("All day"))
    end_date = forms.DateField(required=False, widget=calendar_widget)
    end_time = forms.TimeField(required=False, widget=time_widget, help_text='ex: 10:30AM', input_formats=valid_time_formats)            
    end_recurring_period = forms.DateField(required=False)    
    priority = forms.ChoiceField(widget=forms.RadioSelect(), choices=EVENT_PRIORITY,
                                     initial="2", label=_('Priority'))
    category = forms.ChoiceField(widget=forms.RadioSelect(), choices=EVENT_CATEGORY,
                                     initial="2", label=_('Category'))
    honeypot = forms.CharField(required=False,
                                    label=_('If you enter anything in this field '\
                                            'your comment will be treated as spam'))
    def __init__(self, *args, **kwargs):
        super(BaseEventForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['start_date', 'start_time', 'check_whole_day', 'end_date', 'end_time', 'invite',
                                'min_number_guests', 'max_number_guests', 'close',                                
                                'add_recursion', 'recursion_frequency','end_recurring_period',
                                'recursion_count','recursion_byweekday', 'recursion_bymonthday',
                                'priority', 'category', 'honeypot']      
        self.fields['check_whole_day'].widget.attrs['class'] = 'times'                                        
        self.fields['end_recurring_period'].widget.attrs['class'] = 'recursion'                                    
                
    def clean_start_time(self):
        """cleaning the start time"""
        start_time = self.cleaned_data['start_time']        
        start_date = self.cleaned_data['start_date']        
        if start_time is not None:
            start = datetime.datetime.combine(start_date, start_time)
        else:
            start = datetime.datetime.combine(start_date, datetime.time())        
        return start
        
    def clean_end_time(self):     
        try:
            start_value = self.cleaned_data['start_time']
        except:
            start_value = None 
        if start_value is None:
            raise forms.ValidationError(_("start time is required."))    
        end_time = self.cleaned_data['end_time']
        end_date = self.cleaned_data['end_date']
        if end_date:
            if end_time is not None:
                end_value = datetime.datetime.combine(end_date, end_time)
            else:
                end_value = datetime.datetime.combine(end_date, datetime.time())
        else :
            end_value = None
        if end_value:
            if end_value < start_value:                
                raise forms.ValidationError(_("The end time must be later than start time."))
        check_value = self.cleaned_data["check_whole_day"]                 
        if check_value and check_value is True:            
            if end_value:
                if end_value >= start_value:
                    return datetime.datetime(end_value.year, end_value.month, end_value.day,23, 59, 59)              
            return datetime.datetime(start_value.year, start_value.month, start_value.day,23, 59, 59)
        if end_value :
            return end_value
        else:
            return start_value                                       
        
class EventForm(BaseEventForm, InviteEventForm):
    """plans to do with people"""
    title = forms.CharField(label=_('Title')) 
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['title', 'start_date', 'start_time','check_whole_day', 'end_date', 'end_time', 'invite',
                                'min_number_guests', 'max_number_guests','close',
                                'add_recursion', 'recursion_frequency','end_recurring_period',                                                                
                                'recursion_count','recursion_byweekday', 'recursion_bymonthday',
                                'priority', 'category','honeypot']                                  