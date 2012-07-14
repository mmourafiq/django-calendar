# -*- coding: utf-8 -*-
'''
Created on Mar 20, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''
import datetime
from django.conf import settings
from django import template
from django.core.urlresolvers import reverse
from django.utils.dateformat import format
import datetime
from django.utils.translation import ugettext_lazy as _
from calendars.models.cals import Calendar, Stat



register = template.Library()


@register.simple_tag
def querystring_for_date(date, num=6):
    query_string = '?'
    qs_parts = ['year=%d', 'month=%d', 'day=%d', 'hour=%d', 'minute=%d', 'second=%d']
    qs_vars = (date.year, date.month, date.day, date.hour, date.minute, date.second)
    query_string += '&'.join(qs_parts[:num]) % qs_vars[:num]
    return query_string

@register.simple_tag
def rspv_user_event(user, event):
    if user.is_authenticated():        
        try:            
            return Calendar.objects.get(user=user, event=event).get_status_display()
        except Calendar.DoesNotExist:
            return None        
    
@register.simple_tag
def statistics_event(event):
    stats = Stat.objects.filter(calendar__event=event)[0]
    acception_bar = stats.acception_bar
    max_number_guests = stats.max_number_guests
    if max_number_guests > 0:
        msg = _("%(max)s/%(min)s confirmed") %{
            'max': acception_bar, 
            'min': max_number_guests
            }
    else:
        msg = _("%s confirmed") % (stats.acception_bar)
    if stats.valid:
        msg = _("%s, valid") % msg
    if stats.stopped:
        msg = _("%s, closed") % msg
    return msg