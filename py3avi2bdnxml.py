#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Description:
py3avi2bdnxml.py converts the imageTimings.srt produced by AVISubDetector 
to a BDN XML file that can be read by BDSup2Sub++.

[AVISubDetector URL]
[BDSup2Sub++URL]

The idea is to rip hardsubs into BD PGS (.sup) files.

Usage: 
python py3avi2bdnxml.py imageTimings.srt
python py3avi2bdnxml.py imageTimings.srt -q 480p
python py3avi2bdnxml.py imageTimings.srt -q 480p -o output.xml
python py3avi2bdnxml.py imageTimings.srt -q 480p --yOffset 4 -o output.xml

Current version: 0.2-alpha
Last Modified: 06Mar17
License: any

##stop reading now##

"""

#file input (srt) to (BDN-XML/PNG format)

#load libraries
import argparse               #used to add command line options
import os.path                  #test if file exists
import sys                         #end program on fail condition
import io                            #manipulate files (open/read/write/close)
from io import IOBase     #test if variable is a file object (an "IOBase" object)
from pathlib import Path  #override file in file system with another, experimental library
from PIL import Image     #Pillow image library for image resolution and manipulation
import pysrt                       #read input from subrip (.srt) files
import decimal                 #improved precision for arithmetic operations
from lxml import etree      #XML datastructure + I/O
import copy                       #to deepcopy() SRT object for fixing SRT file quirk

from decimal import ROUND_DOWN
#alias
num=decimal.Decimal

#set default options
defaultPixelOffset=2
defaultDialogueXOffset=0
defaultRomajiXOffset=0
defaultKanjiYOffset=0
defaultQuality='720p'
defaultOutputFilename='invalid'
defaultEncodingType='utf-8'
defaultFPS=num(24000/1001)
defaultDropFrameStatus='false'

#set static internal use variables
currentVersion='v0.2 - 06Mar17'
usageHelp='\n CorrectUsage: \n py3avi2bdnxml input.srt\n py3avi2bdnxml input.srt -o output.xml\n py3avi2bdnxml input.srt [-q 480p] [-yo 2] [-o output.xml]'

#add command line options
command_Line_parser=argparse.ArgumentParser(description='py3avi2bdnxml converts the imageTimings.srt produced by AVISubDetector \n to a BDN XML file that can be read by BDSup2Sub++.' + usageHelp)
command_Line_parser.add_argument("-df", "--dialogueFile", help="specify a dialogue file as input", type=str)
command_Line_parser.add_argument("-df2", "--dialogueFile2", help="specify an additional dialogue input file", type=str)
command_Line_parser.add_argument("-df3", "--dialogueFile3", help="specify an additional dialogue input file", type=str)
command_Line_parser.add_argument("-df4", "--dialogueFile4", help="specify an additional dialogue input file", type=str)
command_Line_parser.add_argument("-rf", "--romajiFile", help="specify a Romaji file as input", type=str)
command_Line_parser.add_argument("-rf2", "--romajiFile2", help="specify an additional Romaji input file", type=str)
command_Line_parser.add_argument("-rf3", "--romajiFile3", help="specify an additional Romaji input file", type=str)
command_Line_parser.add_argument("-rf4", "--romajiFile4", help="specify an additional Romaji input file", type=str)
command_Line_parser.add_argument("-kf", "--kanjiFile", help="specify a Kanji file as input", type=str)
command_Line_parser.add_argument("-kf2", "--kanjiFile2", help="specify an additional Kanji input file", type=str)
command_Line_parser.add_argument("-kf3", "--kanjiFile3", help="specify an additional Kanji input file", type=str)
command_Line_parser.add_argument("-kf4", "--kanjiFile4", help="specify an additional Kanji input file", type=str)

command_Line_parser.add_argument("-df-xo", "--dialogueFile-xOffset", help="specify an X offset for dialogue input, default={}".format(defaultDialogueXOffset),default=defaultDialogueXOffset,type=int)
command_Line_parser.add_argument("-df2-xo", "--dialogueFile2-xOffset", help="specify an X offset for dialogue input file 2, default={}".format(defaultDialogueXOffset),default=defaultDialogueXOffset,type=int)
command_Line_parser.add_argument("-df3-xo", "--dialogueFile3-xOffset", help="specify an X offset for dialogue input file 3, default={}".format(defaultDialogueXOffset),default=defaultDialogueXOffset,type=int)
command_Line_parser.add_argument("-df4-xo", "--dialogueFile4-xOffset", help="specify an X offset for dialogue input file 4, default={}".format(defaultDialogueXOffset),default=defaultDialogueXOffset,type=int)
command_Line_parser.add_argument("-df-yo", "--dialogueFile-yOffset", help="specify how far dialogue should be from bottom, >=2 and <=video.height, default={}".format(defaultPixelOffset),default=defaultPixelOffset,type=int)
command_Line_parser.add_argument("-df2-yo", "--dialogueFile2-yOffset", help="specify a Y offset for dialogue input file 2, default={}".format(defaultPixelOffset),default=defaultPixelOffset,type=int)
command_Line_parser.add_argument("-df3-yo", "--dialogueFile3-yOffset", help="specify a Y offset for dialogue input file 3, default={}".format(defaultPixelOffset),default=defaultPixelOffset,type=int)
command_Line_parser.add_argument("-df4-yo", "--dialogueFile4-yOffset", help="specify a Y offset for dialogue input file 4, default={}".format(defaultPixelOffset),default=defaultPixelOffset,type=int)
command_Line_parser.add_argument("-rf-xo", "--romajiFile-xOffset", help="specify an X offset for romaji input, default={}".format(defaultRomajiXOffset),default=defaultRomajiXOffset,type=int)
command_Line_parser.add_argument("-rf2-xo", "--romajiFile2-xOffset", help="specify an X offset for romaji input file 2, default={}".format(defaultRomajiXOffset),default=defaultRomajiXOffset,type=int)
command_Line_parser.add_argument("-rf3-xo", "--romajiFile3-xOffset", help="specify an X offset for romaji input file 3, default={}".format(defaultRomajiXOffset),default=defaultRomajiXOffset,type=int)
command_Line_parser.add_argument("-rf4-xo", "--romajiFile4-xOffset", help="specify an X offset for romaji input file 4, default={}".format(defaultRomajiXOffset),default=defaultRomajiXOffset,type=int)
command_Line_parser.add_argument("-rf-yo", "--romajiFile-yOffset", help="specify how far romaji should be from top, >=2 and <=video.height, default={}".format(defaultPixelOffset),default=defaultPixelOffset,type=int)
command_Line_parser.add_argument("-rf2-yo", "--romajiFile2-yOffset", help="specify a Y offset for romaji input file 2, default={}".format(defaultPixelOffset),default=defaultPixelOffset,type=int)
command_Line_parser.add_argument("-rf3-yo", "--romajiFile3-yOffset", help="specify a Y offset for romaji input file 3, default={}".format(defaultPixelOffset),default=defaultPixelOffset,type=int)
command_Line_parser.add_argument("-rf4-yo", "--romajiFile4-yOffset", help="specify a Y offset for romaji input file 4, default={}".format(defaultPixelOffset),default=defaultPixelOffset,type=int)
command_Line_parser.add_argument("-kf-xo", "--kanjiFile-xOffset", help="specify how far kanji should be from left or right, >=2 and <=video.width, default={}".format(defaultPixelOffset),default=defaultPixelOffset,type=int)
command_Line_parser.add_argument("-kf2-xo", "--kanjiFile2-xOffset", help="specify an X offset for kanji input file 2, default={}".format(defaultPixelOffset),default=defaultPixelOffset,type=int)
command_Line_parser.add_argument("-kf3-xo", "--kanjiFile3-xOffset", help="specify an X offset for kanji input file 3, default={}".format(defaultPixelOffset),default=defaultPixelOffset,type=int)
command_Line_parser.add_argument("-kf4-xo", "--kanjiFile4-xOffset", help="specify an X offset for kanji input file 4, default={}".format(defaultPixelOffset),default=defaultPixelOffset,type=int)
command_Line_parser.add_argument("-kf-yo", "--kanjiFile-yOffset", help="specify a Y offset for kanji input, default={}".format(defaultKanjiYOffset),default=defaultKanjiYOffset,type=int)
command_Line_parser.add_argument("-kf2-yo", "--kanjiFile2-yOffset", help="specify a Y offset for kanji input file 2, default={}".format(defaultKanjiYOffset),default=defaultKanjiYOffset,type=int)
command_Line_parser.add_argument("-kf3-yo", "--kanjiFile3-yOffset", help="specify a Y offset for kanji input file 3, default={}".format(defaultKanjiYOffset),default=defaultKanjiYOffset,type=int)
command_Line_parser.add_argument("-kf4-yo", "--kanjiFile4-yOffset", help="specify a Y offset for kanji input file 4, default={}".format(defaultKanjiYOffset),default=defaultKanjiYOffset,type=int)

command_Line_parser.add_argument("-q", "--quality", help="specify quality 480p/720p/1080p, default={}".format(defaultQuality),default=defaultQuality,type=str)
command_Line_parser.add_argument("-fps", "--framesPerSecond", help="specify conversion rate from SRT to BDN XML timecodes, default is 24000/1001",default=defaultFPS,type=str)
command_Line_parser.add_argument("-pl", "--preferLast", help="when resolving duplicate file entries for a subtitle, prefer the last one list, default=First", action="store_true")
command_Line_parser.add_argument("-ip", "--enableImageProcessing", help="vertically flip romaji images and rotate kanji ones clockwise, or counterclockwise", action="store_true")
command_Line_parser.add_argument("-kr", "--kanjiRight", help="alignment for Kanji should be on the Right , default=Left", action="store_true")
command_Line_parser.add_argument("-o", "--output", help="specify the output file name, default is to change to .xml",type=str)
command_Line_parser.add_argument("-e", "--encoding", help="specify encoding for input files, default={}".format(defaultEncodingType),default=defaultEncodingType,type=str)
command_Line_parser.add_argument("-d", "--debug", help="display calculated settings and other information",action="store_true")


#parse command line settings
command_Line_arguments=command_Line_parser.parse_args()

dialogueFileXOffset=command_Line_arguments.dialogueFile_xOffset
dialogueFile2XOffset=command_Line_arguments.dialogueFile2_xOffset
dialogueFile3XOffset=command_Line_arguments.dialogueFile3_xOffset
dialogueFile4XOffset=command_Line_arguments.dialogueFile4_xOffset
dialogueFileYOffset=command_Line_arguments.dialogueFile_yOffset
dialogueFile2YOffset=command_Line_arguments.dialogueFile2_yOffset
dialogueFile3YOffset=command_Line_arguments.dialogueFile3_yOffset
dialogueFile4YOffset=command_Line_arguments.dialogueFile4_yOffset

romajiFileXOffset=command_Line_arguments.romajiFile_xOffset
romajiFile2XOffset=command_Line_arguments.romajiFile2_xOffset
romajiFile3XOffset=command_Line_arguments.romajiFile3_xOffset
romajiFile4XOffset=command_Line_arguments.romajiFile4_xOffset
romajiFileYOffset=command_Line_arguments.romajiFile_yOffset
romajiFile2YOffset=command_Line_arguments.romajiFile2_yOffset
romajiFile3YOffset=command_Line_arguments.romajiFile3_yOffset
romajiFile4YOffset=command_Line_arguments.romajiFile4_yOffset

kanjiFileXOffset=command_Line_arguments.kanjiFile_xOffset
kanjiFile2XOffset=command_Line_arguments.kanjiFile2_xOffset
kanjiFile3XOffset=command_Line_arguments.kanjiFile3_xOffset
kanjiFile4XOffset=command_Line_arguments.kanjiFile4_xOffset
kanjiFileYOffset=command_Line_arguments.kanjiFile_yOffset
kanjiFile2YOffset=command_Line_arguments.kanjiFile2_yOffset
kanjiFile3YOffset=command_Line_arguments.kanjiFile3_yOffset
kanjiFile4YOffset=command_Line_arguments.kanjiFile4_yOffset

#check to make sure any dialogue.srt, romaji.srt, and kanji.srt files specified actually exist
if command_Line_arguments.dialogueFile == None:
    if command_Line_arguments.romajiFile == None:
        if command_Line_arguments.kanjiFile == None:
            sys.exit('\n Error: Please specify at least one input file. '+ usageHelp)

specifiedFiles=[]
#specifiedFiles[i]=[dialogueFilePath,typeOfInput,fileXOffset,fileYOffset]

if command_Line_arguments.dialogueFile != None:
    dialogueFilePath=command_Line_arguments.dialogueFile
    specifiedFiles.append([dialogueFilePath,'dialogue',dialogueFileXOffset,dialogueFileYOffset])
    if os.path.isfile(dialogueFilePath) != True:
        sys.exit('\n Error: Unable to find SRT file "' + dialogueFilePath + '"' + usageHelp)
if command_Line_arguments.dialogueFile2 != None:
    dialogueFile2Path=command_Line_arguments.dialogueFile2
    specifiedFiles.append([dialogueFile2Path,'dialogue',dialogueFile2XOffset,dialogueFile2YOffset])
    if os.path.isfile(dialogueFile2Path) != True:
        sys.exit('\n Error: Unable to find SRT file "' + dialogueFile2Path + '"' + usageHelp)
if command_Line_arguments.dialogueFile3 != None:
    dialogueFile3Path=command_Line_arguments.dialogueFile3
    specifiedFiles.append([dialogueFile3Path,'dialogue',dialogueFile3XOffset,dialogueFile3YOffset])
    if os.path.isfile(dialogueFile3Path) != True:
        sys.exit('\n Error: Unable to find SRT file "' + dialogueFile3Path + '"' + usageHelp)
if command_Line_arguments.dialogueFile4 != None:
    dialogueFile4Path=command_Line_arguments.dialogueFile4
    specifiedFiles.append([dialogueFile4Path,'dialogue',dialogueFile4XOffset,dialogueFile4YOffset])
    if os.path.isfile(dialogueFile4Path) != True:
        sys.exit('\n Error: Unable to find SRT file "' + dialogueFile4Path + '"' + usageHelp)

if command_Line_arguments.romajiFile != None:
    romajiFilePath=command_Line_arguments.romajiFile
    specifiedFiles.append([romajiFilePath,'romaji',romajiFileXOffset,romajiFileYOffset])
    if os.path.isfile(romajiFilePath) != True:
        sys.exit('\n Error: Unable to find SRT file "' + romajiFilePath + '"' + usageHelp)
if command_Line_arguments.romajiFile2 != None:
    romajiFile2Path=command_Line_arguments.romajiFile2
    specifiedFiles.append([romajiFile2Path,'romaji',romajiFile2XOffset,romajiFile2YOffset])
    if os.path.isfile(romajiFile2Path) != True:
        sys.exit('\n Error: Unable to find SRT file "' + romajiFile2Path + '"' + usageHelp)
if command_Line_arguments.romajiFile3 != None:
    romajiFile3Path=command_Line_arguments.romajiFile3
    specifiedFiles.append([romajiFile3Path,'romaji',romajiFile3XOffset,romajiFile3YOffset])
    if os.path.isfile(romajiFile3Path) != True:
        sys.exit('\n Error: Unable to find SRT file "' + romajiFile3Path + '"' + usageHelp)
if command_Line_arguments.romajiFile4 != None:
    romajiFile4Path=command_Line_arguments.romajiFile4
    specifiedFiles.append([romajiFile4Path,'romaji',romajiFile4XOffset,romajiFile4YOffset])
    if os.path.isfile(romajiFile4Path) != True:
        sys.exit('\n Error: Unable to find SRT file "' + romajiFile4Path + '"' + usageHelp)

if command_Line_arguments.kanjiFile != None:
    kanjiFilePath=command_Line_arguments.kanjiFile
    specifiedFiles.append([kanjiFilePath,'kanji',kanjiFileXOffset,kanjiFileYOffset])
    if os.path.isfile(kanjiFilePath) != True:
        sys.exit('\n Error: Unable to find SRT file "' + kanjiFilePath + '"' + usageHelp)
if command_Line_arguments.kanjiFile2 != None:
    kanjiFile2Path=command_Line_arguments.kanjiFile2
    specifiedFiles.append([kanjiFile2Path,'kanji',kanjiFile2XOffset,kanjiFile2YOffset])
    if os.path.isfile(kanjiFile2Path) != True:
        sys.exit('\n Error: Unable to find SRT file "' + kanjiFile2Path + '"' + usageHelp)
if command_Line_arguments.kanjiFile3 != None:
    kanjiFile3Path=command_Line_arguments.kanjiFile3
    specifiedFiles.append([kanjiFile3Path,'kanji',kanjiFile3XOffset,kanjiFile3YOffset])
    if os.path.isfile(kanjiFile3Path) != True:
        sys.exit('\n Error: Unable to find SRT file "' + kanjiFile3Path + '"' + usageHelp)
if command_Line_arguments.kanjiFile4 != None:
    kanjiFile4Path=command_Line_arguments.kanjiFile4
    specifiedFiles.append([kanjiFile4Path,'kanji',kanjiFile4XOffset,kanjiFile4YOffset])
    if os.path.isfile(kanjiFile4Path) != True:
        sys.exit('\n Error: Unable to find SRT file "' + kanjiFile4Path + '"' + usageHelp)

if len(specifiedFiles) == 0:
    sys.exit('\n Error: Please specify at least one input file. '+ usageHelp)

quality=command_Line_arguments.quality
fpsRate=encodingType=command_Line_arguments.framesPerSecond
preferLast=command_Line_arguments.preferLast
processImages=command_Line_arguments.enableImageProcessing
kanjiRight=command_Line_arguments.kanjiRight

if command_Line_arguments.output != None:
    outputFileName=command_Line_arguments.output
else:
    outputFileName=os.path.splitext(specifiedFiles[0][0])[0]+ ".xml"
    
encodingType=command_Line_arguments.encoding
debug=command_Line_arguments.debug
dropFrameStatus=defaultDropFrameStatus

if debug == True:
    #print("inputFileName="+inputFileName)
    print("quality="+str(quality))
    #print("yOffset="+str(yOffset))
    print("outputFileName="+outputFileName)
    print("fpsRate="+str(fpsRate))

#check quality
qualityValid=False
if quality == '480p':
    qualityValid=True
    videoWidth=848
    videoHeight=480
if quality == '480':
    quality='480p'
    qualityValid=True
    videoWidth=848
    videoHeight=480
if quality == '480p_43':
    quality='480p'
    qualityValid=True
    videoWidth=640
    videoHeight=480
if quality == '480_43':
    quality='480p'
    qualityValid=True
    videoWidth=640
    videoHeight=480

if quality == '720p':
    qualityValid=True
    videoWidth=1280
    videoHeight=720
if quality == '720':
    quality='720p'
    qualityValid=True
    videoWidth=1280
    videoHeight=720
if quality == '720p_43':
    quality='720p'
    qualityValid=True
    videoWidth=960
    videoHeight=720
if quality == '720_43':
    quality='720p'
    qualityValid=True
    videoWidth=960
    videoHeight=720

if quality == '1080p':
    qualityValid=True
    videoWidth=1920
    videoHeight=1080
if quality == '1080':
    quality='1080p'
    qualityValid=True
    videoWidth=1920
    videoHeight=1080
if quality == '1080p_43':
    quality='1080p'
    qualityValid=True
    videoWidth=1440
    videoHeight=1080
if quality == '1080_43':
    quality='1080p'
    qualityValid=True
    videoWidth=1440
    videoHeight=1080

if qualityValid!=True:
    sys.exit('\n Error: The following quality setting is invalid: "' + quality + '"' + usageHelp)

try: 
    fpsRate=num(fpsRate)
except decimal.InvalidOperation:  #occurs when converting string with / to decimal ('24000/1001'-> decimal)
    #print(sys.exc_info()[0])
    #print('pie')
    if '/' in fpsRate:
        #print(fpsRate.split(sep='/')[0])
        #print(fpsRate.split(sep='/')[0] + ' ' + fpsRate.split(sep='/')[1])
        fpsRate=num(fpsRate.split(sep='/')[0])/num(fpsRate.split(sep='/')[1])
    elif '\\' in fpsRate:
        fpsRate=num(fpsRate.split(sep='\\')[0])/num(fpsRate.split(sep='\\')[1])
#except ValueError: #occurs when converting string with / to float ('24000/1001'-> float)
#    print(fpsRate + 'raised a value error')

for i in range(len(specifiedFiles)):
    if specifiedFiles[i][1] == 'dialogue':
        #check yOffset
        # valid range is [2-1076] for a 2 pixel height image
        # invalid if (yOffset + imageHeight +2 >= videoHeight) #ends too high
        # invalid if (yOffset is < 2) #starts too low
        if specifiedFiles[i][3] < 2:
            sys.exit('\n Error: yOffset setting is out of [2,{}] range: "'.format(videoHeight-4) + str(specifiedFiles[i][3]) + '"' + usageHelp)
        if specifiedFiles[i][3] + 2 >= videoHeight:
            sys.exit('\n Error: yOffset setting is out of [2,{}] range: "'.format(videoHeight-4) + str(specifiedFiles[i][3]) + '"' + usageHelp)
    if specifiedFiles[i][1] == 'romaji':
        if specifiedFiles[i][3] < 2:
            sys.exit('\n Error: yOffset setting is out of [2,{}] range: "'.format(videoHeight-4) + str(specifiedFiles[i][3]) + '"' + usageHelp)
        if specifiedFiles[i][3] + 2 >= videoHeight:
            sys.exit('\n Error: yOffset setting is out of [2,{}] range: "'.format(videoHeight-4) + str(specifiedFiles[i][3]) + '"' + usageHelp)
    if specifiedFiles[i][1] == 'kanji':
        #for Kanji mode, check --xoffset
        #check xOffset
        # valid range is [2-1916] for a 2 pixel width image
        # invalid if (xOffset + imageWidth +2 >= videoHeight) #ends too far right
        # invalid if (xOffset is < 2) #starts too far leftif xOffset < 2:
        if specifiedFiles[i][2] < 2:
            sys.exit('\n Error: xOffset setting is out of [2,{}] range: "'.format(videoWidth-4) + str(specifiedFiles[i][2]) + '"' + usageHelp)
        if specifiedFiles[i][2]+2 >= videoWidth:
            sys.exit('\n Error: xOffset setting is out of [2,{}] range: "'.format(videoWidth-4) + str(specifiedFiles[i][2]) + '"' + usageHelp)

if debug == True:
    print("quality: "+str(quality))
    print("qualityValid: "+str(qualityValid))
    print("videoWidth: "+str(videoWidth))
    print("videoHeight: "+str(videoHeight))
    print("fpsRate after type conversion: "+str(fpsRate))

#read input files into SRT objects and fix AVISubDetector bug where last subtitle does not end promptly
#print('pie')
srtObjectsList = []
for i in range(len(specifiedFiles)):
    #global srtObjectsList
    #print('pie')
    #print(specifiedFiles[i][0])
    #print('pysrt.open(specifiedFiles[i][0], encoding=encodingType)' )
    srtObjectsList.append([pysrt.open(specifiedFiles[i][0], encoding=encodingType)])
    #print(srtObjectsList[i][0])
    #Re-time the last sub to end 3 seconds after it begins due to AVISubDetector quirk
    tempSrtFile=copy.deepcopy(srtObjectsList[i][0])
    #print(len(tempSrtFile))
    #print('Full: '+str(srtObjectsList[i][0][len(srtObjectsList[i][0])-1]))
    tempSrtFile[len(tempSrtFile)-1].shift(seconds=3)
    srtObjectsList[i][0][len(srtObjectsList[i][0])-1].end=tempSrtFile[len(tempSrtFile)-1].start
    #srtObjectsList[len(srtObjectsList)-1].start=tempLastSrtEntry
    #print('Full: '+str(tempSrtFile[len(srtObjectsList)-1]))  #print temporary object
    #print('Full: '+str(srtObjectsList[len(srtObjectsList)-1]))            #print main object
    #print(str(srtObjectsList))

#print(str(len(specifiedFiles)))
#print(str(specifiedFiles))
#print(str(len(srtObjectsList)))
#print(str(srtObjectsList))

if len(specifiedFiles) != len(srtObjectsList):
    sys.exit('\n Error: Unspecified')
 
#if romajiFileSpecified == True:
#    romajiSrtFile=pysrt.open(romajiFile, encoding=encodingType)
#    tempSrtFile=copy.deepcopy(romajiSrtFile)
#    tempSrtFile[len(tempSrtFile)-1].shift(seconds=3)
#    romajiSrtFile[len(romajiSrtFile)-1].end=tempSrtFile[len(tempSrtFile)-1].start

#if kanjiFileSpecified == True:
#    kanjiSrtFile = pysrt.open(kanjiFile, encoding=encodingType)
#    tempSrtFile=copy.deepcopy(kanjiSrtFile)
#    tempSrtFile[len(tempSrtFile)-1].shift(seconds=3)
#    kanjiSrtFile[len(kanjiSrtFile)-1].end=tempSrtFile[len(tempSrtFile)-1].start

#List full object contents + attributes
#for attr, value in srtObjectsList.__dict__.items():
#    print(attr, value)
#for attr, value in srtObjectsList[0].__dict__.items():
#    print(attr, value)
#for attr, value in srtObjectsList[0].text.__dict__.items(): #error
#for attr, value in srtObjectsList[0].start.__dict__.items():
#    print(attr, value)
#for attr, value in srtObjectsList[0].start.ordinal.__dict__.items(): #error

#List 1 by 1
#print('Length: ' + str(len(srtObjectsList)))
#print('Full: '+str(srtObjectsList[0]))
#print('Text: '+srtObjectsList[0].text)
#print('Start: '+str(srtObjectsList[0].start))
#print('Start Minutes: '+str(srtObjectsList[0].start.minutes))
#print('Start Seconds: '+str(srtObjectsList[0].start.seconds))
#print('End: '+str(srtObjectsList[0].end))
#print('End Hour: '+str(srtObjectsList[0].end.hours))
#print('End Minutes: '+str(srtObjectsList[0].end.minutes))
#print('End Seconds: '+str(srtObjectsList[0].end.seconds))

#getFractionalTime(srtObjectsList[0].start.ordinal)  #works
#getFractionalTime(srtObjectsList[0].start) #invalid

#add missing method, takes strobject.start.ordinal or strobject.end.ordinal
def getFractionalTime(x):
    return x % 1000

millisecondsPerHour=3600000
millisecondsPerMinute=60000
millisecondsPerSecond=1000

#takes hours, minutes, seconds and fractions and returns total number of
#miliseconds that amount of time represents (as a long).
def convertToTotalMilliseconds(hours1,minutes1,seconds1,real_milliseconds1):
    tHours=hours1*millisecondsPerHour
    tMinutes=minutes1*millisecondsPerMinute
    tSeconds=seconds1*millisecondsPerSecond
    return tHours+ tMinutes + tSeconds + real_milliseconds1

#takes real time in ms (as long) and converts to BD time that has been offset by fps
#format hh:mm:ss:ff     "ff" means number of frames derived from sub-second ms count relative to 24fps(?)
#This seems okay for 24 and 24000/1001 fps but does not seem accurate for other fps counts. Meh.
#TODO: figure out correct conversion for 25 and 29.976 fps.
def get_BDNXMLTime(funct_hours,funct_minutes,funct_seconds,real_milliseconds):
    totalMiliseconds=convertToTotalMilliseconds(funct_hours,funct_minutes,funct_seconds,real_milliseconds)
    #print(totalMiliseconds)
    baseFPS=24
    newFPS=fpsRate
    fpsMapping=baseFPS/newFPS    #this does not appear to be correct for non 24/23.976 fps counts
    #print(fpsMapping)
    BDXMLTotalMilliseconds=totalMiliseconds/fpsMapping
    #print(BDXMLTotalMilliseconds)
    BDXMLTotalHours=(BDXMLTotalMilliseconds/millisecondsPerHour).quantize(num('10'),rounding=ROUND_DOWN)
    #print(BDXMLTotalHours)
    BDXMLRemainingMiliseconds=BDXMLTotalMilliseconds-(BDXMLTotalHours*millisecondsPerHour)
    BDXMLTotalMinutes=(BDXMLRemainingMiliseconds/millisecondsPerMinute).quantize(num('10'),rounding=ROUND_DOWN)
    #print(BDXMLTotalMinutes)
    BDXMLRemainingMiliseconds=BDXMLRemainingMiliseconds-(BDXMLTotalMinutes*millisecondsPerMinute)
    BDXMLTotalSeconds=(BDXMLRemainingMiliseconds/millisecondsPerSecond).quantize(num('10'),rounding=ROUND_DOWN)
    #print(BDXMLTotalSeconds)
    BDXMLMilliseconds=(BDXMLRemainingMiliseconds-(BDXMLTotalSeconds*millisecondsPerSecond)).quantize(num('10'),rounding=ROUND_DOWN)
    #print(BDXMLMilliseconds)
    #So how many frames will pass in the amount of time specified by BDXMLMilliseconds per second?
    #Using newFPS gives wrong frame count apparently?
    BDXMLFinalFrames=((BDXMLMilliseconds*newFPS)/1000).quantize(num('10'),rounding=ROUND_DOWN)
    #print('Number of final frames: ' + str(BDXMLFinalFrames))
    #from https://stackoverflow.com/questions/17118071/python-add-leading-zeroes-using-str-format
    BDXMLTime='{0:0>2}'.format(str(BDXMLTotalHours))+':'+'{0:0>2}'.format(str(BDXMLTotalMinutes))+':'+'{0:0>2}'.format(str(BDXMLTotalSeconds))+':'+'{0:0>2}'.format(str(BDXMLFinalFrames))
    OriginalTime=str(funct_hours)+':'+str(funct_minutes)+':'+str(funct_seconds)+'.'+str(real_milliseconds)
    #print('OriginalTime: ' + OriginalTime)
    #print('BDXMLTime: ' + BDXMLTime)
    return [BDXMLTime,totalMiliseconds]

def get_graphicDimensions(image_path):
    return Image.open(image_path, mode='r').size

def rotateGraphic(image_path,counterclockwise):
    Image.open(image_path, mode='r').rotate(counterclockwise, expand=1).save(image_path)

#Image.Transpose(int) syntax, rotations are counterclockwise
#1 = FLIP_TOP_BOTTOM
#2 = ROTATE_90
#3 = ROTATE_180
#4 = ROTATE_270
#5 = FLIP_LEFT_RIGHT + ROTATE_90
#So transpose(5).transpose(4) = FLIP_LEFT_RIGHT
def flipVerticalGraphic(image_path):
    Image.open(image_path, mode='r').transpose(1).save(image_path)

#Todo: modify values with distortion ratio for better default placement in 3:4 video
#--centered width, formula: source_frame_width-image_width)/2 = the number of x pixels to offset the image
#same for both dialogue and and romaji
def get_XOffset(functGraphicWidth,fileXOffset):
    return int((videoWidth-functGraphicWidth)/2)+fileXOffset

#--dialogueYOffset, formula: source_frame_height-image_height-yOffset  = the number
def get_dialogueYOffset(functGraphicHeight,fileYOffset):
    return videoHeight-functGraphicHeight-fileYOffset

#--romajiYOffset, formula: return yoffset
def get_romajiYOffset(fileYOffset):
    return fileYOffset

#--kanjiXOffset, Calculate prior to fixing dimensions, so imageHeight is actually imageWidth
#check if -kr is enabled
def get_kanjiXOffset(graphicDimensions,fileXOffset):
    #graphicDimensions[0] = unprocessed width
    #graphicDimensions[1] = unprocessed height
    if kanjiRight != True:
        return fileXOffset
    elif kanjiRight == True:
        #full width - graphicWidth-offset
        return videoWidth-graphicDimensions[1]-fileXOffset

#--kanjiYOffset, Calculate prior to fixing dimensions, so imageWidth is actually imageHeight
#always centered along Y
def get_kanjiYOffset(graphicDimensions,fileYOffset):
    #graphicDimensions[0] = unprocessed width
    #graphicDimensions[1] = unprocessed height
    #(videoHeight-imageheight)/2
    return int((videoHeight-graphicDimensions[0])/2)+fileYOffset

#debug code
#myFilePath=r'C:\Users\User\Desktop\py3avi2bdnxml_workspace\media\Inuyasha\SubPic\[MogNAV][Karaoke_ED_07]Inu_Yasha_-_Amuro_Namie_-_Come[8D874604].orig.00000.bmp'
#dimensions=get_graphicDimensions(myFilePath)
#graphic_xdim=dimensions[0]
#graphic_ydim=dimensions[1]
#print('xoffset: '+str(get_XOffset(graphic_xdim)))
#print('yoffset: '+str(get_dialogueYOffset(graphic_ydim)))

#debug code
#get_BDNXMLTime(2,26,47,549)
#get_BDNXMLTime(0,0,45,337)
#get_BDNXMLTime(0,0,50,425)
#get_BDNXMLTime(0,0,55,97)
#get_BDNXMLTime(1,23,50,234)
#get_BDNXMLTime(1,24,8,710)


#random variable declarations
eventsList=[]
#eventsList[i]=[parsedFilename,totalMilliseconds,inTime,outTime,graphicWidth,graphicHeight,graphicXOffset,graphicYOffset]

#get 
#image width
#image height
#x offset
#y offset
#in time
    #convert to bdxml
#out time
    #convert to bdxml
#parsed filename
#add new Event below <events> tag
    #add Graphic tag with properties inside of event, text is parsed filename

#listOffset
def parseEvent(srtObject,typeOfInput,fileXOffset,fileYOffset,tempSrtImagePath='invalid'):
    #global srtObjectsList
    #srtObject=srtObject
    #global eventsList

    if tempSrtImagePath == 'invalid':
        srtImagePath=srtObject.text
    else:
        srtImagePath=tempSrtImagePath
    graphicDimensions=get_graphicDimensions(srtImagePath)
    #replace functSrtFile[i].text  with srtImagePath
    #print(srtImagePath)
    #return
    #srtObject=srtObject[listOffset]
    #print (str(srtObject))
    #return

    if typeOfInput == 'dialogue':
        graphicWidth=graphicDimensions[0]
        graphicHeight=graphicDimensions[1]
        graphicXOffset=get_XOffset(graphicWidth,fileXOffset)
        graphicYOffset=get_dialogueYOffset(graphicHeight,fileYOffset)
        #print('pie')
    if typeOfInput == 'romaji':
        graphicWidth=graphicDimensions[0]
        graphicHeight=graphicDimensions[1]
        graphicXOffset=get_XOffset(graphicWidth,fileXOffset)
        graphicYOffset=get_romajiYOffset(fileYOffset)
        if processImages == True:
            flipVerticalGraphic(srtImagePath)
    if typeOfInput == 'kanji':
        graphicWidth=graphicDimensions[1]  #processed Width
        graphicHeight=graphicDimensions[0]   #processed Height
        graphicXOffset=get_kanjiXOffset(graphicDimensions,fileXOffset)
        graphicYOffset=get_kanjiYOffset(graphicDimensions,fileYOffset)
        if processImages == True:
                if kanjiRight != True:
                    rotateGraphic(srtImagePath,270)
                elif kanjiRight == True:
                    rotateGraphic(srtImagePath,90)
    #print(srtObject)
    tempBDNXMLInTimeObject=get_BDNXMLTime(srtObject.start.hours,srtObject.start.minutes,srtObject.start.seconds,getFractionalTime(srtObject.start.ordinal))
    inTime=tempBDNXMLInTimeObject[0]
    totalMilliseconds=tempBDNXMLInTimeObject[1]
    tempBDNXMLOutTimeObject=get_BDNXMLTime(srtObject.end.hours,srtObject.end.minutes,srtObject.end.seconds,getFractionalTime(srtObject.end.ordinal))
    outTime=tempBDNXMLOutTimeObject[0]

    parsedFilename=os.path.basename(srtImagePath)
    
    #append event to event list
    #eventsList[i]=[parsedFilename,totalMilliseconds,inTime,outTime,graphicWidth,graphicHeight,graphicXOffset,graphicYOffset]
    eventsList.append([parsedFilename,totalMilliseconds,inTime,outTime,graphicWidth,graphicHeight,graphicXOffset,graphicYOffset])
    
    #tempEvent=etree.SubElement(events,'Event', Forced='False', InTC=inTime, OutTC=outTime)
    #tempGraphic=etree.SubElement(tempEvent,'Graphic', Width=str(graphicWidth), Height=str(graphicHeight), X=str(graphicXOffset), Y=str(graphicYOffset))
    #tempGraphic.text=parsedFilename
    #print('pie')
    
def addToEventList(functSrtFile,typeOfInput,fileXOffset,fileYOffset):
    for i in range(len(functSrtFile)):
        #print('Full: '+str(functSrtFile[i]))
        #print('Text: '+functSrtFile[i].text)
        #if file i/o check, file exists, then process the item, else skip it
        if os.path.isfile(str(functSrtFile[i].text)) == True:
            parseEvent(functSrtFile[i],typeOfInput,fileXOffset,fileYOffset)
        elif os.path.isfile(str(functSrtFile[i].text)) == False:
            #this can also fail on malformed paths, like where srt[23].text is actually 2 concatenated file paths linked with a \n
            #first take the string and determine if there are end line characters  in it
            #if so, then might be dealing with a joint one
                #then split the string into sub strings based upon each endline character
                #check the first and last entries to see if they are files
                #if the first is a file, but the second is not, include the second
                #if the second is a file, but the first is not, include the first
                #if neither is a file print error message
                #if both are files, then check with preferLast variable to see which to include
            if str(functSrtFile[i].text).count('\n') >= 1:
                srtSplitList=str(functSrtFile[i].text).split('\n')
                #print(srtSplitList[0])

                if os.path.isfile(srtSplitList[0]) == True:
                    firstSRTValid=True
                else:
                    firstSRTValid=False
                if os.path.isfile(srtSplitList[-1]) == True:
                    lastSRTValid=True
                else:
                    lastSRTValid=False

                if firstSRTValid == True:
                    if lastSRTValid == False:
                        #then include first one
                        parseEvent(functSrtFile[i], typeOfInput,fileXOffset,fileYOffset,srtSplitList[0])
                if firstSRTValid == False:
                    if lastSRTValid ==True:
                        #then include last one
                        parseEvent(functSrtFile[i], typeOfInput,fileXOffset,fileYOffset,srtSplitList[-1])
                if firstSRTValid == False:
                    if lastSRTValid == False:
                        print('"' + functSrtFile[i].text + '"'+ ' does not exist or is malformed, skipping')
                if firstSRTValid == True:
                    if lastSRTValid == True:
                        #then check with preferLast to see which to include
                        if preferLast != True:
                            #include first one
                            parseEvent(functSrtFile[i], typeOfInput,fileXOffset,fileYOffset,srtSplitList[0])
                        elif preferLast == True:
                            parseEvent(functSrtFile[i], typeOfInput,fileXOffset,fileYOffset,srtSplitList[-1])
                            #include last one
            else:
                print('"' + functSrtFile[i].text + '"'+ ' does not exist or is malformed, skipping')
    #subs.save('other/path.srt', encoding='utf-8')


#specifiedFiles[i]=[dialogueFilePath,typeOfInput,fileXOffset,fileYOffset]
for i in range(len(srtObjectsList)):
    addToEventList(srtObjectsList[i][0],specifiedFiles[i][1],specifiedFiles[i][2],specifiedFiles[i][3])

#lxml template
#from lxml import etree 
#to create
#html = etree.Element("html")
#add child elements, with reference available later
#body = etree.SubElement(html, "body")
#child2 = etree.SubElement(html, "child2")
#child3 = etree.SubElement(html, "child3")
#body.text = "TEXT"  invalid(?)
#paragraph= etree.SubElement(body,"p")
#paragraph.text="Hello"
#etree.tostring(html)  #string, can be written using regular IO library
#to write
#etree.ElementTree(etree.XML('<hi/>')).write('temp.xml',xml_declaration=True, encoding='UTF-8')
#or
#temp=etree.ElementTree(xmldoc)
#temp.write('output.xml',pretty_print=True,xml_declaration=True, encoding='UTF-8')

#bdnxml template
#<BDN Version="0.93" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
#xsi:noNamespaceSchemaLocation="BD-03-006-0093b BDN File Format.xsd">
#    <Description>
#        <Name Title="Undefined" Content=""/>
#        <Language Code="en"/>
#        <Format VideoFormat="480p" FrameRate="23.976" DropFrame="false"/>
#        <Events LastEventOutTC="00:01:36:21" FirstEventInTC="00:00:00:01"
#        ContentInTC="00:00:00:00" ContentOutTC="00:01:36:21" NumberofEvents="2270" Type="Graphic"/>
#    </Description>
#    <Events>
#        <Event Forced="False" InTC="00:00:00:01" OutTC="00:00:01:00">
#           <Graphic Width="620" Height="80" X="49" Y="398">00000000_0.compressed.png</Graphic>
#        </Event>
#        <Event Forced="False" InTC="00:00:01:00" OutTC="00:00:01:01">
#           <Graphic Width="620" Height="80" X="49" Y="398">00000024_0.compressed.png</Graphic>
#        </Event>

xmldoc = 0

def buildXML(eventsList):
    global xmldoc
    
    #from https://stackoverflow.com/questions/863183/python-adding-namespaces-in-lxml
    namespace='http://www.w3.org/2001/XMLSchema-instance'
    BDNfileformat='BD-03-006-0093b BDN File Format.xsd'
    location_attribute = '{%s}noNamespaceSchemaLocation' % namespace

    #eventsList[i]=[parsedFilename,totalMilliseconds,inTime,outTime,graphicWidth,graphicHeight,graphicXOffset,graphicYOffset]
    lowestBDNXMLinTimeObject=0
    highestBDNXMLinTimeObject=0

    #sort event list
    sortedEventsList=sorted(eventsList, key=lambda a: a[1])
    #save first and last events
    firstEventTime=sortedEventsList[0][2]
    lastEventTime=sortedEventsList[len(sortedEventsList)-1][2]

    #get total number of events
    numberOfEvents=len(sortedEventsList)

    #define object
    xmldoc = etree.Element('BDN', attrib={location_attribute: BDNfileformat}, Version='0.93')
    description = etree.SubElement(xmldoc,'Description')
    etree.SubElement(description, 'Name', Title='Undefined', Content='')
    etree.SubElement(description, 'Language',  Code='en')
    etree.SubElement(description, 'Format',  DropFrame=dropFrameStatus, VideoFormat=quality, FrameRate=str(fpsRate.quantize(num('.001'))))
    etree.SubElement(description, 'Events',  Type='Graphic', NumberofEvents=str(numberOfEvents), ContentOutTC=lastEventTime, ContentInTC='00:00:00:00', FirstEventInTC=firstEventTime, LastEventOutTC=lastEventTime)
    events = etree.SubElement(xmldoc,'Events')

    #loop through events and add to xml object
    #eventsList[i]=[parsedFilename,totalMilliseconds,inTime,outTime,graphicWidth,graphicHeight,graphicXOffset,graphicYOffset]
    for i in range(len(sortedEventsList)):
        tempEvent=etree.SubElement(events,'Event', Forced='False', InTC=sortedEventsList[i][2], OutTC=sortedEventsList[i][3])
        tempGraphic=etree.SubElement(tempEvent,'Graphic', Width=str(sortedEventsList[i][4]), Height=str(sortedEventsList[i][5]), X=str(sortedEventsList[i][6]), Y=str(sortedEventsList[i][7]))
        tempGraphic.text=sortedEventsList[i][0]
    
    #tempEvent=etree.SubElement(events,'Event', Forced='False', InTC=inTime, OutTC=outTime)
    #tempGraphic=etree.SubElement(tempEvent,'Graphic', Width=str(graphicWidth), Height=str(graphicHeight), X=str(graphicXOffset), Y=str(graphicYOffset))
    #tempGraphic.text=parsedFilename

    #debug code
    #print(etree.tostring(xmldoc,pretty_print=True))  #send to stdout


buildXML(eventsList)

#and finally writeout to filesystem
def writeOutput():
    temp=etree.ElementTree(xmldoc)
    try: 
        temp.write(outputFileName,pretty_print=True,xml_declaration=True, encoding='UTF-8')
        print('\n Wrote: ' + '"' + outputFileName + '"')
    except:
        print('Unspecified error: '+sys.exc_info()[0])

writeOutput()
