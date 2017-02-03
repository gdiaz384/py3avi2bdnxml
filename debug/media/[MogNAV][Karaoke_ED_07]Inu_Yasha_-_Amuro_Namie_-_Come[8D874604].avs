#LoadPlugin("C:\Program Files (x86)\K-Lite Codec Pack\Filters\vsfilter.dll")
#"C:\Program Files (x86)\VSFilter\VSFilter.dll" #older

vid="[MogNAV][Karaoke_ED_07]Inu_Yasha_-_Amuro_Namie_-_Come[8D874604].avi"
vid2="A Miracle That Starts With a Kiss - Steel Angel Kurumi OP.mp4"
#subs="[MogNAV][Karaoke_ED_07]Inu_Yasha_-_Amuro_Namie_-_Come[8D874604].srt"
aud=vid

FFIndex(vid) AudioDub(FFVideoSource(vid), FFAudioSource(aud))
#ConvertToRGB32()
#FFA#
#AddBorders(left=104,right=104)
AddBorders(104,0,104,0,0)

#video=last

#MaskSub(subs,video.width,video.height,video.framerate,video.framecount) 
#ConvertToRGB32()
#crop(20,400,0,0)
#FlipVertical()

#Spline64Resize(720,480)
#Spline64Resize(848,480)
#Spline64Resize(1280,720)
