# -*- coding: utf-8 -*-

from twisted.application import internet, service
from masterserver.sauerfork.sauerbraten import SauerbratenStyleFactory
from twisted.internet import reactor
from twisted.python import log
import logging


observer = log.PythonLoggingObserver(loggerName="twisted")
observer.start()


def configure_logging(filename=None, loglevel=logging.INFO):
    for loggername in ("twisted",
                       "masterserver",
                       "masterserver:sauerbraten"):
        logger = logging.getLogger(loggername)
        logger.setLevel(loglevel)

        if filename is not None:
            handler = logging.FileHandler(filename)
        else:
            handler = logging.StreamHandler()

        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: [{0}] %(message)s'.format(loggername)
        ))
        logger.addHandler(handler)


def get_reactor():
    configure_logging(loglevel=logging.DEBUG)
    reactor.listenTCP(28787, SauerbratenStyleFactory())
    return reactor


def get_application():
    configure_logging(filename="server.log")
    application = service.Application("masterserver")
    internet.TCPServer(
        28787, SauerbratenStyleFactory()
    ).setServiceParent(application)
    return application
