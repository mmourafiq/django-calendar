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
        1: '#9767a1',
        2: '#e67399',        
        3: '#6d5fca',
        4: '#8392ae',
        5: '#59bfb3',
        6: '#599a48',
        7: '#80ad30',
        8: '#9ea332',
        9: '#bd8528',
        10: '#d16f46',
        11: '#e49442',
        12: '#d6b144',
         }