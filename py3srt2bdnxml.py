#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Description:
py3srt2bdnxml.py converts the imageTimings.srt produced by AVISubDetector 
to a BDN XML file that can be read by BDSup2Sub++.

[AVISubDetector URL]
[BDSup2Sub++URL]

The idea is to rip hardsubs into BD PGS (.sup) files.

Usage: 
python py3srt2bdnxml.py imageTimings.srt
python py3srt2bdnxml.py imageTimings.srt -q 480p
python py3srt2bdnxml.py imageTimings.srt -q 480p -pfb 2 -o output.xml
python py3srt2bdnxml.py imageTimings.srt -q 480p -o output.xml

Current version: 0.1
Last Modified: 02Feb17
License: any, 

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
import pysrt                       #read input from subrip (.srt) files
import decimal                 #improved precision for arithmetic operations
from lxml import etree      #XML datastructure + I/O

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
usageHelp='\n CorrectUsage: \n py3srt2bdnxml input.srt\n py3srt2bdnxml input.srt -o output.xml\n py3srt2bdnxml input.srt -q 480p -pfb 2 -o output.xml'

#add command line options
command_Line_parser=argparse.ArgumentParser(description='Description: Replaces strings in text files using a replacement table.' + usageHelp)
command_Line_parser.add_argument("inputSRT", help="the text file to process",type=str)
command_Line_parser.add_argument("-q", "--quality", help="specify quality 480p/720p/1080p, default={}".format(defaultQuality),default=defaultQuality,type=str)
command_Line_parser.add_argument("-pfb", "--pixelsFromBottom", help="specify how far subs should be from bottom, >=1 and <=video.height, default={}".format(defaultPixelOffset),default=defaultPixelOffset,type=int)
command_Line_parser.add_argument("-fps", "--framesPerSecond", help="specify conversion rate from SRT to BDN XML timecodes, default is 24000/1001",default=defaultFPS,type=str)
command_Line_parser.add_argument("-e", "--srtEncoding", help="specify input file encoding, default={}".format(defaultEncodingType),default=defaultEncodingType,type=str)
command_Line_parser.add_argument("-o", "--output", help="specify the output file name, default is to append .xml")

#parse command line settings
command_Line_arguments=command_Line_parser.parse_args()
inputFileName=command_Line_arguments.inputSRT
quality=command_Line_arguments.quality
pixelsFromBottom=command_Line_arguments.pixelsFromBottom
fpsRate=encodingType=command_Line_arguments.framesPerSecond
encodingType=command_Line_arguments.srtEncoding
dropFrameStatus=defaultDropFrameStatus

if command_Line_arguments.output != None:
    outputFileName=command_Line_arguments.output
else:
    outputFileName=inputFileName + ".xml"   #TODO: rename the srt to .xml not just append an extension

#debug code  TODO: print out some settings, and also support a -debug switch
#print("inputFileName="+inputFileName)
#print("quality="+str(quality))
#print("pixelsFromBottom="+str(pixelsFromBottom))
#print("outputFileName="+outputFileName)
#print("fpsRate="+str(fpsRate))
#check to make sure input is valid
#check input
#check to make sure input.srt actually exists
if os.path.isfile(inputFileName) != True:
    sys.exit('\n Error: Unable to find SRT file "' + inputFileName + '"' + usageHelp)

#TODO: add 4:3 options (quality_43) -humm...
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

if quality == '720p':
    qualityValid=True
    videoWidth=1280
    videoHeight=720
if quality == '720':
    quality='720p'
    qualityValid=True
    videoWidth=1280
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

if qualityValid!=True:
    sys.exit('\n Error: The following quality setting is invalid: "' + quality + '"' + usageHelp)

#TODO: update to 2 pixels from bottom minumum
#check pixelsFromBottom
#1080 - 1080 + 1080 > 1080-1 
# valid range is 2-1076
# invalid if (pixels from bottom + imageHeight > videoHeight) #ends too high
# invalid if (pixels from Bottom is or <1) #starts too low
if pixelsFromBottom < 1:
    sys.exit('\n Error: pixelsFromBottom setting is out of [1,{}] range: "'.format(videoHeight-3) + str(pixelsFromBottom) + '"' + usageHelp)
if pixelsFromBottom + 2 >= videoHeight:
    sys.exit('\n Error: pixelsFromBottom setting is out of [1,{}] range: "'.format(videoHeight-3) + str(pixelsFromBottom) + '"' + usageHelp)

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


#debug code
#print("quality="+str(quality))
#print("qualityValid="+str(qualityValid))
#print("videoWidth="+str(videoWidth))
#print("videoHeight="+str(videoHeight))
#print("fpsRate after type conversion="+str(fpsRate))

#read input
srtFile = pysrt.open(inputFileName, encoding=encodingType)
#TODO: AVISubDetector borks the ending of the last srt entry, so fix it here.

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
#This seems okay for 24 and 24000/1001 fps but does not seem accurate for other fps counts. meh
#TODO: figure out correct conversion for 25 and 29.976 fps.
def get_BDNXMLTime(funct_hours,funct_minutes,funct_seconds,real_milliseconds):
    totalMiliseconds=convertToTotalMilliseconds(funct_hours,funct_minutes,funct_seconds,real_milliseconds)
    #print(totalMiliseconds)
    baseFPS=24
    newFPS=fpsRate
    fpsMapping=baseFPS/newFPS
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
    BDXMLFinalFrames=((BDXMLMilliseconds*baseFPS)/1000).quantize(num('10'),rounding=ROUND_DOWN)
    #print('Number of final frames: ' + str(BDXMLFinalFrames))
    #from https://stackoverflow.com/questions/17118071/python-add-leading-zeroes-using-str-format
    BDXMLTime='{0:0>2}'.format(str(BDXMLTotalHours))+':'+'{0:0>2}'.format(str(BDXMLTotalMinutes))+':'+'{0:0>2}'.format(str(BDXMLTotalSeconds))+':'+'{0:0>2}'.format(str(BDXMLFinalFrames))
    OriginalTime=str(funct_hours)+':'+str(funct_minutes)+':'+str(funct_seconds)+'.'+str(real_milliseconds)
    #print('OriginalTime: ' + OriginalTime)
    #print('BDXMLTime: ' + BDXMLTime)
    return [BDXMLTime,totalMiliseconds]

def get_graphicDimensions(image_path):
    return Image.open(image_path, mode='r').size

#--centered width  (formula: (source_frame_width-image_width)/2 = the number of x pixels to offset the image)
def get_xoffset(functGraphicWidth):
    return int((videoWidth-functGraphicWidth)/2)

#--y offset (formula: source_frame_height-image_height-number_of_pixels_from_bottom = the number
def get_yoffset(functGraphicHeight):
    return videoHeight-functGraphicHeight-pixelsFromBottom 

myFilePath=r'C:\Users\User\Desktop\py3srt2bdnxml_workspace\media\Inuyasha\SubPic\[MogNAV][Karaoke_ED_07]Inu_Yasha_-_Amuro_Namie_-_Come[8D874604].orig.00000.bmp'
dimensions=get_graphicDimensions(myFilePath)
graphic_xdim=dimensions[0]
graphic_ydim=dimensions[1]
#print('xoffset: '+str(get_xoffset(graphic_xdim)))
#print('yoffset: '+str(get_yoffset(graphic_ydim)))

#get_BDNXMLTime(2,26,47,549)
#get_BDNXMLTime(0,0,45,337)
#get_BDNXMLTime(0,0,50,425)
#get_BDNXMLTime(0,0,55,97)
#get_BDNXMLTime(1,23,50,234)
#get_BDNXMLTime(1,24,8,710)

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

numberOfEventsCounter=0

global lowestBDNXMLinTimeObject
global highestBDNXMLinTimeObject

for i in range(len(srtFile)):
    #print('Full: '+str(srtFile[i]))
    #print('Text: '+srtFile[i].text)
    #if file i/o check, file exists, then process the item, else skip it
    if os.path.isfile(str(srtFile[i].text)) == True:
        numberOfEventsCounter+=1
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
        graphicDimensions=get_graphicDimensions(srtFile[i].text)
        graphicWidth=graphicDimensions[0]
        graphicHeight=graphicDimensions[1]
        xOffset=get_xoffset(graphicWidth)
        yOffset=get_yoffset(graphicHeight)
        tempBDNXMLInTimeObject=get_BDNXMLTime(srtFile[i].start.hours,srtFile[i].start.minutes,srtFile[i].start.seconds,returnFractionalTime(srtFile[i].start.ordinal))
        inTime=tempBDNXMLInTimeObject[0]
        tempBDNXMLOutTimeObject=get_BDNXMLTime(srtFile[i].end.hours,srtFile[i].end.minutes,srtFile[i].end.seconds,returnFractionalTime(srtFile[i].end.ordinal))
        outTime=tempBDNXMLOutTimeObject[0]
        if i == 0:
            lowestBDNXMLinTimeObject=tempBDNXMLInTimeObject
            highestBDNXMLinTimeObject=tempBDNXMLOutTimeObject
            #print('pie')
        if tempBDNXMLInTimeObject[1] < lowestBDNXMLinTimeObject[1]:
            lowestBDNXMLinTimeObject=tempBDNXMLInTimeObject
        if tempBDNXMLOutTimeObject[1] > highestBDNXMLinTimeObject[1]:
            highestBDNXMLinTimeObject=tempBDNXMLOutTimeObject
        parsedFilename=os.path.basename(srtFile[i].text)
        tempEvent=etree.SubElement(events,'Event', Forced='False', InTC=inTime, OutTC=outTime)
        tempGraphic=etree.SubElement(tempEvent,'Graphic', Width=str(graphicWidth), Height=str(graphicHeight), X=str(xOffset), Y=str(yOffset))
        tempGraphic.text=parsedFilename
    elif os.path.isfile(str(srtFile[i].text)) == False:
        #this can also fail on malformed paths, like where srt[23].text is actually 2 concatenated file paths linked with a \n
        #TODO: make this code more flexible to account for above scenario
        print('"' + srtFile[i].text + '"'+ ' does not exist or is malformed, skipping')

firstEventTime=lowestBDNXMLinTimeObject[0]
lastEventTime=highestBDNXMLinTimeObject[0]

#print('Total Events: ' + str(numberOfEventsCounter))

#write last event
etree.SubElement(description, 'Events',  Type='Graphic', NumberofEvents=str(numberOfEventsCounter), ContentOutTC=lastEventTime, ContentInTC='00:00:00:00', FirstEventInTC=firstEventTime, LastEventOutTC=lastEventTime)

#debug code
#print(etree.tostring(xmldoc,pretty_print=True))  #send to stdout

#and finally writeout to filesystem
temp=etree.ElementTree(xmldoc)
try: 
    temp.write(outputFileName,pretty_print=True,xml_declaration=True, encoding='UTF-8')
    print('\n Wrote: ' + '"' + outputFileName + '"')
except:
    print('Unspecified error: '+sys.exc_info()[0])
