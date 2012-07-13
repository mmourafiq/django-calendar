# -*- coding: utf-8 -*-
'''
Created on Mar 20, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''

def get_attachment_path(instance, filename):
    """Store file, appending new extension for added security"""
    dir = "uploads/%s/%s" % (instance.event.get_url()[:32], filename)
    return dir