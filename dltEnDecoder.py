#!/usr/bin/env python
import os
import base64
import dltHeader

class dltEnDecoder:
    __argc = 0
    __argv = []
    __s_str = b"p{d"    # start string of encoded persnonal data
    __e_str = b"d}p"    # end string of encoded persnonal data

    def __init__(self, argc, argv):
        self.__argc = argc
        self.__argv = argv

    def __getFileList(self, dir):
        index = 0
        file_list = []
        try:
            is_file = os.path.isfile(dir)

        except Exception as e:
            print(str(e))

        if is_file:
            file_list.append(dir)
        else:
            for file_name in os.listdir(dir):
                if file_name.endswith('_decoded.dlt'):
                    continue
                if file_name.endswith('.dlt'):
                    file_path = os.path.join(dir, file_name)
                    file_list.append(file_path)
                    index += 1
        return file_list

    def __createDecodedFile(self,file_path):
        index = file_path.find(".dlt")
        new_file_path = list(file_path)
        new_file_path.insert(index, "_decoded")
        new_file_path = "".join(new_file_path)
        try:
            file = open(new_file_path, "wb")
        except Exception as e:
            print(str(e))
        else:
            return file

    def __rotateData(self, data, rotate_count):
        if rotate_count < 0:
            rotate_count = (rotate_count*-1) % len(data)
            rotate_count = (rotate_count*-1)
        else:
            rotate_count = rotate_count % len(data)
        data = data[rotate_count:] + data[:rotate_count]
        return data

    def __decode_payload(self, payload):
        decoded_payload = payload
        try:
            index1 = payload.find(self.__s_str)
            index2 = payload.find(self.__e_str)
            c = ""
            while index1 != -1 and index2 != -1:
                s_pos = index1 + len(self.__s_str)
                e_pos = index2
                encoded_data = payload[s_pos:e_pos]
                if e_pos - s_pos > 0:
                    decoded_data = self.decode_data(-5, encoded_data)
                    a = payload[:s_pos - len(self.__s_str)]
                    b = payload[e_pos + len(self.__e_str):]
                    decoded_payload = a + decoded_data + b
                else:
                    # print("\nexit checking personal data: ", decoded_payload)
                    return decoded_payload
                index1 = payload.find(self.__s_str, index2 + len(self.__e_str))
                index2 = payload.find(self.__e_str, index2 + len(self.__e_str))
        except Exception as e:
            print(str(e))
        finally:
            return decoded_payload

    def __do_decording(self,file_path):
        try:
            with open(file_path, 'rb') as file:
                with self.__createDecodedFile(file_path) as newFile:
                    print("newFile:", newFile)
                    parser = dltHeader.dltParser()
                    while True:
                        payload = parser.read_payload(file)
                        # if not payload:
                            # break
                        # get header data
                        if parser.isFileEnd():
                            break
                        dltheader = parser.get_header_data()
                        # decoding...
                        decoded_payload = self.__decode_payload(payload)
                        if payload != decoded_payload:
                            dltheader = parser.update_header_info(dltheader, len(decoded_payload))
                        # write header data to the new file
                        newFile.write(dltheader)
                        # write payload to the new file
                        newFile.write(decoded_payload)
        except Exception as e:
            print(str(e))

    def decode_data(self, rotate_count, encoded_data):
        try:
            encoded_data = self.__rotateData(encoded_data, rotate_count)
            print("\nencoded data: ", encoded_data)
            print("\n")
            decoded_data = base64.b64decode(encoded_data)
        except Exception as e:
            print("Error!\nDeconding error on [", encoded_data, "] : ", str(e))

        finally:
            unicode_string = decoded_data.decode('utf-8')
            return unicode_string

    def encode_data(self, rotate_count, data):
        encoded_data = b""
        try:
            data_bytes = data.encode('utf-8') 
            encoded_data = base64.b64encode(data_bytes)
            # encoded_data = self.__rotateData(encoded_data, rotate_count)
        except Exception as e:
            print("encoding error in ", data, ", ", str(e))
        finally:
            unicode_string = encoded_data.decode('utf-8')
            return unicode_string

    def decode(self):
        print("decoding")
        if self.__argc != 2:
            return False
        else:
            self.dir = self.__argv[1]
            try:
                # file_list = self.__getFileList(self.dir)
                # for file_path in file_list:
                    print("file_path: ", "./log_1_20231024-114122.dlt")
                    self.__do_decording("./log_1_20231024-114122.dlt")
            except Exception as e:
                print(str(e))
        return True
