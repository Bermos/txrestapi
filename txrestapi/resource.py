import re
from itertools import ifilter
from twisted.web.resource import Resource
from twisted.web.error import NoResource

class APIResource(Resource):

    _registry = None

    def __init__(self, *args, **kwargs):
        Resource.__init__(self, *args, **kwargs)
        self._registry = []

    def _get_callback(self, request):
        filterf = lambda t:t[0] in (request.method, 'ALL')
        for m, r, cb in ifilter(filterf, self._registry):
            result = r.search(request.path)
            if result:
                return cb, result.groupdict()
        return None, None

    def register(self, method, regex, callback):
        self._registry.append((method, re.compile(regex), callback))

    def unregister(self, method=None, regex=None, callback=None):
        if regex is not None: regex = re.compile(regex)
        for m, r, cb in self._registry[:]:
            if not method or (method and m==method):
                if not regex or (regex and r==regex):
                    if not callback or (callback and cb==callback):
                        self._registry.remove((m, r, cb))

    def getChild(self, name, request):
        r = self.children.get(name, None)
        if r is None:
            # Go into the thing
            callback, args = self._get_callback(request)
            if callback is None:
                return NoResource()
            else:
                return callback(request, **args)
        else:
            return r
