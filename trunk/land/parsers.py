import logging
import simplejson
from urlparse import parse_qsl
from webob.multidict import MultiDict


def parse(handler_method):

    def parse_request_body(self, *args, **kwargs):
        _parse(self.request)
        handler_method(self, *args, **kwargs)

    return parse_request_body


def _parse(request):
    content_type = request.content_type
    if content_type == 'application/json':
        request.CONTENT = simplejson.loads(request.body)
    elif content_type == 'application/x-www-form-urlencoded':
        request.CONTENT = MultiDict(parse_qsl(request.body))