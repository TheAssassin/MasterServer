# -*- coding: utf-8 -*-

from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site
from twisted.internet import reactor
from .wsgiapp import app

resource = WSGIResource(reactor, reactor.getThreadPool(), app)
httpsite = Site(resource)
