# coding=utf-8
import SocketServer
import ssl
import socket
import traceback


class LocalServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address, RequestHandlerClass, data_manager):
        """add some variable for all the threading to share and
        overwrite some attributes for server,for example:allow_reuse_address..."""
        SocketServer.ThreadingTCPServer.__init__(self, server_address, RequestHandlerClass)
        self.data_manager = data_manager
        self.is_waiting_to_shutdown = False
        
    def get_request(self):
        try:
            newsocket, fromaddr = self.socket.accept()
            connstream = ssl.wrap_socket(newsocket,
                                         server_side=True,
                                         ssl_version=ssl.PROTOCOL_TLSv1_2,
                                         cert_reqs=ssl.CERT_REQUIRED,
                                         certfile="",
                                         keyfile="",
                                         ca_certs="")
            return connstream, fromaddr
        except Exception, e:
            raise socket.error

    def destroy_self(self):
        self.shutdown()
        self.server_close()
