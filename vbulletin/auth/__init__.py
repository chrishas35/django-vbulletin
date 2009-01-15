import logging
logging.warning('Inside auth.__init__')

from django.conf import settings

VBULLETIN_CONFIG = {
    'tableprefix': '',
    'superuser_groupids': (),
    'staff_groupids': (),
}

if hasattr(settings, 'VBULLETIN_CONFIG'):
    VBULLETIN_CONFIG.update(settings.VBULLETIN_CONFIG)