#!/usr/bin/env python
import sys
import os
import base64
import re
import dltHeader

class dltDecoder:
    __argc = 0
    __argv = []
    __exec = ""
    __s_str = b"p{d"    # start string of encoded persnonal data
    __e_str = b"d}p"    # end string of encoded persnonal data
    __shift = 5         # shift of base64 when it is encoded
    
    def __init__(self, argc, argv):
        self.__argc = argc
        self.__argv = argv
        self.__exec = argv[0]

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

    def __get_length_index(self, line):
        return line.rfind(b"ECU1") - 1

    def __get_payload_size_index(self, line):
        return line.rfind(b'\0', 0, len(line) - 2) - 1
    
    def __get_payload_size(self, line):
        index = self.__get_payload_size_index(line)
        return int(line[index])

    def __update_payload(self, input):
        result = b"PRESENT PERSONAL DATA"
        expression = re.compile(b"p{d.+d}p")
        is_match = expression.search(input)
        if is_match:
            texts = is_match.group()
            line = input.decode("utf-8")
            for text in texts:
                etext = text[3:-3].decode("utf-8")
                decoded_text = self.__decode(etext).encode("utf-8")
                line = line.replace(text.decode("utf-8"), decoded_text.decode("utf-8"))
            return line.encode("utf-8")
        return input
    
    def __update(self, line):
        payloadSize = self.__get_payload_size(line)
        payloadSizeIndex = self.__get_payload_size_index(line)
        lenghtIndex = self.__get_length_index(line)
        index = self.__get_payload_size_index(line) + 1
        payload = line[index + 1:]

        newPayload = self.__update_payload(payload)
        delta = len(newPayload) - payloadSize + 1
        header = line[:index]
        header[payloadSizeIndex] += delta
        header[lenghtIndex] += delta
        
        return header + '\0' + newPayload

    def __rotateData(self, data, rotate_count):
        if rotate_count < 0:
            rotate_count = (rotate_count*-1) % len(data)
            rotate_count = (rotate_count*-1)
        else:
            rotate_count = rotate_count % len(data)
        data = data[rotate_count:] + data[:rotate_count]
        return data

    def decode_data(self, rotate_count, encoded_data):
        try:
            encoded_data = self.__rotateData(encoded_data, rotate_count)
            decoded_data = base64.b64decode(encoded_data)
        except Exception as e:
            print("Error!\nDeconding error on [", encoded_data, "] : ", str(e))
        
        finally:
            return decoded_data

    def encode_data(self, rotate_count, data):
        encoded_data = b""
        try:
            encoded_data = base64.b64encode(data)
            encoded_data = self.__rotateData(encoded_data, rotate_count)
        except Exception as e:
            print("encoding error in ", data, ", ", str(e))
        finally:
            return encoded_data

    def __decode_and_write(self, line, file):
        file.write(self.__update(line))
    
    def __decode(self, line, file):        
        try:
            index1 = line.find(self.__s_str)
            index2 = line.find(self.__e_str)
            c = ""
            while index1 != -1 and index2 != -1:
                s_pos = index1 + len(self.__s_str)
                e_pos = index2
                encoded_data = line[s_pos:e_pos]                
                if e_pos - s_pos > 0:
                    decoded_data = self.decode_data(-5, encoded_data)
                    # a = line[:s_pos - len(self.__s_str)]
                    # b = line[e_pos + len(self.__e_str):]
                    a = line[:s_pos]
                    b = line[e_pos:]
                    # a = line[:s_pos]
                    # b = line[e_pos:]
                    c = a + encoded_data + b
                    print("decoded_data: ", encoded_data)
                    file.write(c)
                else:
                    print("exit checking personal data")
                    break
                index1 = line.find(self.__s_str, index2 + len(self.__e_str))
                index2 = line.find(self.__e_str, index2 + len(self.__e_str))
            # file.write(c)
        except Exception as e:
            print(str(e))

    def __do_decording(self,file_path):
        try:            
            with open(file_path, 'rb') as file:
                with self.__createDecodedFile(file_path) as newFile:
                    print("newFile:", newFile)
                    parser = dltHeader.dltParser()
                    while True:
                        # read payload
                        payload = parser.read_payload(file)
                        if not payload:
                            break
                        # get heade data
                        dltheader = parser.get_header_data()
                        # write header data to the new file
                        newFile.write(dltheader)
                        # write payload data to the new file
                        newFile.write(payload)
            for line in file:
                self.__decode_and_write(line, newFile)
        except Exception as e:
            print(str(e))
        
    def __run(self):
        self.dir = self.__argv[1]
        try:
            file_list = self.getFileList(self.dir)
            for file_path in file_list:
                print("file_path: ", file_path)
                self.__do_decording(file_path)
        except Exception as e:
            print(str(e))

    def decoding(self):
        print("decoding")
        if self.__argc != 2:
            self.printUsage()
        else:
            self.__run()

    def getFileList(self, dir):
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
    
    def printUsage(self):
        print("Usage >")
        print(sys.argv[0], " option data")
        print("\n\t[directory or file path] : deconding all dlt files under 'directory_path'")
        print("\t\t", sys.argv[0],  " ./ ")
        print("\t\t", sys.argv[0],  " test.dlt ")
        print("\t-e [data]: enconding for input data")
        print("\t\t", sys.argv[0],  " -e abcdefg ")
        print("\t-d [data]: deconding for input data")
        print("\t\t", sys.argv[0],  " -d  GVmZw==YWJjZ")
        print("\t-c [dlt file]: convert dlt to text")
        print("\t\t", sys.argv[0],  " -c")

def convertDlt2Txt():
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'

    error = False
    for x in os.listdir("."):
        if not x.endswith("dlt"):
            continue

        basename = os.path.splitext(x)[0]
        print('Converting for ' + basename)
        cmd = "dlt-viewer -s -u -c %s %s.log &> /dev/null" % (x, basename)
        if os.system(cmd):
            print("dlt-viewer error")
            error = True
            break

    #    cmd = "rm " + x
    #   if os.system(cmd):
    #       print("rm error")
    #       error = True
    #       break

    if not error:
       os.system('rm -rf index')

a = dltDecoder(len(sys.argv), sys.argv)

if len(sys.argv) > 2:
    data = sys.argv[2].encode()
    if sys.argv[1] == "-d":
        print("Decoding....", data)
        print(a.decodeData(-5, data))
    elif sys.argv[1] == "-e":
        print(a.encode_data(5, data))
    else:
        a.printUsage()
elif len(sys.argv) > 1 and sys.argv[1] == "-c" :
    convertDlt2Txt()
else:
    a.decoding()
