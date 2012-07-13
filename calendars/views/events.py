# -*- coding: utf-8 -*-
'''
Created on Mar 20, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''
import datetime
from django.utils import timezone
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token
from django.contrib.auth.models import User
from calendars.models.cals import Event, AttachmentEvent, Stat, Calendar
from calendars.models.recursions import Recursion
from calendars.forms.attachment import AttachmentForm
from calendars.forms.cals import InviteEventForm
from calendars.utilis import fetch_from_url, errors_as_json
from calendars.settings import *
from calendars.forms.cals import BaseEventForm, EventForm


@login_required
def create(request, template_name=None, next=None, action=None):
    """ create an event """
    if request.method == 'POST':
        request_user = request.user
        f = EventForm(request.POST)
        if f.is_valid():
            title = f.cleaned_data['title']
            start = f.cleaned_data['start_time']
            end = f.cleaned_data['end_time']
            allDay = f.cleaned_data['check_whole_day']
            category = f.cleaned_data['category']
            priority = f.cleaned_data['priority']
            end_recurring_period = f.cleaned_data['end_recurring_period']
            recursion_frequency = f.cleaned_data['recursion_frequency']
            recursion_count = f.cleaned_data['recursion_count']
            recursion_byweekday = f.cleaned_data['recursion_byweekday']
            recursion_bymonthday = f.cleaned_data['recursion_bymonthday']
            close = f.cleaned_data['close']
            invite = f.cleaned_data['invite']
            min_number_guests = f.cleaned_data['min_number_guests']
            max_number_guests = f.cleaned_data['max_number_guests']
            slug = slugify(title)
            if Event.objects.filter(slug=slug).count() > 0:
                slug = slug + str(Event.objects.filter(slug__contains=slug).count())
            event = Event(author=request_user, slug=slug, title=title, start=start,
                                 end=end, category=category, allDay=allDay,
                                 priority=priority, end_recurring_period=end_recurring_period)

            #first we have to check if the current event is recurring, if so we:
            #the recursion parameters are required
            if f.cleaned_data['add_recursion']:
                recursion_params = recursion_count + recursion_byweekday + recursion_bymonthday
                recursion = Recursion(frequency=recursion_frequency, params=recursion_params)
                recursion.save()
                event.recursion = recursion
            event.save()
            stats = Stat(event=event,
                              min_number_guests=min_number_guests,
                              max_number_guests=max_number_guests,
                              close=close)
            stats.save()

            Calendar(event=event, user=request_user, stats=stats, is_guest=True).save()
            #@todo uncomment the code below to set the notification
            #set the notification object
            #ToNotify(user=request_user, basecal=eventCal).save()
            if invite:
                for user in invite:
                    Calendar(event=event, user=user,
                                 stats=stats, is_guest=True).save()
                    #send notification
                    #notification.send([user], "cal_invitation", {'cal': eventCal,})
                    #set the notification object
                    #ToNotify(user=user, basecal=eventCal).save()

            if not request.is_ajax():
                return HttpResponseRedirect(reverse(next, args=(event.get_url(),)))
            else:
                response = {'success':True, 'id':event.id, 'color': EVENT_COLOR[event.category],
                            'url' : event.get_absolute_url(),'start': event.start.strftime('%Y-%m-%dT%H:%M:%S'), 'end': event.end.strftime('%Y-%m-%dT%H:%M:%S'),}
                json = simplejson.dumps(response, ensure_ascii=False)
                return HttpResponse(json, mimetype="application/json")
        else:
            response = errors_as_json(f)
            if request.is_ajax():
                json = simplejson.dumps(response, ensure_ascii=False)
                return HttpResponse(json, mimetype="application/json")
    else:
        f = EventForm()

    c = RequestContext(request, {'form': f,
                                 'action':reverse(action),
                                 })

    return render_to_response(template_name, c)

@login_required
def edit(request, event_slug, cal_type="5", template_name=None, next=None):
    """ edit a withcal """
    (event, err) = fetch_from_url(request, event_slug)
    if err:
        return err
    request_user = request.user
    if request.method == 'POST':
        f = BaseEventForm(request.POST)
        if f.is_valid():
            event.start = f.cleaned_data['start_time']
            event.end = f.cleaned_data['end_time']
            event.allDay = f.cleaned_data['check_whole_day']
            event.category = f.cleaned_data['category']
            event.priority = f.cleaned_data['priority']
            event.end_recurring_period = f.cleaned_data['end_recurring_period']
            recursion_frequency = f.cleaned_data['recursion_frequency']
            recursion_count = f.cleaned_data['recursion_count']
            recursion_byweekday = f.cleaned_data['recursion_byweekday']
            recursion_bymonthday = f.cleaned_data['recursion_bymonthday']

            #first we have to check if the current event is recurring, if so we:
            #the recursion parameters are required
            if f.cleaned_data['add_recursion']:
                recursion_params = recursion_count + recursion_byweekday + recursion_bymonthday
                if event.recursion is None:
                    recursion = Recursion(frequency=recursion_frequency, params=recursion_params)
                    recursion.save()
                    event.recursion = recursion
                else :
                    recursion = event.recursion
                    recursion.frequency = recursion_frequency
                    recursion.params = recursion_params
                    recursion.save()
            else :
                if event.recursion is not None:
                    recursion = event.recursion
                    event.recursion = None
                    event.save()
                    recursion.delete()

            event.save()
            #notify all concerned users by the object by the new comment
            #users_tonotify = ToNotify.objects.filter(event=event).exclude(user=request_user)
            #for user_tonotify in users_tonotify:
                #user = user_tonotify.user
                #notification.send([user], "cal_updated", {'event': event, 'user':request_user,})

            if not request.is_ajax():
                return HttpResponseRedirect(reverse(next, args=(event.get_url(),)))
            response = ({'success':'True'})
        else:
            response = errors_as_json(f)
        if request.is_ajax():
            json = simplejson.dumps(response, ensure_ascii=False)
            return HttpResponse(json, mimetype="application/json")
    else:

        if event.recursion:
            params = event.recursion.get_params()
            count = ''
            byweekday = ''
            bymonthday = ''
            if 'count' in params:
                count = params['count']
            if 'byweekday' in params:
                try:
                    byweekday = [int(params['byweekday'])]
                except:
                    byweekday = params['byweekday']
            if 'bymonthday' in params:
                try:
                    bymonthday = [int(params['bymonthday'])]
                except:
                    bymonthday = params['bymonthday']
            f = BaseEventForm({'start_date': event.start.date(),
                      'start_time': event.start.time().strftime("%I:%M %p"),
                      'end_date': event.end.date(),
                      'end_time': event.end.time().strftime("%I:%M %p"),
                      'category': event.cal_category,
                      'priority': event.priority,
                      'check_whole_day': event.allDay,
                      'end_recurring_period': event.end_recurring_period,
                      'recursion_frequency' : event.recursion.frequency,
                      'add_recursion': True,
                      'recursion_count': count,
                      'recursion_byweekday':byweekday,
                      'recursion_bymonthday':bymonthday,
                      })
        else :
            f = BaseEventForm({'start_date': event.start.date(),
                      'start_time': event.start.time().strftime("%I:%M %p"),
                      'end_date': event.end.date(),
                      'end_time': event.end.time().strftime("%I:%M %p"),
                      'check_whole_day': event.allDay,
                      'category': event.category,
                      'priority': event.priority,
                      'end_recurring_period': event.end_recurring_period,
                      })
    c = RequestContext(request, {'form': f,
                                 'action': event.get_edit_url(),
                                 'event': event,
                                 })

    return render_to_response(template_name, c)

def view(request, event_slug, template_name=None):
    """ view a cal """
    (event, err) = fetch_from_url(request, event_slug)
    if err:
        return err
    rspv = False
    if event.start > timezone.now():
        rspv = True
    stats = Stat.objects.filter(event=event)[0]
    open = not stats.close
    values = Calendar.objects.filter(event=event, status = RSPV_YES).values_list('user', flat=True)
    if values:
        confirmed = User.objects.filter(pk__in = values)
    else:
        confirmed = None
    accept_url = reverse('event_accept_inv', args=[event.get_url()])
    maybe_url = reverse('event_maybe_accept_inv', args=[event.get_url()])
    refuse_url = reverse('event_refuse_inv', args=[event.get_url()])
    attachments_count= event.attachments().count()
    rest_attachments = 0
    first_attachments = []
    if attachments_count > 0:
        first_attachments = event.attachments()[:4]
        if attachments_count < 4:
            rest_attachments = range(4 - attachments_count)
    c = RequestContext(request, {'event': event,
                                 'accept_url':accept_url,
                                 'maybe_url':maybe_url,
                                 'refuse_url':refuse_url,
                                 'open' : open,
                                 'confirmed': confirmed,
                                 'rspv': rspv,
                                 'attachments_count': attachments_count,
                                 'first_attachments': first_attachments,
                                 'rest_attachments': rest_attachments,
                                 })
    return render_to_response(template_name, c)

@csrf_exempt
@requires_csrf_token
@login_required
def cancel(request, event_slug, next=None):
    """ Cancel a cal """
    (event, err) = fetch_from_url(request, event_slug)
    if err:
        return err
    request_user = request.user
    if event.delete(request_user):
        """ The function delete returns True if it is set to True, False otherwise
            notify all concerned users by the object by the deletion
        """
        #users_tonotify = ToNotify.objects.filter(event=event).exclude(user=request_user)
        #for user_tonotify in users_tonotify:
            #user = user_tonotify.user
            #notification.send([user], "event_cancelled", {'event': event, 'user':request_user,})

    if request.is_ajax():
        json_response = simplejson.dumps({
                'success': True,})
        return HttpResponse(json_response, mimetype="application/json")
    return  HttpResponseRedirect(reverse(next, args=(event.get_url(),)))

@csrf_exempt
@requires_csrf_token
@login_required
def reactivate(request, event_slug, next=None):
    """ Uncancel a event """
    (event, err) = fetch_from_url(request, event_slug)
    if err:
        return err
    request_user = request.user
    if event.reactivate(request_user):
        """ The function reactivate returns True if it is set to True, False otherwise
            notify all concerned users by the object by the reactivation
        """
        #@TODO: If you use django_notification you can uncomment the code below
        #users_tonotify = ToNotify.objects.filter(event=event).exclude(user=request_user)
        #for user_tonotify in users_tonotify:
            #user = user_tonotify.user
            #notification.send([user], "event_reactivated", {'event': event, 'user':request_user,})

    if request.is_ajax():
        json_response = simplejson.dumps({
                'success': True,})
        return HttpResponse(json_response, mimetype="application/json")
    return  HttpResponseRedirect(reverse(next, args=(event.get_url(),)))

@login_required
def add_attachment(request, event_slug, template_name=None, next=None):
    """ add related cals """
    (event, err) = fetch_from_url(request, event_slug)
    if err:
        return err
    request_user = request.user
    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            AttachmentEvent(picture=form.cleaned_data['picture'], event = event, uploaded_by = request_user).save()
            if not request.is_ajax():
                return HttpResponseRedirect(reverse(next, args=(event.get_url(),)))
            response = {'success':True}
        else:
            response = errors_as_json(form)
        if request.is_ajax():
            json = simplejson.dumps(response, ensure_ascii=False)
            return HttpResponse(json, mimetype="application/json")
    else:
        form = AttachmentForm()
    c = RequestContext(request, {'form': form,
                                 'event': event,
                                 })

    return render_to_response(template_name, c)

@login_required
def change_invite_list(request, event_slug, template_name=None, next=None):
    """ invite people for a cal """
    (event, err) = fetch_from_url(request, event_slug)
    if err:
        return err
    old_invite_list = []
    request_user = request.user
    stats = Stat.objects.filter(event=event)[0]
    invite_l = User.objects.filter(calendar__stats=stats, calendar__is_guest=True)
    for user in invite_l:
        old_invite_list.append(user)

    if request.method == 'POST':
        f = InviteEventForm(request.POST)
        if f.is_valid():
            old_close = stats.close
            stats.close = f.cleaned_data['close']
            invite = f.cleaned_data['invite']
            stats.min_number_guests = f.cleaned_data['min_number_guests']
            stats.max_number_guests = f.cleaned_data['max_number_guests']
            stats.save()
            if invite:
                for user in invite:
                    if user in old_invite_list:
                        old_invite_list.remove(user)
                    else:
                        Calendar(event=event, user=user,
                                 stats=stats, is_guest=True).save()
                        #send notification
                        #notification.send([user], "event_invitation", {'event': event,})
                        #set the notification object
                        #ToNotify.objects.get_or_create(user=user, event=event)
                for user in old_invite_list:
                    #delete calendar
                    Calendar.objects.filter(event=event, user=user,
                                 stats=stats)[0].delete()
                    #delete tonotofy for this user
                    #ToNotify.objects.filter(user=user, event=event)[0].delete()

            return HttpResponseRedirect(reverse(next, args=(event.get_url(),)))

    invite_names = ''
    for user in old_invite_list:
        if not user == request_user:
            invite_names = invite_names + user.first_name+' '+user.last_name + ','
    f = InviteEventForm({
                  'close': stats.close,
                  'invite': old_invite_list,
                  'min_number_guests':stats.min_number_guests,
                  'max_number_guests':stats.max_number_guests,
                  })

    c = RequestContext(request, {'form': f,
                                 'invite_names': invite_names,
                                 'event': event,
                                 })

    return render_to_response(template_name, c)

def respond_to_invitation(request, event_slug, status, next):
    """respond to the invitation by changing the invitation status"""
    (event, err) = fetch_from_url(request, event_slug)
    if err:
        return err
    request_user = request.user

    calendar = Calendar.objects.filter(event=event, user=request_user)
    if event.count() == 0:
        stats = Stat.objects.filter(event=event)[0]
        calendar = Calendar(event=event, user=request_user, stats=stats)
        calendar.save()
    else:
        calendar = calendar[0]

    if status == RSPV_YES:
        #attending
        stat = calendar.accept()
        #if (stat):
            #add user to be notified
            #ToNotify.objects.get_or_create(user=request_user, event=event)
            #notification.send([event.author], "cal_accepted", {'event': event, 'user_to':request_user,})
    elif status == RSPV_MAYBE:
        #may be attending
        #add user to be notified
        #ToNotify.objects.get_or_create(user=request_user, event=event)
        calendar.maybe_accept()
    elif status == RSPV_NO:
        #not attending
        #delete tonotofy for this user
        #ToNotify.objects.filter(user=request_user, event=event)[0].delete()
        #notification.send([event.author], "cal_refused", {'event': event, 'user_to':request_user,})
        calendar.refuse()

    if request.is_ajax():
        json_response = simplejson.dumps({
                'success': True,})
        return HttpResponse(json_response, mimetype="application/json")
    return HttpResponseRedirect(reverse(next, args=(event.get_url(),)))

@csrf_exempt
@requires_csrf_token
@login_required
def accept_invitation(request, event_slug, next):
    """accept an ainvitation, attend"""
    request_user = request.user
    return respond_to_invitation(request, event_slug, RSPV_YES, next)

@csrf_exempt
@requires_csrf_token
@login_required
def maybe_accept_invitation(request, event_slug, next):
    """may be attend the envent"""
    return respond_to_invitation(request, event_slug, RSPV_MAYBE, next)


@csrf_exempt
@requires_csrf_token
@login_required
def refuse_invitation(request, event_slug, next):
    """refuse the invitation"""
    return respond_to_invitation(request, event_slug, RSPV_NO, next)

def cancelled_occurrence(request, event_slug, template_name):
    """ return a list of cancelled occurrences for the current cal"""
    (event, err) = fetch_from_url(request, event_slug)
    if err:
        return err
    request_user = request.user
    cancelled_occurrences = event.occurrence_set.filter(cancelled=True)
    c = RequestContext(request, {
                                     'event': event,
                                     'cancelled_occurrences' : cancelled_occurrences,
                                     })

    return render_to_response(template_name, c)


@login_required
def events_titles(request):
    """ return a json object containing related people names """
    q = request.GET['q'];
    list_titles = []

    events = Event.active.all().filter(title__icontains=q)
    for event in events:
        name = {
               'value' : event.id,
               'name' : event.title,
               }
        list_titles.append(name)

    json_cals = simplejson.dumps(list_titles, ensure_ascii=False)
    return HttpResponse(json_cals, content_type='application/javascript; charset=utf-8')

#def get_open_event_nearby(request, latit, longit, zoom=1, within=6, day=None, month=None, year=None, amount=None, template_name="calendars/event_map.html"):
#    km = 25.00
#    nbre_km = int(zoom)
#    latit, longit = to_radians(float(latit), float(longit))
#    places = list(Place.search.geoanchor('latit', 'longit', latit, longit).filter(**{'@geodist__lt':nbre_km*km}).order_by('-@geodist'))
#    if year == None:
#        in_datetime = datetime.date.today()
#    else :
#        in_datetime = datetime.date(int(year), int(month), int(day))
#    opens = Stat.objects.filter(close=False).values_list('event', flat=True).all()
#    all_events = on_this_day(by_date="S",timeline="public", in_datetime=in_datetime, within=within)
#    #cals with recursions
#    other_open_results = Event.active.filter(~Q(recursion__exact=None), Q(place__in=places),Q(pk__in=list(opens)))
#    open_events = list(all_events.filter(place__in=places, pk__in=list(opens)))
#    in_datetime_plus = in_datetime + datetime.timedelta(days=int(within))
#    in_datetime_plus = datetime.datetime.combine(in_datetime_plus, datetime.time())
#    in_datetime = datetime.datetime.combine(in_datetime, datetime.time())
#    for r in other_open_results:
#        difference = (r.end - r.start)
#        end = in_datetime_plus
#        if r.recursion is not None:
#            if r.end_recurring_period and r.end_recurring_period < in_datetime_plus:
#                end = r.end_recurring_period
#            rule = r.get_rrule_object()
#            o_starts = rule.between(in_datetime - difference, end, inc=True)
#            for o_start in o_starts:
#                if in_datetime.date() == o_start.date():
#                    open_events.append(r)
#    if amount is not None:
#        open_events = all_events.filter(place__in=places, pk__in=list(opens))[:amount]
#    request_user = request.user
#    if request.user.is_authenticated():
#        values = RelationTimeLine.objects.filter(user=request_user).values_list('basecal', flat=True)
#        events = list(all_events.filter(Q(place__in=places,pk__in=list(values)),~Q(pk__in=list(opens))))
#        other_relation_results = EventCal.active.filter(~Q(recursion__exact=None), Q(place__in=places), Q(pk__in=list(values)),~Q(pk__in=list(opens)))
#        for r in other_relation_results:
#            difference = (r.end - r.start)
#            end = in_datetime_plus
#            if r.recursion is not None:
#                if r.end_recurring_period and r.end_recurring_period < in_datetime_plus:
#                    end = r.end_recurring_period
#                rule = r.get_rrule_object()
#                o_starts = rule.between(in_datetime - difference, end, inc=True)
#                for o_start in o_starts:
#                    if in_datetime.date() == o_start.date():
#                        open_events.append(r)
#    else:
#        events = []
#
#    if amount is None:
#        places = Place.active.filter(place__in=places, show_on_map=True)
#    else:
#        places = Place.active.filter(place__in=places, show_on_map=True)[:amount]
#    context = {
#               'events': events,
#               'open_events': open_events,
#               'places': places}
#    return render_to_response(template_name, context, context_instance=RequestContext(request))