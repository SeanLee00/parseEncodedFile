#!/usr/bin/env python
import struct

# https://stackoverflow.com/questions/52240617/i-want-how-to-read-dlt-binary-file-without-dlt-viwer-using-c-fstream
# ------------------------------------------------------------------------------------------------
#      4    |   8       |   4       |   16
# ------------------------------------------------------------------------------------------------
# DLT +0x01 | timestamp | ECU ID    | Dlt log or trace message
# ------------------------------------------------------------------------------------------------
#                                   | HEADER
# ------------------------------------------------------------------------------------------------


# ---------------------------------- Header(16bytes) ---------------------------------------------
# ------------------------------------------------------------------------------------------------
#   1   |   1           |   2       |   4       |   4           |   4       |
# ------------------------------------------------------------------------------------------------
# header| message count | Length    | ECU ID    | Session ID    | Timestamp |
# ------------------------------------------------------------------------------------------------
#                                   |
# ------------------------------------------------------------------------------------------------

# ------------------------------ Extended Header (16bytes)----------------------------------------
# ------------------------------------------------------------------------------------------------
#   1           |   1                   |   4               |   4           |   4   |   2
# ------------------------------------------------------------------------------------------------
# Message Info  | number of arguments   | Application ID    | Context ID    |   ?   | payload length
# ------------------------------------------------------------------------------------------------
#                                   |
# ------------------------------------------------------------------------------------------------


class dltParser:
    __DLT_HEADER_FMT = ">4s L L 4s"
    __DLT_MESSAGE_HEADER_FMT = ">1s 1s H 4s 4s L"
    __DLT_EXT_HEADER_FMT = ">1s 1s 4s 4s 4s 2s"

    __DLT_HEADER_SIZE = 16
    __MESSAGE_HEADER_SIZE = 16
    __EXT_HEADER_SIZE = 16
    __MESSAGE_HEADER_OFFSET_TO_LENGTH = 2
    __MESSAGE_LENGTH_SIZE = 2
    __header_data = b''
    __active_debug = False

    def __init__(self, debug = False):
        self.__active_debug = debug

    def debug(self, debug):
        self.__active_debug = debug

    def __read_header(self, file):
        header_bytes = file.read(self.__DLT_HEADER_SIZE)
        if not header_bytes:
            print('End of file')
            return b''
        magic, sec, msec, ecu_id = struct.unpack(self.__DLT_HEADER_FMT, header_bytes)
        if self.__active_debug:
            print(f"header_bytes: {header_bytes}, (", len(header_bytes), ")")
            print(f"Magic number: {magic}")
            print(f"sec: {sec}")
            print(f"msec: {msec}")
            print(f"ECU ID: {ecu_id}")
            print(f"\n")
        return header_bytes

    def __read_message_header(self, file):
        message_header_bytes = file.read(self.__MESSAGE_HEADER_SIZE)
        if not message_header_bytes:
            print('End of file')
            return [b'', b'']
        header_type, msg_cnt, message_len, ecu_id, ss_id, timestamp = struct.unpack(self.__DLT_MESSAGE_HEADER_FMT, message_header_bytes)
        if self.__active_debug:
            print(f"message_header_bytes: {message_header_bytes}, (", len(message_header_bytes), ")")
            print(f"header_type: {header_type}")
            print(f"msg_cnt: {msg_cnt}")
            print(f"length: {message_len}")
            print(f"ecu_id: {ecu_id}")
            print(f"timestamp: {timestamp}")
            print(f"\n")
        return [message_len, message_header_bytes]

    def __read_ext_header(self, file):
        ext_header_bytes = file.read(self.__EXT_HEADER_SIZE)
        if not ext_header_bytes:
            print('End of file')
            return [0, b'']
        msg_info, num_arg, app_id, ctx_id, unknown, payload_length = struct.unpack(self.__DLT_EXT_HEADER_FMT, ext_header_bytes)
        if self.__active_debug:
            print(f"ext_header_bytes: {ext_header_bytes}, (", len(ext_header_bytes), ")")
            print(f"msg_info: {msg_info}")
            print(f"num_arg: {num_arg}")
            print(f"app_id: {app_id}")
            print(f"ctx_id: {ctx_id}")
            print(f"unknown: {unknown}")
            print(f"payload_length: {payload_length}")
            print(f"\n")
        return [payload_length, ext_header_bytes]
# 153+10+16 (6 마지막 6byte에 payload length가 기록됨)
# *** dltheader:        b'DLT\x01 \x842g_#\xb5\x02\x00 ECU1 = k \x00\xb5        ECU1 \x00\x00\x06\x89 \x00\x03\x93\xbe A \x01 STBH NOWP \x00\x02\x00\x00  \x99\x00'
                                                                #message length                                                                            payload length
# dltheader_org:        b'DLT\x01\xb2qg_4\xfe\x0b\x00ECU1=\n\x01L   ECU1\x00\x00T\xcf\t\xa7\x9b?A\x01PUMGPUMG\x00\x02\x00\x00,   \x01'
# dltheader_updated:    b'DLT\x01\xb2qg_4\xfe\x0b\x00ECU1=\n\x01\x1cECU1\x00\x00T\xcf\t\xa7\x9b?A\x01PUMGPUMG\x00\x02\x00\x00\xfc\x01'
    def get_header_data(self):
        return self.__header_data

    def update_header_info(self, message_header, payload_length):
        message_header_new = message_header
        message_length_offset = (self.__DLT_HEADER_SIZE + self.__MESSAGE_HEADER_OFFSET_TO_LENGTH)
        message_length = self.__MESSAGE_HEADER_SIZE + self.__EXT_HEADER_SIZE + payload_length
        # update message length
        msg_front = message_header_new[:message_length_offset]
        msg_end = message_header_new[message_length_offset+self.__MESSAGE_LENGTH_SIZE:]
        message_length_bytes = message_length.to_bytes(2, byteorder='big')
        message_header_new = msg_front + message_length_bytes + msg_end
        # update payload length
        payload_length_new = payload_length.to_bytes(2, byteorder='little')
        msg_front = message_header_new[:len(message_header_new)-2]
        msg_end = message_header_new[len(message_header_new):]
        message_header_new = msg_front + payload_length_new + msg_end

        if self.__active_debug:
            print(f"\nupdate_header_info[message_header]\t: {message_header}")
            print(f"update_header_info[message_header_new]\t: {message_header_new}")
            print(f"update_header_info[payload_length_new]: {payload_length_new}")
            print(f"update_header_info[payload_length]: {payload_length}")
            print(f"update_header_info[message_length]: {message_length}\n")
        return message_header_new

    def read_payload(self, file):
        dlt_header = self.__read_header(file)
        if dlt_header == b'':
            print('End of file in header')
            return b''
        
        # read message header
        [mesage_len, message_header] = self.__read_message_header(file)

        # read extend header
        payload_length_bin, ext_header = self.__read_ext_header(file)
        payload_length = int.from_bytes(payload_length_bin, byteorder='little')
        payload_length1 = int.from_bytes(payload_length_bin, byteorder='big')

        if payload_length != (mesage_len - 32):
            print('=> Error! payload_length is ', payload_length)
            print('=> Error! payload_length1 is ', payload_length1)
            # payload_length = mesage_len - 32

            print(f"\ndlt_header\t: {dlt_header}")
            print(f"message_header\t: {message_header}")
            print(f"ext_header\t: {ext_header}")
            print(f"payload_length\t: {payload_length}")
            print(f"mesage_len\t: {mesage_len}")
            print(f"header_data\t: {self.__header_data}")
            print(f"payload\t\t: {payload}\n")
            return b''
        
        payload = file.read(payload_length)

        # update header data
        self.__header_data = dlt_header + message_header + ext_header

        if self.__active_debug:
            print(f"\ndlt_header\t: {dlt_header}")
            print(f"message_header\t: {message_header}")
            print(f"ext_header\t: {ext_header}")
            print(f"payload_length\t: {payload_length}")
            print(f"mesage_len\t: {mesage_len}")
            print(f"header_data\t: {self.__header_data}")
            print(f"payload\t\t: {payload}\n")

        if not payload:
            print('End of file in payload')
            print(f"\ndlt_header\t: {dlt_header}")
            print(f"message_header\t: {message_header}")
            print(f"ext_header\t: {ext_header}")
            print(f"payload_length\t: {payload_length}")
            print(f"mesage_len\t: {mesage_len}")
            print(f"header_data\t: {self.__header_data}")
            print(f"payload\t\t: {payload}\n")
            return b''
        return payload
