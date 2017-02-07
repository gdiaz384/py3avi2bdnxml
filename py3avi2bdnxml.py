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

Current version: 0.1-beta
Last Modified: 07Feb17
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
from PIL import Image     #Pillow image library for checking image resolutions
#import Image     #Pillow image library for checking image resolutions
import pysrt                       #read input from subrip (.srt) files
import decimal                 #improved precision for arithmetic operations
from lxml import etree      #XML datastructure + I/O
import copy                       #to deepcopy() SRT object for fixing SRT file quirk

from decimal import ROUND_DOWN
num=decimal.Decimal

#set default options
defaultPixelOffset=2
defaultQuality='720p'
defaultOutputFilename='invalid'
defaultEncodingType='utf-8'
defaultFPS=num(24000/1001)
defaultDropFrameStatus='false'

#set static internal use variables
currentVersion='v0.1 - 02Feb17'
usageHelp='\n CorrectUsage: \n py3avi2bdnxml input.srt\n py3avi2bdnxml input.srt -o output.xml\n py3avi2bdnxml input.srt [-q 480p] [-yo 2] [-o output.xml]'

#add command line options
command_Line_parser=argparse.ArgumentParser(description='Description: Replaces strings in text files using a replacement table.' + usageHelp)
command_Line_parser.add_argument("inputSRT", help="the text file to process",type=str)
command_Line_parser.add_argument("-q", "--quality", help="specify quality 480p/720p/1080p, default={}".format(defaultQuality),default=defaultQuality,type=str)
command_Line_parser.add_argument("-xo", "--xOffset", help="specify how far kanji should be from left and right, >=2 and <=video.width, default={}".format(defaultPixelOffset),default=defaultPixelOffset,type=int)
command_Line_parser.add_argument("-yo", "--yOffset", help="specify how far dialogue and romaji should be from bottom and top, >=2 and <=video.height, default={}".format(defaultPixelOffset),default=defaultPixelOffset,type=int)
command_Line_parser.add_argument("-fps", "--framesPerSecond", help="specify conversion rate from SRT to BDN XML timecodes, default is 24000/1001",default=defaultFPS,type=str)
command_Line_parser.add_argument("-e", "--srtEncoding", help="specify encoding for input files, default={}".format(defaultEncodingType),default=defaultEncodingType,type=str)
command_Line_parser.add_argument("-ok", "--onlyKanji", help="specify the only input file represents a line of vertical Kanji input", action="store_true")
command_Line_parser.add_argument("-or", "--onlyRomaji", help="specify the only input file represents Romaji input", action="store_true")
command_Line_parser.add_argument("-kf", "--kanjiFile", help="specify an additional Kanji input file", type=str)
command_Line_parser.add_argument("-rf", "--romajiFile", help="specify an additional Romaji input file", type=str)
command_Line_parser.add_argument("-kr", "--kanjiRight", help="alignment for Kanji should be on the Right , default=Left", action="store_true")
command_Line_parser.add_argument("-ip", "--enableImageProcessing", help="vertically flip romaji images and rotate kanji ones clockwise, or counterclockwise", action="store_true")
command_Line_parser.add_argument("-pl", "--preferLast", help="when resolving duplicate file entries for a subtitle, prefer the last one list, default=First", action="store_true")
command_Line_parser.add_argument("-d", "--debug", help="display calculated settings and other information",action="store_true")
command_Line_parser.add_argument("-o", "--output", help="specify the output file name, default is to change to .xml",type=str)

#parse command line settings
command_Line_arguments=command_Line_parser.parse_args()
inputFileName=command_Line_arguments.inputSRT
quality=command_Line_arguments.quality
xOffset=command_Line_arguments.xOffset
yOffset=command_Line_arguments.yOffset
fpsRate=encodingType=command_Line_arguments.framesPerSecond
encodingType=command_Line_arguments.srtEncoding
onlyKanji=command_Line_arguments.onlyKanji
onlyRomaji=command_Line_arguments.onlyRomaji
kanjiRight=command_Line_arguments.kanjiRight
processImages=command_Line_arguments.enableImageProcessing
debug=command_Line_arguments.debug
dropFrameStatus=defaultDropFrameStatus

if debug == True:
    print("inputFileName="+inputFileName)
    print("quality="+str(quality))
    print("yOffset="+str(yOffset))
    print("outputFileName="+outputFileName)
    print("fpsRate="+str(fpsRate))

#check to make sure input.srt actually exists
if os.path.isfile(inputFileName) != True:
    sys.exit('\n Error: Unable to find SRT file "' + inputFileName + '"' + usageHelp)

if command_Line_arguments.output != None:
    outputFileName=command_Line_arguments.output
else:
    outputFileName=os.path.splitext(inputFileName)[0]+ ".xml"

kanjiFileSpecified=False
if command_Line_arguments.kanjiFile != None:
    if os.path.isfile(kanjiFile) == True:
        kanjiFile=command_Line_arguments.kanjiFile
        kanjiFileSpecified=True

romajiFileSpecified=False
if command_Line_arguments.romajiFile != None:
    if os.path.isfile(romajiFile) == True:
        romajiFile=command_Line_arguments.romajiFile
        romajiFileSpecified=True

#subtle bug in case user includes both -kf and input file
if onlyRomaji == True:
    romajiFileSpecified=False

if onlyKanji == True:
    kanjiFileSpecified=False

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

#TODO: include rules for romaji and kanji -partial
#check yOffset
# valid range is [2-1076] for a 2 pixel height image
# invalid if (yOffset + imageHeight +2 >= videoHeight) #ends too high
# invalid if (yOffset is < 2) #starts too low
if yOffset < 2:
    sys.exit('\n Error: yOffset setting is out of [2,{}] range: "'.format(videoHeight-4) + str(yOffset) + '"' + usageHelp)
if yOffset + 2 >= videoHeight:
    sys.exit('\n Error: yOffset setting is out of [2,{}] range: "'.format(videoHeight-4) + str(yOffset) + '"' + usageHelp)

#for Kanji mode, check --xoffset
#check xOffset
# valid range is [2-1916] for a 2 pixel width image
# invalid if (xOffset + imageWidth +2 >= videoHeight) #ends too far right
# invalid if (xOffset is < 2) #starts too far left
if xOffset < 2:
    sys.exit('\n Error: xOffset setting is out of [2,{}] range: "'.format(videoWidth-4) + str(xOffset) + '"' + usageHelp)
if xOffset +2 >= videoWidth:
    sys.exit('\n Error: xOffset setting is out of [2,{}] range: "'.format(videoWidth-4) + str(xOffset) + '"' + usageHelp)

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


if debug == True:
    print("quality: "+str(quality))
    print("qualityValid: "+str(qualityValid))
    print("videoWidth: "+str(videoWidth))
    print("videoHeight: "+str(videoHeight))
    print("fpsRate after type conversion: "+str(fpsRate))

#read input
srtFile = pysrt.open(inputFileName, encoding=encodingType)
#TODO: AVISubDetector borks the ending time of the last srt entry, so fix it here. -done
#Re-time the last sub to end 3 seconds after it begins
tempSrtFile=copy.deepcopy(srtFile)
#print('Full: '+str(srtFile[len(srtFile)-1]))
tempSrtFile[len(tempSrtFile)-1].shift(seconds=3)
srtFile[len(srtFile)-1].end=tempSrtFile[len(tempSrtFile)-1].start
#srtFile[len(srtFile)-1].start=tempLastSrtEntry
#print('Full: '+str(tempSrtFile[len(srtFile)-1]))  #print temporary object
#print('Full: '+str(srtFile[len(srtFile)-1]))            #print main object

if romajiFileSpecified == True:
    romajiSrtFile=pysrt.open(romajiFile, encoding=encodingType)
    tempSrtFile=copy.deepcopy(romajiSrtFile)
    tempSrtFile[len(tempSrtFile)-1].shift(seconds=3)
    romajiSrtFile[len(romajiSrtFile)-1].end=tempSrtFile[len(tempSrtFile)-1].start
    
if kanjiFileSpecified == True:
    kanjiSrtFile = pysrt.open(kanjiFile, encoding=encodingType)
    tempSrtFile=copy.deepcopy(kanjiSrtFile)
    tempSrtFile[len(tempSrtFile)-1].shift(seconds=3)
    kanjiSrtFile[len(kanjiSrtFile)-1].end=tempSrtFile[len(tempSrtFile)-1].start

#List full object contents + attributes
#for attr, value in srtFile.__dict__.items():
#    print(attr, value)
#for attr, value in srtFile[0].__dict__.items():
#    print(attr, value)
#for attr, value in srtFile[0].text.__dict__.items(): #error
#for attr, value in srtFile[0].start.__dict__.items():
#    print(attr, value)
#for attr, value in srtFile[0].start.ordinal.__dict__.items(): #error

#List 1 by 1
#print('Length: ' + str(len(srtFile)))
#print('Full: '+str(srtFile[0]))
#print('Text: '+srtFile[0].text)
#print('Start: '+str(srtFile[0].start))
#print('Start Minutes: '+str(srtFile[0].start.minutes))
#print('Start Seconds: '+str(srtFile[0].start.seconds))
#print('End: '+str(srtFile[0].end))
#print('End Hour: '+str(srtFile[0].end.hours))
#print('End Minutes: '+str(srtFile[0].end.minutes))
#print('End Seconds: '+str(srtFile[0].end.seconds))

#returnFractionalTime(srtFile[0].start.ordinal)  #works
#returnFractionalTime(srtFile[0].start) #invalid

#add missing method, takes strobject.start.ordinal or strobject.end.ordinal
def returnFractionalTime(x):
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
    fpsMapping=baseFPS/newFPS    #this does not appear to be correct for non 24 fps counts
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

#--centered width, formula: source_frame_width-image_width)/2 = the number of x pixels to offset the image
#same for both dialogue and and romaji
def get_XOffset(functGraphicWidth):
    return int((videoWidth-functGraphicWidth)/2)

#--dialogueYOffset, formula: source_frame_height-image_height-yOffset  = the number
def get_dialogueYOffset(functGraphicHeight):
    return videoHeight-functGraphicHeight-yOffset 

#--romajiYOffset, formula: return yoffset
def get_romajiYOffset():
    return yOffset

#--kanjiXOffset, Calculate prior to fixing dimensions, so imageHeight is actually imageWidth
#check if -kr is enabled
def get_kanjiXOffset(graphicDimensions):
    #graphicDimensions[0] = unprocessed width
    #graphicDimensions[1] = unprocessed height
    if kanjiRight != True:
        return xOffset
    elif kanjiRight == True:
        #full width - graphicWidth-offset
        return  videoWidth-graphicDimensions[1]-xOffset

#--kanjiYOffset, Calculate prior to fixing dimensions, so imageWidth is actually imageHeight
#always centered along Y
def get_kanjiYOffset(graphicDimensions):
    #graphicDimensions[0] = unprocessed width
    #graphicDimensions[1] = unprocessed height
    #(videoHeight-imageheight)/2
    return int((videoHeight-graphicDimensions[0])/2)

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

#from https://stackoverflow.com/questions/863183/python-adding-namespaces-in-lxml
namespace='http://www.w3.org/2001/XMLSchema-instance'
BDNfileformat='BD-03-006-0093b BDN File Format.xsd'
location_attribute = '{%s}noNamespaceSchemaLocation' % namespace

#define object
xmldoc = etree.Element('BDN', attrib={location_attribute: BDNfileformat}, Version='0.93')
description = etree.SubElement(xmldoc,'Description')
etree.SubElement(description, 'Name', Title='Undefined', Content='')
etree.SubElement(description, 'Language',  Code='en')
etree.SubElement(description, 'Format',  DropFrame=dropFrameStatus, VideoFormat=quality, FrameRate=str(fpsRate.quantize(num('.001'))))
#etree.SubElement(description, 'Events',  Type='Graphic', NumberofEvents=numberOfEventsCounter, ContentOutTC=lastEventTime, ContentInTC='00:00:00:00', FirstEventInTC=firstEventTime, LastEventOutTC=lastEventTime)
#description_events not written here because requires information not yet known
events = etree.SubElement(xmldoc,'Events')

#random variable declarations
numberOfEventsCounter=0
lowestBDNXMLinTimeObject=0
highestBDNXMLinTimeObject=0

#try to add to xml
#if only dialogue, add as dialogue, write out, quit
#if only romaji, add as romaji, write out, quit
#if only kanji, add as kani, write out, quit
#if combined...

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
#add new Event below "events" tag
    #add Graphic tag with properties inside of event, text is parsed filename
def addToBDNXML(functSrtFile,typeOfInput):
    for i in range(len(functSrtFile)):
        global numberOfEventsCounter
        global highestBDNXMLinTimeObject
        global lowestBDNXMLinTimeObject
        #print('Full: '+str(functSrtFile[i]))
        #print('Text: '+functSrtFile[i].text)
        #if file i/o check, file exists, then process the item, else skip it
        if os.path.isfile(str(functSrtFile[i].text)) == True:
            numberOfEventsCounter+=1
            graphicDimensions=get_graphicDimensions(functSrtFile[i].text)

            if typeOfInput == 'dialogue':
                graphicWidth=graphicDimensions[0]
                graphicHeight=graphicDimensions[1]
                graphicXOffset=get_XOffset(graphicWidth)
                graphicYOffset=get_dialogueYOffset(graphicHeight)
                #print('pie')
            if typeOfInput == 'romaji':
                graphicWidth=graphicDimensions[0]
                graphicHeight=graphicDimensions[1]
                graphicXOffset=get_XOffset(graphicWidth)
                graphicYOffset=get_romajiYOffset()
                if processImages == True:
                    flipVerticalGraphic(functSrtFile[i].text)
            if typeOfInput == 'kanji':
                graphicWidth=graphicDimensions[1]  #proc essed Width
                graphicHeight=graphicDimensions[0]   #processed Height
                graphicXOffset=get_kanjiXOffset(graphicDimensions)
                graphicYOffset=get_kanjiYOffset(graphicDimensions)
                if processImages == True:
                        if kanjiRight != True:
                            rotateGraphic(functSrtFile[i].text,270)
                        elif kanjiRight == True:
                            rotateGraphic(functSrtFile[i].text,90)

            tempBDNXMLInTimeObject=get_BDNXMLTime(functSrtFile[i].start.hours,functSrtFile[i].start.minutes,functSrtFile[i].start.seconds,returnFractionalTime(functSrtFile[i].start.ordinal))
            inTime=tempBDNXMLInTimeObject[0]
            tempBDNXMLOutTimeObject=get_BDNXMLTime(functSrtFile[i].end.hours,functSrtFile[i].end.minutes,functSrtFile[i].end.seconds,returnFractionalTime(functSrtFile[i].end.ordinal))
            outTime=tempBDNXMLOutTimeObject[0]

            if lowestBDNXMLinTimeObject == 0:
                lowestBDNXMLinTimeObject=tempBDNXMLInTimeObject
                highestBDNXMLinTimeObject=tempBDNXMLOutTimeObject
                #print('pie')
            if tempBDNXMLInTimeObject[1] < lowestBDNXMLinTimeObject[1]:
                lowestBDNXMLinTimeObject=tempBDNXMLInTimeObject
            if tempBDNXMLOutTimeObject[1] > highestBDNXMLinTimeObject[1]:
                highestBDNXMLinTimeObject=tempBDNXMLOutTimeObject

            parsedFilename=os.path.basename(functSrtFile[i].text)
            tempEvent=etree.SubElement(events,'Event', Forced='False', InTC=inTime, OutTC=outTime)
            tempGraphic=etree.SubElement(tempEvent,'Graphic', Width=str(graphicWidth), Height=str(graphicHeight), X=str(graphicXOffset), Y=str(graphicYOffset))
            tempGraphic.text=parsedFilename

        elif os.path.isfile(str(functSrtFile[i].text)) == False:
            #this can also fail on malformed paths, like where srt[23].text is actually 2 concatenated file paths linked with a \n
            #TODO: make this code more flexible to account for above scenario
            print('"' + functSrtFile[i].text + '"'+ ' does not exist or is malformed, skipping')

#if only dialogue, add as dialogue, write out, quit
#if kanjiFileSpecified != True:
#    if romajiFileSpecified != True:
if onlyRomaji !=True:
    if onlyKanji != True:
        addToBDNXML(srtFile, 'dialogue')

#if only romaji, add as romaji, write out, quit
if onlyRomaji == True:
    addToBDNXML(srtFile, 'romaji')

#if only kanji, add as kanji, write out, quit
if onlyKanji == True:
    addToBDNXML(srtFile, 'kanji')

# dialogue + romaji    
if kanjiFileSpecified != True:
    if romajiFileSpecified == True:
        addToBDNXML(srtFile, 'dialogue')
        addToBDNXML(romajiSrtFile, 'romaji')

# dialogue + kanji
if kanjiFileSpecified == True:
    if romajiFileSpecified != True:
        addToBDNXML(srtFile, 'dialogue')
        addToBDNXML(kanjiSrtFile, 'kanji')

# dialogue + romaji + kanji
if kanjiFileSpecified == True:
    if romajiFileSpecified == True:
        addToBDNXML(srtFile, 'dialogue')
        addToBDNXML(romajiSrtFile, 'romaji')
        addToBDNXML(kanjiSrtFile, 'kanji')

# kanji + romaji   #not a supported operation due to requiring input.srt, (interface issue)

firstEventTime=lowestBDNXMLinTimeObject[0]
lastEventTime=highestBDNXMLinTimeObject[0]

#print('Total Events: ' + str(numberOfEventsCounter))

#write last event
etree.SubElement(description, 'Events',  Type='Graphic', NumberofEvents=str(numberOfEventsCounter), ContentOutTC=lastEventTime, ContentInTC='00:00:00:00', FirstEventInTC=firstEventTime, LastEventOutTC=lastEventTime)

#debug code
#print(etree.tostring(xmldoc,pretty_print=True))  #send to stdout

#and finally writeout to filesystem
def writeOutput():
    temp=etree.ElementTree(xmldoc)
    try: 
        temp.write(outputFileName,pretty_print=True,xml_declaration=True, encoding='UTF-8')
        print('\n Wrote: ' + '"' + outputFileName + '"')
    except:
        print('Unspecified error: '+sys.exc_info()[0])

writeOutput()
