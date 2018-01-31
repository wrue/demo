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

def decode_all_data(requestHandler):
    dataBuffer = bytes()
    while True:
        try:
            data = requestHandler.recv(AgentChannelProto.MAX_LENGTH)
            if not data:
                logger.info("connection closed")
                return None

            dataBuffer += data
            while True:
                if len(dataBuffer) < AgentChannelProto.MIN_LENGTH:
                    logger.error("length of input string < %d" % AgentChannelProto.MIN_LENGTH)
                    break
                elif len(dataBuffer) > AgentChannelProto.MAX_LENGTH:
                    logger.error("length of input string > %d" % AgentChannelProto.MAX_LENGTH)
                    return None
                signature = socket.ntohl(struct.unpack('I',dataBuffer[0:4])[0])
                if signature != AgentChannelProto.SIGNATURE:
                    logger.error("signature is wrong. expected '%s',acture '%s'" %
                                      (AgentChannelProto.SIGNATURE, signature))
                    return None
                version = socket.ntohs(struct.unpack('H',dataBuffer[8:10])[0])
                if version != AgentChannelProto.VERSION:
                    logger.error("version is wrong. expected '%s',acture '%s'" %
                                      (AgentChannelProto.VERSION, version))
                    return None
                pbLen = socket.ntohl(struct.unpack('I',dataBuffer[4:8])[0])
                if len(dataBuffer) < (pbLen + AgentChannelProto.MIN_LENGTH):
                    logger.info("recv data:%s is not enough: %s" % ((len(dataBuffer)), (pbLen + AgentChannelProto.MIN_LENGTH)))
                    break
                msgType = socket.ntohs(struct.unpack('H',dataBuffer[10:12])[0])
                logger.info("pblen:%s,msgType:%s" % (pbLen,  msgType))
                pbBuf = dataBuffer[12:12 + pbLen]
                msg = get_message_class(msgType)
                if msg is None:
                    return None
                try:
                    msg.ParseFromString(pbBuf) #if parse expction?
                except pbmsg.Error:
                    logger.error("Parse Error!")
                    return None
                return msgType, msg
        except Exception, err:
            logger.error("decode_all_data err %s" % traceback.format_exc(err))
            return None

 def encode(msgType, msg):
    '''
      Encode message object into string which use well-defined protocol

    :param msgType: message-Type
    :param msg: message object
    :return: string
    '''
    signaturePack = struct.pack('I',socket.htonl(AgentChannelProto.SIGNATURE))
    versionPack = struct.pack('H',socket.htons(AgentChannelProto.VERSION))
    msgTypePack = struct.pack('H',socket.htons(msgType))
    msgPack = msg.SerializeToString()
    pbLenPack = struct.pack('I',socket.htonl(len(msgPack)))
    return signaturePack + pbLenPack + versionPack + msgTypePack + msgPack
