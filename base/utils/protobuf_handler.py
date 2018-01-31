import struct
import socket
import traceback
import google.protobuf.message as pbmsg
import descriptor_local as mgntDes
from base import log

logger = log.get_logger()


class AgentChannelProto(object):
    SIGNATURE = 0x5aa5ff00
    VERSION = 1
    MIN_LENGTH = 12
    MAX_LENGTH = 64 * 1024
    HA_MSG_TYPE_MIN = 301
    HA_MSG_TYPE_MAX = 400
    DB_MANAGE_TYPE_MAX = 2000


MessageDict = {
    mgntDes.MSG_RPC_RESPONSE: mgntDes.RpcResponse,
    mgntDes.MSG_EXEC_CMD: mgntDes.ExecCmdReq,
}

HandleDict = {
    mgntDes.MSG_EXEC_CMD: 'exec_cmd',
}

def get_message_class(msgType):
    if msgType in MessageDict.keys():
        return MessageDict[msgType]() #TODO modify as MessageDict.get(msgType)
    else:
        logger.error("msgType:%s not exist in MessageDict" % msgType)
        return None


def get_message_handle(msgType):
    if msgType in HandleDict.keys():
        return HandleDict[msgType]
    else:
        logger.error("msgType:%s not exist in HandleDict" % msgType)
        return None
