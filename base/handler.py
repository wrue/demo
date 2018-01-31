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

class RequestHandler(object):

    def __init__(self, request, client_address, tcp_server):
        self.request = request
        self.client_host = client_address[0]
        self.client_port = client_address[1]
        self.server = tcp_server

    def handle(self):
        logger.info("Agent is handling request now.")
        keep_conn = True
    
        while keep_conn:
            try:
                client_id = self.get_client_id()
                request_msg = self.receive_message()
                if request_msg is None:
                    break
                (msg_type, request_info) = request_msg
                keep_conn = self.handle_other_req(request_info, msg_type)
            except Exception, e:
                keep_conn = False
                logger.error("AgentHandler handle_request catch exception:%s" % e.message)
                logger.exception(str(e))
    
        logger.info("handle over")
        
    def handle_other_req(self, request_info, msg_type):
        method = protobuf_handle.get_message_handle(msg_type)
        logger.info("request method is %s" % method)
        (res_msg_type, res_msg) = getattr(self.server.data_manager, method)(request_info)
        self.request.sendall(protobuf_handle.encode(res_msg_type, res_msg))
        if "upgrade" == request_info.scriptPath:
            os.system(r"cd.>C:\local_server\need_shut_down")
        logger.info("the response for request {%s}: %s" % (request_info.requestId, res_msg))
        keep_conn = True
        return keep_conn
    
    def get_client_id(self):
        ch3 = lambda x: sum([256 ** j * int(i) for j, i in enumerate(x.split('.')[::-1])])
        client_id = ch3(self.client_host)
        logger.info("request is from client %s:%s, agent set the client id as %d" %
                    (self.client_host, self.client_port, client_id))
        return client_id
    
    def receive_message(self):
        logger.info("begin decoding all data")
        msg = protobuf_handle.decode_all_data(self.request)
        if msg is None:
            logger.error("Agent received a illegal request!")
            self.request.close()
            return None
        (msg_type, request_info) = msg
        logger.info("Agent received a request, it's type is %s" % msg_type)
        return msg_type, request_info

    
