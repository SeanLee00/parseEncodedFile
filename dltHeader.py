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

    def __read_header(self, file):
        header_bytes = file.read(self.__HEADER_SIZE)
        if not header_bytes:
            print('End of file')
            return False
        print(f"header_bytes: {header_bytes}, (", len(header_bytes), ")")
        magic, sec, msec, ecu_id = struct.unpack(self.__DLT_HEADER_FMT, header_bytes)
        # magic = magic.decode('ascii')
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
        print(f"payload_header_bytes: {payload_header_bytes}, (", len(payload_header_bytes), ")")
        header_type, msg_cnt, payload_len, ecu_id, ss_id, timestamp = struct.unpack(self.__DLT_PAYLOAD_HEADER_FMT, payload_header_bytes)
        # magic = magic.decode('ascii')
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
        print(f"ext_header_bytes: {ext_header_bytes}, (", len(ext_header_bytes), ")")
        msg_info, num_arg, app_id, ctx_id = struct.unpack(self.__DLT_EXT_HEADER_FMT, ext_header_bytes)

        print(f"msg_info: {msg_info}")
        print(f"num_arg: {num_arg}")
        print(f"app_id: {app_id}")
        print(f"ctx_id: {ctx_id}")
        print(f"\n")
        self.__header_data = self.__header_data + ext_header_bytes
        return True
        
    def get_header_data(self):
        return self.__header_data

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
