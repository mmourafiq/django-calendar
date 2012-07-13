# -*- coding: utf-8 -*-
'''
Created on Mar 20, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''

from django import forms
from django.utils.translation import ugettext_lazy as _

class AttachmentForm(forms.Form):
    picture = forms.ImageField(label=_("Picture")) 
    error_css_class = "error" 
    def clean_picture(self):
        image = self.cleaned_data.get('picture',False)
        if image:
            if image._size > 500*1024:
                raise forms.ValidationError("Image file too large ( should be < 500kb )")
            return image
        else:   
            raise forms.ValidationError("Couldn't read uploaded image")