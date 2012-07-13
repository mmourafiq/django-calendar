# -*- coding: utf-8 -*-
'''
Created on Mar 20, 2011

@author: Mourad Mourafiq

@copyright: Copyright © 2011

other contributers:
'''
import os
import heapq
from django.db import models
from django.conf import settings
from django.template.defaultfilters import truncatewords
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from dateutil import rrule
from django.utils.translation import ugettext, ugettext_lazy as _
from django.template.defaultfilters import date
from django.db.models import signals
from django.template.defaultfilters import timesince

from calendars.managers import ActiveManager
from calendars.settings import *
from calendars.files import get_attachment_path
from calendars.models.recursions import Recursion
if "djangosphinx" in settings.INSTALLED_APPS:
    from djangosphinx.models import SphinxSearch
else:
    SphinxSearch = None

class Event(models.Model):
    """
    Event model
    Contains all the basics about events,
    """


    author = models.ForeignKey(User, blank=True, null=True, related_name="created_events")
    title = models.CharField(max_length=140, verbose_name=_('Title'),
                             blank=False)
    slug = models.SlugField(max_length=140, verbose_name=_('slug'),
                            help_text=_('Letters, numbers, underscore and hyphen.'
                                        ' Do not use reserved words \'create\','
                                        ' \'history\' and \'edit\'.'),blank=True)
    created_at = models.DateTimeField(_('created at'), default=datetime.now)
    modified_on = models.DateTimeField(_('modified on'), default=datetime.now)
    is_active = models.BooleanField(default=True)
    users = models.ManyToManyField(User, related_name="events", through='Calendar')
    start = models.DateTimeField(_("start"))
    end = models.DateTimeField(_("end"), blank=True, null=True, help_text=_("The end time must be later than the start time."))
    allDay = models.BooleanField(default=False)
    category = models.CharField(max_length=1, choices=EVENT_CATEGORY)
    priority = models.CharField(max_length=1, choices=EVENT_PRIORITY)
    recursion = models.ForeignKey(Recursion, null=True, blank=True, verbose_name=_("recursion"))
    end_recurring_period = models.DateTimeField(_("end recurring period"),
                                                null=True, blank=True,
                                                help_text=_("This date is ignored for one time only events."))

    active = ActiveManager()
    objects = models.Manager()
    if SphinxSearch:
        search_events = SphinxSearch(
            index='event event_delta',
            weights={
                     'title':100,
                     'slug':100,
                     },
            )

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
        app_label = 'calendars'

    def __unicode__(self):
        return self.title

    def get_indiv_cal(self):
        return '<a href= "%s" data-analytic="profile" data-tooltip="user"> \
                 %s %s </a>:\
                 <h3><a class="cal_title" href= "%s" > %s </a></h3>'% (
                    reverse('profiles_profile_detail',args=[self.author.username]),
                    self.author.first_name,
                    self.author.last_name,
                    self.get_absolute_url(),
                    self.title,)

    def attachments(self):
        return AttachmentEvent.objects.filter(event__exact=self)

    def attachment_profile(self):
        attachments =  AttachmentEvent.objects.filter(event__exact=self).order_by('-uploaded_on')
        if attachments.count()>0:
            return attachments[0].thumbnail.url
        else :
            return False

    def get_url(self):
        """Return the cal URL for an article"""
        return self.slug

    @models.permalink
    def get_absolute_url(self):
        url = 'event_view'
        return (url, [self.get_url()])

    @models.permalink
    def get_edit_url(self):
        url = 'event_edit'
        return (url, [self.get_url()])

    @models.permalink
    def get_upload_photo_url(self):
        url = 'event_upload_photo'
        return (url, [self.get_url()])

    @models.permalink
    def get_cancel_url(self):
        url = 'event_cancel'
        return (url, [self.get_url()])

    @models.permalink
    def get_reactivate_url(self):
        url = 'event_reactivate'
        return (url, [self.get_url()])


    def get_occurrences(self, start, end):
        """
        >>> recursion = Recursion(frequency = "MONTHLY", name = "Monthly")
        >>> recursion.save()
        >>> event = Event(recursion=recursion, start=datetime.datetime(2008,1,1), end=datetime.datetime(2008,1,2))
        >>> event.recursion
        <recursion: Monthly>
        >>> occurrences = event.get_occurrences(datetime.datetime(2008,1,24), datetime.datetime(2008,3,2))
        >>> ["%s to %s" %(o.start, o.end) for o in occurrences]
        ['2008-02-01 00:00:00 to 2008-02-02 00:00:00', '2008-03-01 00:00:00 to 2008-03-02 00:00:00']

        Ensure that if an event has no recursion, that it appears only once.

        >>> event = Event(start=datetime.datetime(2008,1,1,8,0), end=datetime.datetime(2008,1,1,9,0))
        >>> occurrences = event.get_occurrences(datetime.datetime(2008,1,24), datetime.datetime(2008,3,2))
        >>> ["%s to %s" %(o.start, o.end) for o in occurrences]
        []

        """
        persisted_occurrences = self.occurrence_set.all()
        occ_replacer = OccurrenceReplacer(persisted_occurrences)
        occurrences = self._get_occurrence_list(start, end)
        final_occurrences = []
        for occ in occurrences:
            # replace occurrences with their persisted counterparts
            if occ_replacer.has_occurrence(occ):
                p_occ = occ_replacer.get_occurrence(
                        occ)
                # ...but only if they are within this period
                if p_occ.start < end and p_occ.end >= start:
                    final_occurrences.append(p_occ)
            else:
                final_occurrences.append(occ)
        # then add persisted occurrences which originated outside of this period but now
        # fall within it
        final_occurrences += occ_replacer.get_additional_occurrences(start, end)
        return final_occurrences

    def get_rrule_object(self):
        if self.recursion is not None:
            params = self.recursion.get_params()
            frequency = 'rrule.%s' % self.recursion.frequency
            return rrule.rrule(eval(frequency), dtstart=self.start, **params)

    def _create_occurrence(self, start, end=None):
        if end is None:
            end = start + (self.end - self.start)
        return Occurrence(event=self, start=start, end=end, original_start=start, original_end=end)

    def get_occurrence(self, date):
        rule = self.get_rrule_object()
        if rule:
            next_occurrence = rule.after(date, inc=True)
        else:
            next_occurrence = self.start
        if next_occurrence == date:
            try:
                return Occurrence.objects.get(event=self, original_start=date)
            except Occurrence.DoesNotExist:
                return self._create_occurrence(next_occurrence)

    def has_occurrence(self, date):
        try:
            return Occurrence.objects.get(event=self, original_start=date)
        except Occurrence.DoesNotExist:
            return None

    def _get_occurrence_list(self, start, end):
        """
        returns a list of occurrences for this event from start to end.
        """
        difference = (self.end - self.start)
        if self.recursion is not None:
            occurrences = []
            if self.end_recurring_period and self.end_recurring_period < end:
                end = self.end_recurring_period
            rule = self.get_rrule_object()
            o_starts = rule.between(start - difference, end, inc=True)
#            #check if the first occurrence doesn't much the original event, if so append the original
#            if not self.start in o_starts:
#                # check if event is in the period
#                if self.start < end and self.end >= start:
#                    return [self._create_occurrence(self.start)]
            #continue with normal occurrences
            for o_start in o_starts:
                o_end = o_start + difference
                occurrences.append(self._create_occurrence(o_start, o_end))
            return occurrences
        else:
            # check if event is in the period
            if self.start < end and self.end >= start:
                return [self._create_occurrence(self.start)]
            else:
                return []

    def _occurrences_after_generator(self, after=None):
        """
        returns a generator that produces unpresisted occurrences after the
        datetime ``after``.
        """

        if after is None:
            after = datetime.now()
        rule = self.get_rrule_object()
        if rule is None:
            if self.end > after:
                yield self._create_occurrence(self.start, self.end)
            raise StopIteration
        date_iter = iter(rule)
        difference = self.end - self.start
        while True:
            o_start = date_iter.next()
            if o_start > self.end_recurring_period:
                raise StopIteration
            o_end = o_start + difference
            if o_end > after:
                yield self._create_occurrence(o_start, o_end)


    def occurrences_after(self, after=None):
        """
        returns a generator that produces occurrences after the datetime
        ``after``.  Includes all of the persisted Occurrences.
        """
        occ_replacer = OccurrenceReplacer(self.occurrence_set.all())
        generator = self._occurrences_after_generator(after)
        while True:
            next = generator.next()
            yield occ_replacer.get_occurrence(next)


class AttachmentEvent(models.Model):
    event = models.ForeignKey(Event, verbose_name=_('Event'))
    picture = models.ImageField(upload_to=get_attachment_path, default=DEFAULT_PICTURE, blank=True, null=True)
    thumbnail = models.ImageField(upload_to='uploads/thumbs/cals/', blank=True, null=True,
         editable=False)
    uploaded_by = models.ForeignKey(User, blank=True, verbose_name=_('Uploaded by'), null=True)
    uploaded_on = models.DateTimeField(default=datetime.now,verbose_name=_('Upload date'))

    class Meta:
        app_label = 'calendars'

    def save(self, force_insert=False, force_update=False):
        #get mtime stats from file
        thumb_update = False

        if self.thumbnail:
            try:
                if self.picture:
                    statinfo1 = os.stat(self.picture.path)
                    statinfo2 = os.stat(self.thumbnail.path)
                    if statinfo1 > statinfo2:
                        thumb_update = True
                else:
                    self.picture = DEFAULT_PICTURE
                    thumb_update = True

            except OSError:
                thumb_update = True

        if self.picture and not self.thumbnail or thumb_update:
            from PIL import Image

            THUMB_SIZE = (200,200)

            #self.thumbnail = self.picture

            image = Image.open(self.picture)

            if image.mode not in ('L', 'RGB'):
                image = image.convert('RGB')

            image.thumbnail(THUMB_SIZE, Image.ANTIALIAS)
            (head, tail) = os.path.split(self.picture.path)
            (a, b) = os.path.split(self.picture.name)

            if not os.path.isdir(head + '/uploads/thumbs/cals'):
                os.mkdir(head + '/uploads/thumbs/cals')

            image.save(head + '/uploads/thumbs/cals/' + tail)

            self.thumbnail = 'uploads/thumbs/cals/' + b

        super(AttachmentEvent, self).save()





class Stat(models.Model):
    """
    A cal to be planned with friends
    """
    event = models.ForeignKey(Event)
    can_join = models.ManyToManyField(User, blank=True, null=True, related_name='join')
    acception_bar = models.IntegerField(default=0)
    min_number_guests = models.IntegerField(default=0)
    max_number_guests = models.IntegerField(default=0)
    close = models.BooleanField(default=False)
    stopped = models.BooleanField(default=False)
    valid = models.BooleanField(default=False)


    class Meta:
        verbose_name = _('Stat')
        verbose_name_plural = _('Stats')
        app_label = 'calendars'

class Calendar(models.Model):
    """
    A manytomany relationship between the Event and
    the Calender
    """

    event = models.ForeignKey(Event)
    user = models.ForeignKey(User)
    status = models.CharField(max_length=1, verbose_name=_('RSPV status'),
                                  choices=RSPV_STATUS, null=True, blank=True)
    is_guest = models.BooleanField(default=False)
    stats = models.ForeignKey(Stat)
    class Meta:
        verbose_name = _('Calendar')
        verbose_name_plural = _('Calendars')
        app_label = 'calendars'

    def accept(self):
        """when a user accept a cal invitation"""
        if not self.stats.stopped and self.status != RSPV_YES:
            self.stats.acception_bar = self.stats.acception_bar + 1
            if self.stats.acception_bar >= self.stats.min_number_guests and not self.stats.valid:
                self.stats.valid = True
            if self.stats.acception_bar == self.stats.max_number_guests and not self.stats.stopped:
                self.stats.stopped = True
            self.status = RSPV_YES
            self.stats.save()
            self.save()
            return True
        else:
            return False

    def maybe_accept(self):
        """when a user is may be attending an invitation"""
        if self.status == RSPV_YES:
            return self.cancel(RSPV_MAYBE)
        else:
            self.status = RSPV_MAYBE
            self.stats.save()
            self.save()

    def refuse(self):
        """when a user decline an invitation"""
        if self.status == RSPV_YES:
            return self.cancel(RSPV_NO)
        else:
            self.status = RSPV_NO
            self.stats.save()
            self.save()

    def cancel(self, status=RSPV_NO):
        """cancel a confirmed invitation"""
        if self.stats.acception_bar > 0:
            self.stats.acception_bar = self.stats.acception_bar - 1
        if self.stats.acception_bar < self.stats.min_number_guests and self.stats.valid:
            self.stats.valid = False
        if self.stats.acception_bar < self.stats.max_number_guests and self.stats.stopped:
            self.stats.stopped = False
        self.status = status
        self.stats.save()
        self.save()


class Occurrence(models.Model):
    event = models.ForeignKey(Event, verbose_name=_("event"))
    start = models.DateTimeField(_("start"))
    end = models.DateTimeField(_("end"))
    cancelled = models.BooleanField(_("cancelled"), default=False)
    original_start = models.DateTimeField(_("original start"))
    original_end = models.DateTimeField(_("original end"))

    class Meta:
        verbose_name = _("occurrence")
        verbose_name_plural = _("occurrences")
        app_label = 'calendars'

    def moved(self):
        return self.original_start != self.start or self.original_end != self.end
    moved = property(moved)

    def move(self, new_start, new_end):
        self.start = new_start
        self.end = new_end
        self.save()

    def cancel(self):
        self.cancelled = True
        self.save()

    def uncancel(self):
        self.cancelled = False
        self.save()


    def get_absolute_url(self):
        if self.pk is not None:
            return reverse('occurrence_view', kwargs={'occurrence_id': self.pk})

        query_string = '?'
        qs_parts = ['year=%d', 'month=%d', 'day=%d', 'hour=%d', 'minute=%d', 'second=%d']
        qs_vars = (self.start.year, self.start.month, self.start.day,
                    self.start.hour, self.start.minute, self.start.second)
        query_string += '&'.join(qs_parts[:6]) % qs_vars[:6]
        return '/occurrence/%(url)s/%(start)s' % {'url':self.event.get_url(),
                                               'start':query_string, }

    def get_cancel_url(self):
        if self.pk is not None:
            return reverse('occurrence_cancel', kwargs={'occurrence_id': self.pk})
        query_string = '?'
        qs_parts = ['year=%d', 'month=%d', 'day=%d', 'hour=%d', 'minute=%d', 'second=%d']
        qs_vars = (self.start.year, self.start.month, self.start.day,
                    self.start.hour, self.start.minute, self.start.second)
        query_string += '&'.join(qs_parts[:6]) % qs_vars[:6]
        return '/occurrence/%(url)s/_cancel/%(start)s' % {'url':self.event.get_url(),
                                               'start':query_string, }
    def get_reactivate_url(self):
        if self.pk is not None:
            return reverse('occurrence_reactivate', kwargs={'occurrence_id': self.pk})

    def get_edit_url(self):
        if self.pk is not None:
            return reverse('occurrence_edit', kwargs={'occurrence_id': self.pk,})
        query_string = '?'
        qs_parts = ['year=%d', 'month=%d', 'day=%d', 'hour=%d', 'minute=%d', 'second=%d']
        qs_vars = (self.start.year, self.start.month, self.start.day,
                    self.start.hour, self.start.minute, self.start.second)
        query_string += '&'.join(qs_parts[:6]) % qs_vars[:6]
        return '/occurrence/%(url)s/_edit/%(start)s' % {'url':self.event.get_url(),
                                               'start':query_string, }

    def __unicode__(self):
        return ugettext("%(start)s to %(end)s") % {
            'start': self.start,
            'end': self.end,
        }

    def __cmp__(self, other):
        rank = cmp(self.start, other.start)
        if rank == 0:
            return cmp(self.end, other.end)
        return rank

    def __eq__(self, other):
        return self.event == other.event and self.original_start == other.original_start and self.original_end == other.original_end



class OccurrenceReplacer(object):
    """
    When getting a list of occurrences, the last thing that needs to be done
    before passing it forward is to make sure all of the occurrences that
    have been stored in the datebase replace, in the list you are returning,
    the generated ones that are equivalent.  This class makes this easier.
    """

    def __init__(self, persisted_occurrences):
        lookup = [((occ.event, occ.original_start, occ.original_end), occ) for
            occ in persisted_occurrences]
        self.lookup = dict(lookup)

    def get_occurrence(self, occ):
        """
        Return a persisted occurrences matching the occ and remove it from lookup since it
        has already been matched
        """
        return self.lookup.pop(
            (occ.event, occ.original_start, occ.original_end),
            occ)

    def has_occurrence(self, occ):
        return (occ.event, occ.original_start, occ.original_end) in self.lookup

    def get_additional_occurrences(self, start, end):
        """
        Return persisted occurrences which are now in the period
        """
        return [occ for key, occ in self.lookup.items() if (occ.start < end and occ.end >= start and not occ.cancelled)]

class EventListManager(object):
    """
    This class is responsible for doing functions on a list of events. It is
    used to when one has a list of events and wants to access the occurrences
    from these events in as a group
    """
    def __init__(self, events):
        self.events = events

    def occurrences_after(self, after=None):
        """
        It is often useful to know what the next occurrence is given a list of
        events.  This function produces a generator that yields the
        the most recent occurrence after the date ``after`` from any of the
        events in ``self.events``
        """
        if after is None:
            after = datetime.now()
        occ_replacer = OccurrenceReplacer(
            Occurrence.objects.filter(eventcal__in=self.events))
        generators = [event._occurrences_after_generator(after) for event in self.events]
        occurrences = []

        for generator in generators:
            try:
                heapq.heappush(occurrences, (generator.next(), generator))
            except StopIteration:
                pass

        while True:
            if len(occurrences) == 0: raise StopIteration

            generator = occurrences[0][1]

            try:
                next = heapq.heapreplace(occurrences, (generator.next(), generator))[0]
            except StopIteration:
                next = heapq.heappop(occurrences)[0]
            yield occ_replacer.get_occurrence(next)
