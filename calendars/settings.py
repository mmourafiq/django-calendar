from django.utils.translation import ugettext, ugettext_lazy as _


EVENT_PRIORITY = (
    ("1", "!"),
    ("2", "!!"),
    ("3", "!!!"),
    )


EVENT_CATEGORY = (
    ("1", "Party"),
    ("2", "Work"),
    ("3", "Education"),
    )

RSPV_STATUS = (
    ("1", "rspv-yes"),
    ("2", "rspv-maybe"),
    ("3", "rspv-no")
    )

RSPV_YES = "1"
RSPV_MAYBE = "2"
RSPV_NO = "3"

DEFAULT_PICTURE = 'event.gif'

freqs = (("YEARLY", _("Yearly")),
            ("MONTHLY", _("Monthly")),
            ("WEEKLY", _("Weekly")),
            ("DAILY", _("Daily")))

PERIOD_DAY = (
        (0, "M"),
        (1, "T"),
        (2, "W"),
        (3, "T"),
        (4, "F"),
        (5, "S"),
        (7, "S"),
        )
PERIOD_DAY_CAP = (
        (0, "monday"),
        (1, "tuesday"),
        (2, "wednesday"),
        (3, "thursday"),
        (4, "friday"),
        (5, "saturday"),
        (7, "sunday"),
        )

EVENT_COLOR = {
        31: '#e67399',
        121: '#9767a1',
        28: '#6d5fca',
        34: '#8392ae',
        9: '#59bfb3',
        25: '#599a48',
        13: '#80ad30',
        119: '#9ea332',
        15: '#bd8528',
        120: '#d16f46',
        14: '#e49442',
        36: '#d6b144',
         }