#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import argparse                #used to add command line options
import os.path                   #test if file exists
import sys                          #end program on fail condition
import io                            #manipulate files (open/read/write/close)
from io import IOBase     #test if variable is a file object (an "IOBase" object)
from pathlib import Path  #override file in file system with another, experimental library

#set default options
defaultEncodingType='utf-8'
defaultConsoleEncodingType='utf-8'
defaultReplacementListEncodingType='utf-8'

#set static internal use variables
currentVersion='v0.1 - 02Feb17'
usageHelp='\n Todo: put usage help here'

#add command line options
command_Line_parser=argparse.ArgumentParser(description='Description: Replaces strings in text files using a replacement table.' + usageHelp)
command_Line_parser.add_argument("inputFile", help="the text file to process",type=str)
command_Line_parser.add_argument("replacementList", help="the text file with match pairs",type=str)
command_Line_parser.add_argument("-o", "--output", help="specify the output file name, default is to append '.mod.txt'")
command_Line_parser.add_argument("-nc", "--noCopy", help="modify the existing file instead of creating a copy, default=create a copy, Takes precedence over -o",action="store_true")
command_Line_parser.add_argument("-sm", "--showMatching", help="show matches in stdout and exit",action="store_true")
command_Line_parser.add_argument("-d", "--debug", help="show generated replacementTable and exit",action="store_true")
command_Line_parser.add_argument("-e", "--encoding", help="specify input/output file encoding, default=utf-8",default=defaultEncodingType,type=str)
command_Line_parser.add_argument("-ce", "--consoleEncoding", help="specify encoding for stdout, default=utf-8",default=defaultConsoleEncodingType,type=str)
command_Line_parser.add_argument("-rle", "--replacementListEncoding", help="specify encoding for the replacementList.txt, default=utf-8",default=defaultReplacementListEncodingType,type=str)

#parse command line settings
command_Line_arguments=command_Line_parser.parse_args()
inputFileName=command_Line_arguments.inputFile
replaceListName=command_Line_arguments.replacementList
noCopy=command_Line_arguments.noCopy
showMatching=command_Line_arguments.showMatching
debug=command_Line_arguments.debug
encodingType=command_Line_arguments.encoding
consoleEncodingType=command_Line_arguments.consoleEncoding
replacementListEncodingType=command_Line_arguments.replacementListEncoding

if command_Line_arguments.output != None:
    outputFileName=command_Line_arguments.output
else:
    outputFileName=inputFileName+".mod.txt"

#debug code
#print("inputFileName="+inputFileName)
#print("replaceListName="+replaceListName)
#print("outputFileName="+outputFileName)
#print("noCopy="+str(noCopy))
#print("showMatching="+str(showMatching))
#print("debug="+str(debug))

#check to make sure inputFile.txt and replacementList.txt actually exist
if os.path.isfile(inputFileName) != True:
    sys.exit('\n Error: Unable to find input file "' + inputFileName + '"' + usageHelp)
if os.path.isfile(replaceListName) != True:
    sys.exit('\n Error. Unable to find replacement list "' + replaceListName + '"' + usageHelp)


#read replacement list
replaceListFile=open(replaceListName,'r',encoding=replacementListEncodingType)
replacementTable=dict({})

