# -*- coding: utf-8 -*-
'''
Created on Mar 20, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import datetime
from django.utils import simplejson
from calendars.calendar_meth import all_events_by_params
from calendars.settings import *
from calendars.models.cals import Event

@login_required
def planning(request,user_id=None, plannable=None, priority=None, category=None, is_active=None, template_name="calendars/planning.html"):
    list_cal = all_events_by_params(user=user_id, user_request=request.user.pk, is_active=is_active,
                                  category=category,calendar=True,
                                  priority=priority, by_date="S")
    in_datetime = datetime.datetime.now()
    upcoming = list_cal.filter(end__gte=in_datetime)
    due = list_cal.filter(end__lte=in_datetime)
    if not list_cal:
        list_cal = None
    c = RequestContext(request, {'upcoming': upcoming,
                                 'due': due,
                                 })
    return render_to_response(template_name, c)

@login_required
def calendar_by_params(request, period=None, date=None, category=None, priority=None,
                        is_active=None):
    """
    returns events for:

        -> a period = Year, Month, Week, Day
        -> a DATE = datetime
        -> a user
        -> a cal_type = wikis, events, with cals, for cals,
        -> a cal_place = place where the cal takes effect
        -> a cal_category
        -> a cal_priority
        -> eventually to see whether if the cal is active or canceled
    """
#    in_datetime = None
#    if user is None:
#        user = request.user.id
#    in_datetime = coerce_date_dict(request.GET)
#    if in_datetime:
#        try:
#            in_datetime = datetime.datetime(**in_datetime)
#        except ValueError:
#            raise Http404
#    else:
#        in_datetime = datetime.datetime.now()
    start = request.GET['start']
    start = datetime.datetime.fromtimestamp(int(start))
    end = request.GET['end']
    end = datetime.datetime.fromtimestamp(int(end))
    list_cal = all_events_by_params(user=request.user.pk, is_active=is_active,
                                  category=category,calendar=True,
                                  priority=priority, by_date="S")
    list_cal = list_cal.filter(Q(start__gte=start, start__lte=end) |
                               Q(end__gte=start, end__lte=end) |
                               Q(end_recurring_period__gte=start))
#    f_period = period(list_cal, in_datetime)
#    if not f_period:
#        return HttpResponseRedirect('/')

    json_cals = simplejson.dumps(_get_sorted_occurrences(list_cal, start, end), ensure_ascii=False)
    return HttpResponse(json_cals, content_type='application/javascript; charset=utf-8')

def _get_sorted_occurrences(list_cals, start, end):
    occurrences = []
    for cal in list_cals:
        cal_occurrences = cal.get_occurrences(start, end)
        for occurrence in cal_occurrences:
            if not occurrence.cancelled:
                if occurrence.event.recursion is not None:
                    cancel_url = occurrence.get_cancel_url()
                    edit_url = occurrence.get_edit_url()
                else :
                    cancel_url = occurrence.event.get_cancel_url()
                    edit_url = ""
                occ = {
                       'id' : occurrence.event.id,
                       'title' : occurrence.event.title,
                       'allDay' : occurrence.event.allDay,
                       'color' : EVENT_COLOR[occurrence.event.category],
                       'start' : occurrence.start.strftime('%Y-%m-%dT%H:%M:%S'),
                       'end' : occurrence.end.strftime('%Y-%m-%dT%H:%M:%S'),
                       'url' : occurrence.event.get_absolute_url(),
                       'edit_url' : edit_url,
                       }
                occurrences.append(occ)
    return occurrences

@login_required
def update_event_date(request, event_id, delta_day=0, delta_minute=0, allDay=None):
    """ Update only the start, end and allDay parameters of an event """
    event = Event.active.get(pk=event_id)
    start = event.start
    end = event.end
    if allDay=="1":
        event.allDay = True
    elif allDay=="0":
        event.allDay = False
    delta_day = int(delta_day)
    delta_minute = int(delta_minute)
    if not delta_day==0:
        end = end + datetime.timedelta(days=delta_day)
        if not allDay=="2":
            start = start + datetime.timedelta(days=delta_day)
    if not delta_minute==0:
        end = end + datetime.timedelta(minutes=delta_minute)
        if not allDay=="2":
            start = start + datetime.timedelta(minutes=delta_minute)

    event.start = start
    event.end = end

    event.save()
    json = simplejson.dumps({'success':True}, ensure_ascii=False)
    return HttpResponse(json, mimetype="application/json")

