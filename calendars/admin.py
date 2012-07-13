# -*- coding: utf-8 -*-
'''
Created on Mar 20, 2011

@author: Mourad Mourafiq

@license: closed application, My_licence, http://www.binpress.com/license/view/l/6f5700aefd2f24dd0a21d509ebd8cdf8

@copyright: Copyright © 2011

other contributers:
'''
from django.contrib import admin

from models.cals import Event, AttachmentEvent, Calendar, Occurrence
from models.recursions import Recursion

admin.site.register(Event)
admin.site.register(AttachmentEvent)
admin.site.register(Calendar)
admin.site.register(Occurrence)
admin.site.register(Recursion)