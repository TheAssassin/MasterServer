# -*- coding: utf-8 -*-


class ServerException(Exception):
    pass


class ServerNotFoundError(ServerException):
    pass


class ServerCollisionError(ServerException):
    pass
