#! -*- coding: utf-8 -*-

from masterserver.exc import ServerNotFoundError, ServerCollisionError


class Server(object):
    __serverlist = []

    def __init__(self, ip, port, proxied=False):
        if type(ip) != str or [
            x for x in ip.replace(".", "") if int(x) not in range(10)
        ] or len([x for x in ip.split(".") if len(x) > 0]) != 4:
            raise ValueError("Invalid IP address")

        self.ip = ip
        self.port = int(port)
        self.proxied = proxied

    @classmethod
    def getlist(cls):
        return list(cls.__serverlist)

    @classmethod
    def setlist(cls, serverlist):
        for i in serverlist:
            if not isinstance(i, Server):
                raise ValueError("You have non-Server objects in the list!")
        cls.__serverlist = serverlist

    @classmethod
    def register(cls, ip, port, proxied=False):
        server = Server(ip, port, proxied)
        if server in cls.__serverlist:
            raise ServerCollisionError()
        cls.__serverlist.append(server)
        return server

    def unregister(self):
        self.__serverlist.remove(self)

    @classmethod
    def search(cls, ip=None, port=None, proxied=None, silent=False):
        if proxied is not None:
            servers = [i for i in cls.getlist() if i.proxied == bool(proxied)]
        else:
            servers = cls.getlist()

        if ip is not None:
            oldlist = servers
            servers = []
            for server in servers:
                if ip == server.ip:
                    servers.append(server)

        if port is not None:
            for server in servers:
                if server.port == port:
                    return server

        elif servers:
            return servers

        if not silent:
            raise ServerNotFoundError("Requested server is not registered")

        else:
            if port is not None:
                return None
            else:
                return []

    def __eq__(self, other):
        return isinstance(other, Server) and \
            self.ip == other.ip and \
            self.port == other.port
