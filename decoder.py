#!/usr/bin/env python
import sys
import os
import dltEnDecoder

def printUsage():
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
    if not error:
       os.system('rm -rf index')

dlt_decoder = dltEnDecoder.dltEnDecoder(len(sys.argv), sys.argv)

if len(sys.argv) > 2:
    data = sys.argv[2]
    if sys.argv[1] == "-d":
        print("Decoding....\n", data)
        print("\n\n")
        print(dlt_decoder.decode_data(-5, data))
    elif sys.argv[1] == "-e":
        print(dlt_decoder.encode_data(5, data))
    else:
        printUsage()
elif len(sys.argv) > 1 and sys.argv[1] == "-c" :
    convertDlt2Txt()
else:
    if not dlt_decoder.decode():
        printUsage()
