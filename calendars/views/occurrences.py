# -*- coding: utf-8 -*-
'''
Created on Mar 20, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, Context, loader
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseServerError, HttpResponseForbidden, HttpResponseNotAllowed
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token
from django.utils import simplejson
from calendars.utilis import fetch_from_url_occ, errors_as_json
from calendars.forms.occurrence import OccurrenceForm 
from calendars.models.cals import Occurrence

@login_required
def view_occ_date(request, event_slug):
    """
    view an occurrence by date (for non persisted occurrences)
    """
    (event, err, occurrence) = fetch_from_url_occ(request, event_slug)
    if err:
        return err

    if not occurrence.cancelled:
        c = RequestContext(request, {'occurrence': occurrence,
                                     })
        return render_to_response('calendars/occurrence_view.html', c)

@csrf_exempt
@requires_csrf_token
@login_required
def cancel_occ_date(request, event_slug):
    """
    cancel a non persisted occurrence
    """
    (event, err, occurrence) = fetch_from_url_occ(request, event_slug)
    if err:
        return err


    if not occurrence.cancelled:
        next = event.get_absolute_url()
        occurrence.cancel()
        return HttpResponseRedirect(next)


@login_required
def edit_occ_date(request, event_slug):
    """
    edit an unpersisted occurrence
    """
    (event, err, occurrence) = fetch_from_url_occ(request, event_slug)
    if err:
        return err


    if not occurrence.cancelled:
        form = OccurrenceForm(data=request.POST or None, instance=occurrence)
        if request.method == 'POST':
            if form.is_valid():
                occurrence = form.save(commit=False)
                occurrence.event = event
                occurrence.save()
                if not request.is_ajax():
                    return HttpResponseRedirect(occurrence.get_absolute_url())
                response = ({'success':'True'})
            else:
                response = errors_as_json(form)
            if request.is_ajax():
                json = simplejson.dumps(response, ensure_ascii=False)
                return HttpResponse(json, mimetype="application/json")
        return render_to_response('calendars/occurrence_edit.html', {
            'occ_form': form,
            'occurrence': occurrence,
            'action' : occurrence.get_edit_url(),
            'event' : occurrence.event,
        }, context_instance=RequestContext(request))

@login_required
def view_occ(request, occurrence_id):
    """
    view an occurrence with its id (for persisted occurrences)
    """
    occurrence = get_object_or_404(Occurrence, id=occurrence_id)

    if not occurrence.cancelled:
        c = RequestContext(request, {'occurrence': occurrence,
                                     })
        return render_to_response('calendars/occurrence_view.html', c)



@csrf_exempt
@requires_csrf_token
@login_required
def cancel_occ(request, occurrence_id):
    """
    cancel a persisted occurrence
    """
    occurrence = get_object_or_404(Occurrence, id=occurrence_id)

    next = occurrence.event.get_absolute_url()
    occurrence.cancel()
    return HttpResponseRedirect(next)

@login_required
def reactivate_occ(request, occurrence_id):
    """
    reactivate an occurrence
    """
    occurrence = get_object_or_404(Occurrence, id=occurrence_id)

    occurrence.uncancel()
    return HttpResponseRedirect(occurrence.get_absolute_url())

@login_required
def edit_occ(request, occurrence_id):
    """
    edit a persisted occurrence
    """
    occurrence = get_object_or_404(Occurrence, id=occurrence_id)


    if not occurrence.cancelled:
        form = OccurrenceForm(data=request.POST or None, instance=occurrence)
        if request.method == 'POST':
            if form.is_valid():
                occurrence = form.save()
                if not request.is_ajax():
                    return HttpResponseRedirect(occurrence.get_absolute_url())
                response = ({'success':'True'})
            else:
                response = errors_as_json(form)
            if request.is_ajax():
                json = simplejson.dumps(response, ensure_ascii=False)
                return HttpResponse(json, mimetype="application/json")

        return render_to_response('calendars/occurrence_edit.html', {
            'occ_form': form,
            'occurrence': occurrence,
            'action' : occurrence.get_edit_url(),
            'event' : occurrence.event,
        }, context_instance=RequestContext(request))
