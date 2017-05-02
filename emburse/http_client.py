import os
import sys
import textwrap
import warnings

import emburse.errors as error

# - Requests is the preferred HTTP library
# - Google App Engine has urlfetch
# - Fall back to urllib2 with a warning if needed
try:
    import urllib2
except ImportError:
    urllib2 = None

try:
    import requests
except ImportError:
    requests = None
else:
    try:
        # Require version 0.8.8, but don't want to depend on distutils
        version = requests.__version__
        major, minor, patch = [int(i) for i in version.split('.')]
    except Exception:
        # Probably some new version, so it should support verify
        pass
    else:
        if (major, minor, patch) < (0, 8, 8):
            sys.stderr.write(
                'Warning: the Emburse library requires that your Python "requests" library be newer than version 0.8.8'
            )
            requests = None

try:
    from google.appengine.api import urlfetch
except ImportError:
    urlfetch = None


def new_default_http_client(*args, **kwargs):
    if requests:
        impl = RequestsClient
    elif urlfetch:
        impl = UrlFetchClient
    else:
        impl = Urllib2Client
        warnings.warn(
            "Warning: the Emburse library is falling back to urllib2/urllib because neither requests nor pycurl are installed. urllib2's SSL implementation doesn't verify server certificates. For improved security, installing requests."
        )

    return impl(*args, **kwargs)


class HTTPClient(object):
    def __init__(self, verify_ssl_certs=True, proxy=None):
        self._verify_ssl_certs = verify_ssl_certs
        if proxy:
            if type(proxy) is str:
                proxy = {"http": proxy, "https": proxy}
            if not (type(proxy) is dict):
                raise error.EmburseValueError(
                    "Proxy(ies) must be specified as either a string URL or a dict() with string URL under the ""https"" and/or ""http"" keys.")
        self._proxy = proxy.copy() if proxy else None

    def request(self, method, url, headers, post_data=None):
        raise NotImplementedError(
            'HTTPClient subclasses must implement `request`')


class RequestsClient(HTTPClient):
    name = 'requests'

    def __init__(self, timeout=80, **kwargs):
        super(RequestsClient, self).__init__(**kwargs)
        self._timeout = timeout

    def request(self, method, url, headers, post_data=None):
        kwargs = {}
        if self._verify_ssl_certs:
            kwargs['verify'] = os.path.join(
                os.path.dirname(__file__), 'data/ca-certificates.crt')
        else:
            kwargs['verify'] = False

        if self._proxy:
            kwargs['proxies'] = self._proxy

        try:
            try:
                result = requests.request(method,
                                          url,
                                          headers=headers,
                                          data=post_data,
                                          timeout=self._timeout,
                                          **kwargs)
            except TypeError as e:
                raise error.EmburseTypeError(
                    'Warning: It looks like your installed version of the "requests" library is not compatible with Emburse\'s usage thereof. (HINT: The most likely cause is that your "requests" library is out of date. You can fix that by running "pip install -U requests".) The underlying error was: {0}'.format(
                        e))

            content = result.content
            status_code = result.status_code
        except Exception as e:
            self._handle_request_error(e)
        return content, status_code, result.headers

    def _handle_request_error(self, e):
        if isinstance(e, requests.exceptions.RequestException):
            msg = "Unexpected error communicating with Emburse."
            err = "{0}: {1}".format(type(e).__name__, str(e))
        else:
            msg = "Unexpected error communicating with Emburse. It looks like there's probably a configuration issue locally."
            err = "A {0} was raised".format(type(e).__name__)
            if str(e):
                err += " with error message {0}".format(str(e))
            else:
                err += " with no error message"
        msg = textwrap.fill(msg) + "\n\n(Network error: {0})".format(err)
        raise error.EmburseAPIConnectionError(msg)


class UrlFetchClient(HTTPClient):
    name = 'urlfetch'

    def __init__(self, verify_ssl_certs=True, proxy=None, deadline=55):
        super(UrlFetchClient, self).__init__(
            verify_ssl_certs=verify_ssl_certs, proxy=proxy)

        if proxy:
            raise error.EmburseValueError(
                "No proxy support in urlfetch library. ")

        self._verify_ssl_certs = verify_ssl_certs
        self._deadline = deadline

    def request(self, method, url, headers, post_data=None):
        try:
            result = urlfetch.fetch(
                url=url,
                method=method,
                headers=headers,
                validate_certificate=self._verify_ssl_certs,
                deadline=self._deadline,
                payload=post_data
            )
        except urlfetch.Error as e:
            self._handle_request_error(e, url)

        return result.content, result.status_code, result.headers

    def _handle_request_error(self, e, url):
        if isinstance(e, urlfetch.InvalidURLError):
            msg = "The Emburse library attempted to fetch an invalid URL, {0}. This is likely due to a bug ".format(
                url)
        elif isinstance(e, urlfetch.DownloadError):
            msg = "There was a problem retrieving data from Emburse."
        elif isinstance(e, urlfetch.ResponseTooLargeError):
            msg = "There was a problem receiving all of your data from Emburse."
        else:
            msg = "Unexpected error communicating with Emburse."

        msg = textwrap.fill(msg) + "\n\n(Network error: {0})".format(str(e))
        raise error.EmburseAPIConnectionError(msg)


class Urllib2Client(HTTPClient):
    if sys.version_info >= (3, 0):
        name = 'urllib.request'
    else:
        name = 'urllib2'

    def __init__(self, verify_ssl_certs=True, proxy=None):
        super(Urllib2Client, self).__init__(
            verify_ssl_certs=verify_ssl_certs, proxy=proxy)
        self._opener = None
        if self._proxy:
            proxy = urllib2.ProxyHandler(self._proxy)
            self._opener = urllib2.build_opener(proxy)

    def request(self, method, url, headers, post_data=None):
        if sys.version_info >= (3, 0) and isinstance(post_data, str):
            post_data = post_data.encode('utf-8')

        req = urllib2.Request(url, post_data, headers)

        if method not in ('get', 'post'):
            req.get_method = lambda: method.upper()

        try:
            response = self._opener.open(
                req) if self._opener else urllib2.urlopen(req)
            rbody = response.read()
            rcode = response.code
            headers = dict(response.info())
        except urllib2.HTTPError as e:
            rcode = e.code
            rbody = e.read()
            headers = dict(e.info())
        except (urllib2.URLError, ValueError) as e:
            self._handle_request_error(e)
        lh = dict((k.lower(), v) for k, v in dict(headers).iteritems())
        return rbody, rcode, lh

    def _handle_request_error(self, e):
        msg = "Unexpected error communicating with Emburse."
        msg = textwrap.fill(msg) + "\n\n(Network error: ({0})".format(str(e))
        raise error.EmburseAPIConnectionError(msg)