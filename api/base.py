import json
import urllib

import requests


def check_allow(func):
    def wrapper(self, *args, **kwargs):
        if func.__name__ not in self.allow_methods:
            raise NotAllowedMethod
        ret = func(self, *args, **kwargs)
        print(f'[{func.__name__.upper()}] {self.url} -> {ret.status_code}')
        return ret
    return wrapper


class NotAllowedMethod(Exception):
    pass


class API:
    host = ''
    endpoint = ''
    verify = False
    allow_methods = tuple()
    data_to_json = True

    def __init__(self, host=None, **kwargs):
        if host:
            self.host = host
        self.kwargs = kwargs

    @check_allow
    def post(self, data=None, files=None):
        data = data or {}
        files = files or {}

        if self.data_to_json:
            data = json.dumps(data)

        return requests.post(self.url, data=data, headers=self.headers, verify=self.verify, files=files)

    @check_allow
    def patch(self, data=None, files=None):
        data = data or {}
        files = files or {}

        if self.data_to_json:
            data = json.dumps(data)

        return requests.patch(self.url, data=data, headers=self.headers, verify=self.verify, files=files)

    @check_allow
    def get(self, **queries):
        url = self.url
        if queries:
            query_str = urllib.parse.urlencode(queries)
            url += '?' + query_str
        return requests.get(url, verify=self.verify, headers=self.headers)

    @property
    def url(self):
        return self.host + self.endpoint.format(**self.kwargs)

    @property
    def headers(self):
        return {}
