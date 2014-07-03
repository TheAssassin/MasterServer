# -*- coding: utf-8 -*-

from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from masterserver.exc import ServerCollisionError
from .models import Server
import logging
import socket


class SauerbratenStyleProtocol(LineReceiver):
    delimiter = '\n'

    def __init__(self):
        self.logger = logging.getLogger("masterserver:sauerbraten")

    def timeoutReached(self, server, transport):
        self.logger.info(
            "server reached timeout: %s:%d" % (server.ip, server.port)
        )
        server.unregister()
        transport.loseConnection()

    def connectionMade(self):
        peer = self.transport.getPeer()
        ip = peer.host
        port = peer.port
        self.logger.debug("client connected: %s:%d" % (ip, port))

    def lineReceived(self, line):
        def fail():
            self.transport.write("failreg\n")
            self.transport.loseConnection()

        def success(server):
            self.transport.write("succreg\n")
            task = reactor.callLater(60*60, self.timeoutReached,
                                     server, self.transport)

        line = line.rstrip("\r").rstrip("\n")
        if line.startswith("regserv"):
            try:
                ip = self.transport.getPeer().host
                port = int(line.split()[1])
                server = Server.register(ip, port)
            except ServerCollisionError:
                self.logger.error(
                    "server already registered: %s:%d" % (ip, port)
                )
                fail()
            except (ValueError, IndexError):
                self.logger.error(
                    "bad syntax for registration: %s" % line
                )
                fail()
            else:
                self.logger.info(
                    "server registered successfully: %s:%d" % (ip, port)
                )
                success(server)

        elif line.strip() == "list":
            for server in Server.getlist():
                self.transport.write(
                    "addserver %s %d\n" % (server.ip, server.port)
                )
                self.transport.loseConnection()

        else:
            self.logger.error("client wanted something unknown: %s" % line)
            self.transport.loseConnection()


class SauerbratenStyleFactory(ServerFactory):
    protocol = SauerbratenStyleProtocol

    def startFactory(self):
        LoopingCall(
            lambda: query_other_master("sauerbraten.org", 28787)
        ).start(300)


def query_other_master(ip, port, bufsize=65536):
    logger = logging.getLogger("masterserver:sauerbraten")

    logger.info("fetching servers from masterserver %s:%d" % (ip, port))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.debug("connecting to %s:%d" % (ip, port))
    sock.connect((ip, port))

    logger.debug("retrieving server list")
    sock.send("list\n")

    data = ""
    while True:
        buffer = sock.recv(bufsize)
        data += buffer
        if not buffer:
            break

    for line in data.split("\n"):
        if line.startswith("addserver"):
            try:
                ip = line.split()[1]
                port = int(line.split()[2])
                Server.register(ip, port, proxied=True)
            except ServerCollisionError:
                logger.debug("server already registered: %s:%d" % (ip, port))
            except (IndexError, ValueError):
                logger.warn("error parsing line: %s" % line)
            else:
                logger.info(
                    "server from other masterserver "
                    "registered: %s:%d" % (ip, port)
                )

    sock.close()
    logger.info("querying other masterserver finished successfully")
