# -*- coding: utf-8 -*-
'''
Created on Mar 20, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''
from django.conf.urls import patterns, include, url
from calendars.views import occurrences as occurrences



#persisted occurrence
urlpatterns = patterns('',
    url(r'^(?P<occurrence_id>\d+)/_cancel/$', occurrences.cancel_occ, name='occurrence_cancel'),
    url(r'^(?P<occurrence_id>\d+)/_reactivate/$', occurrences.reactivate_occ, name='occurrence_reactivate'),
    url(r'^(?P<occurrence_id>\d+)/_edit/$', occurrences.edit_occ, name='occurrence_edit'),
    url(r'^(?P<occurrence_id>\d+)/$', occurrences.view_occ, name='occurrence_view'),
    )

#unpersisted occurrence views 
urlpatterns += patterns('',
    url(r'^([a-zA-Z\d/_-]*)/_cancel/$', occurrences.cancel_occ_date, name='occurrence_cancel_by_date'),
    url(r'^([a-zA-Z\d/_-]*)/_edit/$', occurrences.edit_occ_date, name='occurrence_edit_by_date'),
    url(r'^([a-zA-Z\d/_-]*)/$', occurrences.view_occ_date, name='occurrence_by_date'),
    ) 
