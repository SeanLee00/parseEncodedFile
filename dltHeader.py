#!/usr/bin/env python
import struct
# ================================================================================================================
# https://stackoverflow.com/questions/52240617/i-want-how-to-read-dlt-binary-file-without-dlt-viwer-using-c-fstream
# ================================================================================================================

class dltParser:
    __DLT_HEADER_FMT = ">4s L L 4s"
    __DLT_PAYLOAD_HEADER_FMT = ">1s 1s H 4s 4s L"
    __DLT_EXT_HEADER_FMT = ">1s 1s 4s 4s"

    __HEADER_SIZE = 16
    __PAYLOAD_HEADER_SIZE = 16
    __EXT_HEADER_SIZE = 10
    __header_data = b''
    __active_debug = False

    def __init__(self, debug = False):
        self.__active_debug = debug

    def __read_header(self, file):
        header_bytes = file.read(self.__HEADER_SIZE)
        if not header_bytes:
            print('End of file')
            return False
        magic, sec, msec, ecu_id = struct.unpack(self.__DLT_HEADER_FMT, header_bytes)
        # magic = magic.decode('ascii')
        if self.__active_debug:
            print(f"header_bytes: {header_bytes}, (", len(header_bytes), ")")
            print(f"Magic number: {magic}")
            print(f"sec: {sec}")
            print(f"msec: {msec}")
            print(f"ECU ID: {ecu_id}")
            print(f"\n")
        self.__header_data = self.__header_data + header_bytes
        return True

    def __read_payload_header(self, file):
        payload_header_bytes = file.read(self.__PAYLOAD_HEADER_SIZE)
        if not payload_header_bytes:
            print('End of file')
            return 0
        header_type, msg_cnt, payload_len, ecu_id, ss_id, timestamp = struct.unpack(self.__DLT_PAYLOAD_HEADER_FMT, payload_header_bytes)
        # magic = magic.decode('ascii')
        if self.__active_debug:
            print(f"payload_header_bytes: {payload_header_bytes}, (", len(payload_header_bytes), ")")
            print(f"header_type: {header_type}")
            print(f"msg_cnt: {msg_cnt}")
            print(f"payload_len: {payload_len}")
            print(f"ecu_id: {ecu_id}")
            print(f"timestamp: {timestamp}")
            print(f"\n")
        self.__header_data = self.__header_data + payload_header_bytes
        return payload_len

    def __read_ext_header(self, file):
        ext_header_bytes = file.read(self.__EXT_HEADER_SIZE)
        if not ext_header_bytes:
            print('End of file')
            return False
        msg_info, num_arg, app_id, ctx_id = struct.unpack(self.__DLT_EXT_HEADER_FMT, ext_header_bytes)
        if self.__active_debug:
            print(f"ext_header_bytes: {ext_header_bytes}, (", len(ext_header_bytes), ")")
            print(f"msg_info: {msg_info}")
            print(f"num_arg: {num_arg}")
            print(f"app_id: {app_id}")
            print(f"ctx_id: {ctx_id}")
            print(f"\n")
        self.__header_data = self.__header_data + ext_header_bytes
        return True
# [1673:1673] : 1673:1673 applyNowPlayingInfoChanged: new source: 13 old source: 13 duration: 0 mainText: p{dSBhdCBEYXduQ2l0ed}p sub1: p{dd}p sub2: p{dd}p\x00
# 153+10+16 (6가 모자람)

# [1673:1673] : 1673:1673 applyNowPlayingInfoChanged: new source: 13 old source: 13 duration: 0 mainText: p{dCity at Dawnd}p sub1: p{dd}p sub2: p{dd}p\x00
# 149+10+16 ()
# p{dSBhdCBEYXduQ2l0ed}p
# p{dCity at Dawnd}p


# *** dltheader:        b'DLT\x01 \x842g_#\xb5\x02\x00 ECU1 = k \x00\xb9 ECU1 \x00\x00\x06\x89 \x00\x03\x93\xbe A \x01 STBH NOWP \x00\x02\x00\x00\x99\x00'
# *** dltheader:        b'DLT\x01 \x842g_#\xb5\x02\x00 ECU1 = k \x00\xb5 ECU1 \x00\x00\x06\x89 \x00\x03\x93\xbe A \x01 STBH NOWP \x00\x02\x00\x00\x"payloadlength"\x00'




    def get_header_data(self):
        return self.__header_data

    def update_payload_length(self, payload_header, length):
        payload_index_s = (self.__HEADER_SIZE + 2)

        print("length:                     ", length, ",", hex(length))
        print("self.__EXT_HEADER_SIZE:     ", self.__EXT_HEADER_SIZE, " ,", hex(self.__EXT_HEADER_SIZE))
        print("self.__PAYLOAD_HEADER_SIZE: ", self.__PAYLOAD_HEADER_SIZE, " ,", hex(self.__PAYLOAD_HEADER_SIZE))
        payload_length = length + self.__EXT_HEADER_SIZE + self.__PAYLOAD_HEADER_SIZE + 6

        a = payload_header[:payload_index_s]
        b = payload_header[payload_index_s+2:]
        payload_length_bytes = payload_length.to_bytes(2, byteorder='big')
        c = a + payload_length_bytes + b

        payload_header_ = length.to_bytes(2, byteorder='big')
        # print("c[len(payload_header)-2]: ",c[len(payload_header)-2])
        a = c[:len(payload_header)-3]
        b = c[len(payload_header)-1:]
        c = a + payload_header_ + b
        return c

    def read_payload(self, file):
        self.__header_data = b''
        payload = b''
        if self.__read_header(file) == False:
            return b''
        length = self.__read_payload_header(file) - self.__EXT_HEADER_SIZE - self.__PAYLOAD_HEADER_SIZE
        self.__read_ext_header(file)
        payload = file.read(6)
        self.__header_data = self.__header_data + payload
        length = length - 6
        payload = file.read(length)
        if not payload:
            print('End of file in payload')
            return b''
        if self.__active_debug:
            print(f"payload: {payload}")
        return payload

# # Open the DLT file and read the first 28 bytes (file header)
# with open('log_1_20200920-104358.dlt', 'rb') as file:
#     parser = dltParser()
#     # file.seek(28)
#     # header = file.read(19)
#     # print("aaa", header)
#     # unpack the header data using the format string ">4sB3s3sQ"
#     # a, b, c, d, message_length = struct.unpack(">4sB3s3sQ", header)
    
#     # print the payload length
#     # print(f"Payload Length: {message_length}")
#     # while False:
#     # while True:
#     print(parser.read_payload(file))
#     print(parser.get_header_data())
    # else:
        # break
        # break
