#! /usr/bin/env python
# -*- coding: utf-8 -*-

import masterserver

import logging
logging.getLogger("masterserver").info("Server starting up")

if __name__ == "__main__":
    reactor = masterserver.get_reactor()
    reactor.run()
else:
    application = masterserver.get_application()
