import urllib
import platform
from pytz import utc as UTC
import datetime
import emburse.util as util
import emburse.errors as error
import emburse.http_client as http_client
import emburse.version as version


class Requestor(object):
    def __init__(self, token=None, proxy=None, client=None,
                 verify_ssl_certs=True):
        self.api_base = 'https://api.emburse.com/{api_version}'.format(
            api_version=version.API_VERSION)
        self.auth_token = token

        self._client = client or http_client.new_default_http_client(
            verify_ssl_certs=verify_ssl_certs, proxy=proxy)

    def request(self, method, url_, params=None, headers=None):
        """
        Request, makes a request to the emburse API
        Args:
            method (str): The HTTP method used to send request 
            url_ (str): The URL to make request to. 
            params (dict): Params to send to the API 
            headers (dict): Custom Headers to send to with request. 

        Returns:
            set (dict, str): Dict of response body and the api key in a set.
        """
        resp_body, resp_code, resp_headers, my_api_key = self.request_raw(
            method.lower(), url_, params, headers)
        resp = self.interpret_response(resp_body, resp_code, resp_headers)
        return resp, my_api_key

    def handle_api_error(self, resp_body, resp_code, resp, resp_headers):
        """
        Handle API Error, used to tell what kind of error was sent back from 
        emburse and raise a valid Exception.
        Args:
            resp_body: 
            resp_code: 
            resp: 
            resp_headers: 

        Returns:

        """
        try:
            err = resp['detail']
        except (KeyError, TypeError):
            raise error.EmburseAPIError(
                "Invalid response object from API: {0} (HTTP response code was {1})".format(
                    repr(resp_body), resp_code),
                resp_body,
                resp_code,
                resp
            )

        if resp_code in [400, 404]:
            raise error.EmburseInvalidRequestError(err.get('message'),
                                                   err.get('param'), resp_body,
                                                   resp_code, resp,
                                                   resp_headers)
        elif resp_code == 401:
            raise error.EmburseAuthenticationError(err.get('message'),
                                                   resp_body, resp_code, resp,
                                                   resp_headers)
        elif resp_code == 403:
            raise error.EmbursePermissionError(err.get('message'), resp_body,
                                               resp_code, resp, resp_headers)
        else:
            raise error.EmburseAPIError(err.get('message'), resp_body,
                                        resp_code, resp, resp_headers)

    def request_raw(self, method, url, params=None, supplied_headers=None):
        """
        Request Raw, method for issuing an API call
        """

        if self.auth_token:
            my_auth_token = self.auth_token
        else:
            raise error.EmburseAttributeError('Auth Token not set!')

        abs_url = '{base}{passed}'.format(base=self.api_base, passed=url)

        if method == 'get' or method == 'delete':
            encoded_params = util.urlencode(
                list(self.api_encode(params or {}))
            )
            if params:
                abs_url = self.build_api_url(abs_url, encoded_params)
            post_data = None
        elif method == 'post':
            if not supplied_headers:
                supplied_headers = {'Content-Type': 'application/json'}
            post_data = util.json.dumps(self.api_encode_post(params or {}))
        else:
            raise error.EmburseAPIConnectionError('Unrecognized HTTP method {0}'.format(method))

        ua = {
            'bindings_version': version.VERSION,
            'lang': 'python',
            'publisher': 'pigeonly',
            'httplib': self._client.name,
        }
        for attr, func in [['lang_version', platform.python_version], ['platform', platform.platform],
                           ['uname', lambda: ' '.join(platform.uname())]]:
            try:
                val = func()
            except Exception as e:
                val = "!! {0}".format(e)
            ua[attr] = val

        headers = {
            'X-Client-User-Agent': util.json.dumps(ua),
            'User-Agent': 'Pigeonly Emburse/v1 PythonBindings/{0}'.format(version.VERSION),
            'Authorization': 'Token {0}'.format(my_auth_token)
        }

        if supplied_headers is not None:
            for key, value in supplied_headers.iteritems():
                headers[key] = value

        resp_body, resp_code, resp_headers = self._client.request(method, abs_url, headers, post_data)

        util.logger.info(
            '{req_method} {req_url} {code}'.format(req_method=method.upper(), req_url=abs_url, code=resp_code)
        )
        util.logger.debug(
            'API request to {req_url} returned (response code, response body) of ({code}, {body})'.format(
                req_url=abs_url,
                code=resp_code,
                body=resp_body
            )
        )
        return resp_body, resp_code, resp_headers, my_auth_token

    def interpret_response(self, resp_body, resp_code, resp_headers):
        try:
            if hasattr(resp_body, 'decode'):
                resp_body = resp_body.decode('utf-8')
            resp = util.json.loads(resp_body)
        except Exception:
            raise error.EmburseAPIError(
                "Invalid response body from API: {0} (HTTP response code was {1})".format(
                    resp_body, resp_code),
                resp_body,
                resp_code,
                resp_headers
            )
        if not (200 <= resp_code < 300):
            self.handle_api_error(resp_body, resp_code, resp, resp_headers)
        return resp

    def api_encode_post(self, data):
        """
        API Encode Post, method to generate post data to be sent to API
        Args:
            data (dict): Dictionary of data to be sent to API 

        Returns: A Dictionary of API safe values.

        """
        params = {}
        for key, value in data.items():
            key = util.utf8(key)
            if value is None:
                params[key] = None
                continue
            elif isinstance(value, list) or isinstance(value, tuple):
                params[key] = []
                for sv in value:
                    params[key].append(self.api_encode_post(sv))
            elif isinstance(value, dict):
                params[key] = self.api_encode_post(value)
            elif isinstance(value, datetime.datetime):
                params[key] = util.utf8(self.encode_datetime(value))
            elif isinstance(value, bool):
                params[key] = value
            else:
                params[key] = util.utf8(value)

        return params

    def encode_datetime(self, dttime):
        """
        Encode Datetime, converts datetime objects to ISO 8601 format
        :param dttime: datetime
        :return: ISO 8601 formatted datetime
        :rtype: str
        """
        if dttime.tzinfo and dttime.tzinfo.utcoffset(dttime) is not None:
            utc_timestamp = dttime.astimezone(tz=UTC)
        else:
            utc_timestamp = dttime.replace(tzinfo=UTC)

        return utc_timestamp.isoformat()

    def encode_nested_dict(self, key, data, fmt='{0}[{1}]'):
        """
        Encode Nested Dict, method to api encode a nested dict.
        :param key: Key of the parent dict
        :param data: Nested Dict
        :param fmt: Format to encode
        :return: Encoded values
        """
        d = {}
        for sub_key, sub_value in data.items():
            d[fmt.format(key, sub_key)] = sub_value
        return d

    def api_encode(self, data):
        """
        API Encode, generator function to encode data for sending to API
        :param data: Data to be encoded
        :return: Encoded Data set (key, value)
        :rtype: set
        """
        for key, value in data.items():
            key = util.utf8(key)
            if value is None:
                yield (key, 'null')
            elif isinstance(value, list) or isinstance(value, tuple):
                for sv in value:
                    if isinstance(sv, dict):
                        sub_dict = self.encode_nested_dict(key, sv,
                                                           fmt='{0}[][{1}]')
                        for k, v in self.api_encode(sub_dict):
                            yield (k, v)
                    else:
                        yield ("{0}[]".format(key), util.utf8(sv))
            elif isinstance(value, dict):
                sub_dict = self.encode_nested_dict(key, value)
                for sub_key, sub_value in self.api_encode(sub_dict):
                    yield (sub_key, sub_value)
            elif isinstance(value, datetime.datetime):
                yield (key, util.utf8(self.encode_datetime(value)))
            else:
                yield (key, util.utf8(value))

    def build_api_url(self, url, query):
        scheme, netloc, path, base_query, fragment = util.urlparse.urlsplit(url)

        if base_query:
            query = '{0}&{1}' % (base_query, query)

        return util.urlparse.urlunsplit((scheme, netloc, path, query, fragment))
