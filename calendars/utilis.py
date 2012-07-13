# -*- coding: utf-8 -*-
'''
Created on Mar 20, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context, loader
from django.utils.html import strip_tags 

from calendars.settings import *
from calendars.models.cals import Event
import datetime

def fetch_from_url_occ(request, url):
    in_datetime = coerce_date_dict(request.GET)    
    in_datetime = datetime.datetime(**in_datetime)
    (cal, err) = fetch_from_url(request, url)
    occ = cal.pagecal.eventcal.get_occurrence(in_datetime)
    if occ is not None:
        return (cal, err, occ)
    else :
        err = not_found(request, '')
        return (cal, err, occ)

def fetch_from_url(request, event_slug):
    """ Returns the object for the current slug"""
    events = Event.active.filter(slug=event_slug)
    if events.count() > 0:
        return events[0], False
    else:
        return None, not_found(request, event_slug)

def find_key_for_caltype(dic, val):
    """return the key of dictionary dic given the value"""
    return [k for k, v in dic.iteritems() if v == val][0]

def not_found(request, cal_url):
    """Generate a NOT FOUND message for some URL"""
    return render_to_response('simplewiki_error.html',
                              RequestContext(request, {'err_notfound': True,
                                                       'wiki_url': cal_url}))

def coerce_date_dict(date_dict):
    """
    given a dictionary (presumed to be from request.GET) it returns a tuple
    that represents a date. It will return from year down to seconds until one
    is not found.  ie if year, month, and seconds are in the dictionary, only
    year and month will be returned, the rest will be returned as min. If none
    of the parts are found return an empty tuple.
    """
    keys = ['year', 'month', 'day', 'hour', 'minute', 'second']
    retVal = {
                'year': 1,
                'month': 1,
                'day': 1,
                'hour': 0,
                'minute': 0,
                'second': 0}
    modified = False
    for key in keys:
        try:
            retVal[key] = int(date_dict[key])
            modified = True
        except KeyError:
            break
        except TypeError:
            break
    return modified and retVal or {}

def errors_as_json(form, striptags=False):
    error_summary = {}
    errors = {}
    for error in form.errors.iteritems():
        errors.update({error[0] : unicode(strip_tags(error[1]) \
            if striptags else error[1])})
    error_summary.update({'errors' : errors })
    return error_summary