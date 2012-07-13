# -*- coding: utf-8 -*-
'''
Created on Mar 20, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
import datetime
from calendars.models.cals import Event, EventListManager

def all_events(user=None, is_active=None, by_date="C", user_request=None):    
        
    if is_active is not None:
        events = Event.objects.filter(is_active=is_active)
    else :
        events = Event.active.all()

    if user is None:
        return events
    
    user = get_object_or_404(User, pk=user)
    return events.filter(author=user)

def all_calendar_events(user, is_active=None, user_request=None):    
    user = get_object_or_404(User, pk=user)
    if is_active is not None:
        events = Event.objects.filter(is_active=is_active, calendar__user=user)
    else:
        events = Event.active.filter(calendar__user=user)
    return events

def all_events_by_params(user=None, priority=None, is_active=None, category=None, user_request=None,
                       calendar=None, by_date="C"):
    """
    returns all clas by filtering on category
    """
    if calendar is not None and calendar:
        events = all_calendar_events(user, is_active, user_request=user_request)
    else:
        events = all_events(user, is_active, by_date=by_date, user_request=user_request)
    if priority is not None:    
        events = events.filter(periority=priority)
    if category is not None:
        events = events.filter(category=category)
    if by_date == "S":
        events = events.order_by('-start')
    return events

def on_this_day(user=None, in_datetime=None, within=None,priority=None, category=None,
                    is_active=None,user_request=None,since=None, calendar=None, by_date="S"):
    """
    Get all events happening on this day
    """       
    if in_datetime is None:
        in_datetime = datetime.date.today()   
    
    events = all_events_by_params(user=user,user_request=user_request,
                                   priority=priority, is_active=is_active,
                                   category=category,calendar=calendar,by_date=by_date)
    if within is not None:
        last_datetime = in_datetime + datetime.timedelta(days=int(within))
        return events.order_by('-start').filter(start__gte=in_datetime, start__lte=last_datetime)
    else : 
        return events.order_by('-start').filter(start__startswith=in_datetime)
    

def get_recent_events(user=None, in_datetime=None,priority=None, category=None,
                    is_active=None, user_request=None,since=None, calendar=None,by_date='C'):
    """
    This shortcut function allows you to get events that have created
    recently.

    amount is the amount of events you want in the queryset. The default is
    5.

    in_datetime is the datetime you want to check against.  It defaults to
    datetime.datetime.now
    """
    in_datetime = datetime.datetime.now()
    
    events = all_events_by_params(user=user, user_request=user_request,
                                priority=priority, is_active=is_active,
                                category=category,calendar=calendar,by_date=by_date)
    if by_date == 'C':
        if since is not None:
            sincae = datetime.datetime.fromtimestamp(int(since))
            return events.order_by('-created_at').filter(created_at__lte=in_datetime, created_at__gte=sincae)
        return events.order_by('-created_at').filter(created_at__lte=in_datetime)
    elif by_date == 'M':
        return events.order_by('-modified_on').filter(modified_on__lt=in_datetime)
    elif by_date == 'S':        
        return events.order_by('-start').filter(end__gte=in_datetime)

def occurrences_after(user=None, date=None):
    """get a list of all occurrences for events after the date"""
    events = all_events(user=user, is_active=True, plannable=True)
    return EventListManager(events).occurrences_after(date)