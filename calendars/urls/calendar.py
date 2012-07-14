# -*- coding: utf-8 -*-
'''
Created on Mar 20, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''
from django.conf.urls import patterns, include, url
from calendars.views import calendar_tables as calendar_tables 
from calendars.views import events as events

urlpatterns = patterns('', 
    url(r'^$', calendar_tables.calendar_detail, {'template_name': "calendars/calendar.html"}, name='calendar_detail'),   
    url(r'^(?P<events_id>\d+)/(?P<delta_day>.?\d+)/(?P<delta_minute>.?\d+)/(?P<allDay>\d)/_update/$', calendar_tables.update_event_date, name='update_event_date'),
    url(r'^planning/(?P<user_id>\d+)/$', calendar_tables.planning, name='planning'),
    url(r'^events/$', calendar_tables.calendar_by_params, name='calendar_events'),
    url(r'^events_title/$', events.events_titles, name='events_titles'),    
    )