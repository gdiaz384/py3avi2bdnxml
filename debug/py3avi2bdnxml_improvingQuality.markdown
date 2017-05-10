## improving quality

Disclaimer: Only transcribing the entire series into softsubs can make it pefect. This method cannot capture subtitles with perfect accuracy. In the end, only so much can be done to improve quality. Try to keep quality at least above 95% (1 error every 20 lines) and not worry too worry too much about the errors that occur after that due to diminishing returns of additional effort.

### AVISubDetector Settings

* Use the default settings, change only the crop settings
* Use the highest crop setting possible (find a 2-liner and crop just above and just below it)
* If the program has on screen-text that is occasionally getting captured as well, then and only then: 
    * change the "Subpicture Box Margins" down from 16 pixels to a lower value, such as 9-14. 
        * Note: This risks splitting a single line into multiple sub-pictures, thus ruining the capture.

### AVISubDetector "SubPic" Directory Checklist

delete the false positives found in SubPic\
See: Using explorer properly.

crop any overly large ones
Hint: Use the crop tool in photoshop.

merge duplicates
1. identify the first in a series of duplicates
1. identify the last in the series of duplicates
1. open avisubdetector_output.srt and find the last reference for duplicate
    1. copy the ending time
    1. replace the ending time of the first in the series with the ending time of the last duplicate
    1. make the duplicates after the first in the series inaccessible
        * suggestion make a new folder, move the duplicates, excluding the first one, to that new folder 

missing/cut lines and "3" liners

Missing line:
cut line: missing 2nd part of top
3 liners: missing 3rd part of top
Go find the missing line in the episode. Capture it into a raw.png
place into subpic\
modify the avisubdetector_output.srt to include it
time it manually if necessary

### py3avi2bdnxml

The only FPS modes currently supported are 24 and 24000/1001. For other FPS counts, use Bdsup2sub to convert between frame rates.

set the proper pixel Y-offset to the subtitle pictures (-df-yo, -rf-yo). The default value is 2.

Remember to set the resolution properly for the target video size or the, 720p by default.

Subtitles for 4:3 resolutions are not currently displayed properly. Use BDsup2sub's batch image mode to modify placement.

Use the --image-processing switch once, and only once, to change the rotation of romaj (flip vertical) and kanji (rotate 90 or 270) files automatically. If needing to recreate the capture.xml at a later time, omit it from subsequent passes. --image-processing will not process images not actually parsed to be included in the final output (e.g. resolving duplicates), so every image may not actually be processed initially. Rotate the pictures not rotated manually if they need to be included after the -ip switch has already been used, or the -ip switch will re-flip the properly.

Usage of the --image-processing switch resamples the image using the Pillow image library when creating the new "correct" version and is a lossly operation. IDK how to make it lossless.

### bdsup2sub v1.0.2

The highest quality is to include the original files Palette: keep existing but this will create unecessarily large files
the reccomended settings are Palette: create new and Filter: Lanczos3

bdsup2sub v1.0.2 requires the parsed.xml and every picture referenced in it to be in the same folder
this means the pictures must have different names and, by default, avisubdetector will create conflicting (identical) names for the .bmp files it generates that are based on the name of the video file loaded every time it is run.

e.g.:  example:
myfile.avs
will create .bmp files with identifcal conflict if run multiple times

This is not an issue when running a single pass through a video file but can create issues when multiple passes are run (such as with different crop settings or for romaji/kanji). To avoid these conflicting file names, the avi/avs file must be renamed every pass

Every AVISubDetector pass that will be used to generate entries for the final should be uniquely named:
myfile.avs
myfile.second.avs
myfile.romaji.avs
myfile.kanji.avs
The resulting output.bmp files will not have names that conflict with each other and can be placed into the same directory without overring each other.

### Improving Speed:

To run this AVISubdetector on multiple episodes concurrently do the following in __exactly__ this order:

1. start avisubdetector
1. update the project autosave directory path
1. open AVI/AVS
1. click on the settings tab
1. determine correct crop settings for your video, save them (settings-save settings)
1. close avisubdetector
1. start a new instance
1. Important: modify the project autosave directory
1. after modifying the project autosave directory, then open AVI/AVS
1. click on the settings tab
1. settings settings-load settings
1. Start [Full]
1. minimize the instance
1. start a new instance...

* Note: The instances will render their respective GUIs mostly inoperable once the process completes, and will need to be closed. This bug does not affect the functionality of new instances or other currently operating instances.

Use explorer properly:

* List mode shows all files, use to get to the last files in a folder quickly.
* extra large + preview is the "image viewer" mode and can be used to quickly identify false positives, incorrectly cut ones and duplicates
* Use large icon mode temporarily generates icons for extra large mode.
