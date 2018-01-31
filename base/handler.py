import abc
import six
import os
import SocketServer
from base import log
import base.utils.protobuf_handle as protobuf_handle

logger = log.get_logger()
HA_LEASE_TIMEOUT = None


@six.add_metaclass(abc.ABCMeta)
class ServerHandler(SocketServer.BaseRequestHandler, object):
    def handle(self):
        try:
            req_handler = RequestHandler(self.request, self.client_address, self.server)
            req_handler.handle()
        except Exception,e:
            logger.error("AgentHandler handle catch exception:%s" % e.message)
            logger.exception(str(e))
