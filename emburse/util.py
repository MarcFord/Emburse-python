import sys
import logging


logger = logging.getLogger('emburse')


__all__ = ['StringIO', 'parse_qsl', 'json', 'utf8']

try:
    # When cStringIO is available
    import cStringIO as StringIO
except ImportError:
    if sys.version_info < (3, 0):
        import StringIO
    else:
        from io import StringIO

try:
    from urlparse import parse_qsl
except ImportError:
    # Python < 2.6
    from cgi import parse_qsl

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

try:
    from urllib import quote_plus
except ImportError:
    from urllib.parse import quote as quote_plus

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

try:
    import json
except ImportError:
    json = None

if not (json and hasattr(json, 'loads')):
    try:
        import simplejson as json
    except ImportError:
        if not json:
            raise ImportError(
                "Emburse requires a JSON library, such as simplejson. "
                "HINT: Try installing the "
                "python simplejson library via 'pip install simplejson' or "
                "'easy_install simplejson'!")
        else:
            raise ImportError(
                "Emburse requires a JSON library with the same interface as "
                "the Python 2.6 'json' library.  You appear to have a 'json' "
                "library with a different interface.  Please install "
                "the simplejson library.  HINT: Try installing the "
                "python simplejson library via 'pip install simplejson' "
                "or 'easy_install simplejson'")


def utf8(value):
    """
    UTF8, makes value a utf8 encoded string.
    :param value: String to encode to utf8
    :return: Utf8 encoded string
    :rtype: str
    """
    if sys.version_info < (3, 0) and isinstance(value, unicode):
        return value.encode('utf-8')
    return value
