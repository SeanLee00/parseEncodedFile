#!/usr/bin/env python

import sys
import os
import base64

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
        
    def __makeNumberTable():
        __numberMap[0] = 'Z'
        __numberMap[1] = 'A'
        __numberMap[2] = '%'
        __numberMap[3] = 'Q'
        __numberMap[4] = 'S'
        __numberMap[5] = '#'
        __numberMap[6] = 'R'
        __numberMap[7] = 'E'
        __numberMap[8] = '^'
        __numberMap[9] = '&'

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

    def decodeData(self, shift, encoded_data):
        decoded_data = b""
        try:
            pos = len(encoded_data) - shift
            a = encoded_data[pos:]
            b = encoded_data[:pos]        
            decoded_data = base64.b64decode(a+b)
        except Exception as e:
            print("Error!\nDeconding error on [", encoded_data, "] : ", str(e))
        
        finally:
            return decoded_data

    def encodeData(self, shift, data):
        encoded_data = b""
        try:
            encoded_data = base64.b64encode(data)
        except Exception as e:
            print("encoding error in ", data, ", ", str(e))
        else:
            a = encoded_data[:shift]
            b = encoded_data[shift:]
            encoded_data = b + a
        finally:
            return encoded_data

    def __isNumber(self, data):
        len = len(data)
        for num in data:
            for a in range(0,9):
                print(a)
        return true

    def __decodingAndWrite(self, line, file):
        index1 = line.find(self.__s_str)
        index2 = line.find(self.__e_str)
        if index1 != -1 and index2 != -1:
            # print(line)
            s_pos = line.find(self.__s_str) + len(self.__s_str)
            e_pos = line.find(self.__e_str)
            encoded_data = line[s_pos:e_pos]
            c = line
            try:
                decoded_dtat = self.decodeData(self.__shift, encoded_data)
                a = line[:s_pos - len(self.__s_str)]
                b = line[e_pos + len(self.__e_str):]
                c = a + decoded_dtat + b
            except Exception as e:
                print(str(e))
            finally:
                file.write(c)
        else:
            file.write(line)

    def __doDecording(self,file_path):
        try:
            file = open(file_path, "rb")
            newFile = self.__createDecodedFile(file_path)
            for line in file:
                self.__decodingAndWrite(line, newFile)
        except Exception as e:
            print(str(e))
        finally:
            print("file closed")
            file.close()
            newFile.close()
        
    def __run(self):
        if self.__argc < 2:
            self.printUsage()
            return
        self.dir = self.__argv[1]
        try:
            file_list = self.getFileList(self.dir)
            for file_path in file_list:
                self.__doDecording(file_path)
        except Exception as e:
            print(str(e))

    def decoding(self):
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
        print("\t\t", sys.argv[0],  " -c  test.dlt")

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
        print("Encoding....", data)
        print(a.decodeData(5, data))
    elif sys.argv[1] == "-e":
        print(a.encodeData(5, data))
    else:
        a.printUsage()
elif len(sys.argv) > 1 and sys.argv[1] == "-c" :
    convertDlt2Txt()
else:
    a.decoding()
