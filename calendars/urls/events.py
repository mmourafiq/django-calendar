# -*- coding: utf-8 -*-
'''
Created on Mar 20, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''
from django.conf.urls import patterns, include, url
from calendars.views import events as events 

urlpatterns = patterns('',
    url(r'^_create/$', events.create,
        {'template_name':'calendars/event_form.html', 
         'next':'event_view','action':'event_create'},
        name='event_create'),                      
    url(r'^([a-zA-Z\d/_-]*)/_edit/$', events.edit,
        {'template_name':'calendars/event_form.html', 'next':'event_view'},
        name='event_edit'),
    url(r'^([a-zA-Z\d/_-]*)/_invite/$', events.change_invite_list,
        {'template_name':'calendars/event_form.html', 'next':'event_view'},
        name='event_invite'),
    url(r'^([a-zA-Z\d/_-]*)/_cancel/$', events.cancel,
        {'next':'event_view'},
        name='event_cancel'),
    url(r'^([a-zA-Z\d/_-]*)/_reactivate/$', events.reactivate,
        {'next':'event_view'},
        name='event_reactivate'),
    url(r'^([a-zA-Z\d/_-]*)/_maybe/$', events.maybe_accept_invitation,
        {'next':'event_view'},
        name='event_maybe_accept_inv'),
    url(r'^([a-zA-Z\d/_-]*)/_accept/$', events.accept_invitation,
        {'next':'event_view'},
        name='event_accept_inv'),
    url(r'^([a-zA-Z\d/_-]*)/_refuse/$', events.refuse_invitation,
        {'next':'event_view'},
        name='event_refuse_inv'),               
    url(r'^([a-zA-Z\d/_-]*)/_add_photo/$', events.add_attachment,
        {'template_name':'calendars/event_form.html', 'next':'event_view'},
        name='event_upload_photo'),     
    url(r'^([a-zA-Z\d/_-]*)/_occurrence_cancelled/$', events.cancelled_occurrence,
        {'template_name':'calendars/cancelled_occurrences.html'},
        name='event_cancelled_occurrence'),                                                                                                        
    url(r'^([a-zA-Z\d/_-]*)$', events.view,
        {'template_name':'calendars/event_view.html'},
        name='event_view'),
    )