# -*- coding: utf-8 -*-
'''
Created on Mar 20, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from calendars.settings import *

class Recursion(models.Model):
    """
    This defines a recursion by which an event will recur.  This is defined by the
    rrule in the dateutil documentation.

    * name - the human friendly name of this kind of recursion.
    * description - a short description describing this type of recursion.
    * frequency - the base recurrence period
    * param - extra params required to define this type of recursion. The params
      should follow this format:

        param = [rruleparam:value;]*
        rruleparam = see list below
        value = int[,int]*

      The options are: (documentation for these can be found at
      http://labix.org/python-dateutil#head-470fa22b2db72000d7abe698a5783a46b0731b57)
        ** count
        ** bysetpos
        ** bymonth
        ** bymonthday
        ** byyearday
        ** byweekno
        ** byweekday
        ** byhour
        ** byminute
        ** bysecond
        ** byeaster
    """
    frequency = models.CharField(_("frequency"), choices=freqs, max_length=10)
    params = models.TextField(_("params"), null=True, blank=True)

    class Meta:
        verbose_name = _('recursion')
        verbose_name_plural = _('recursions')  
        app_label = 'calendars'
          
    def get_params(self):
        """
        >>> recursion = Recursion(params = "count:1;bysecond:1;byminute:1,2,4,5")
        >>> recursion.get_params()
        {'count': 1, 'byminute': [1, 2, 4, 5], 'bysecond': 1}
        """
        if self.params is None:
            return {}
        params = self.params.split(';')
        param_dict = []
        for param in params:
            param = param.split(':')
            if len(param) == 2:
                param = (str(param[0]), [int(p) for p in param[1].split(',')])
                if len(param[1]) == 1:
                    param = (param[0], param[1][0])
                param_dict.append(param)
        return dict(param_dict)
    
    def __unicode__(self):
        text = self.frequency
        if text == 'WEEKLY':
            params = self.get_params()  
            byweekday = ''               
            if 'byweekday' in params:                
                try:
                    text = text + ' : every ' + PERIOD_DAY_CAP[int(params['byweekday'])][1]
                except:
                    byweekday = params['byweekday']  
        if text == 'MONTHLY':
            params = self.get_params()  
            bymonthday = ''               
            if 'bymonthday' in params:
                try:                    
                    text = text + ' : every ' + PERIOD_DAY_CAP[int(params['bymonthday'])][1]
                except:
                    bymonthday = params['bymonthday']             
        return text
