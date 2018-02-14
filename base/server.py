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

    def destroy_self(self):
        self.shutdown()
        self.server_close()
