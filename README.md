# py3avi2bdnxml

py3avi2bdnxml.py converts the imageTimings.srt produced by AVISubDetector to a BDN XML file that can be read by BDSup2Sub++. It is meant to be part of a larger workflow to convert hardsubs to softsubs as BD PGS (.sup) files in Matroska containers.

## Key Features:

- Works.
- Produces a standard BDNXML_output.xml file can be read by applications like BDSup2Sub++.
- Supports 23.976 and 24 fps modes. 
- Supports multiple resolutions (480, 720p, 1080p both 16:9 and 4:3 variants).
- Automatically removes quirks from SRT AVISubDetector file.
- Supports Romaji and Kanji modes (experimental).

## Workflow Features:

- Provides a non-OCR way to include subs.
- Ideal for subs foriegn to one's native language.
- Ideal for difficult to OCR fonts and non-Latin scripts (Chinese, Arabic, Devanagari, Cyrillic).
- Automatic generates timing information from hardsubs (SRT/ASS).

## Planned Features:

- Future: Supports quirky SRT to "standard SRT" conversions.
- Future: Supports merging discrete AVISubDetector SRT files.
- Future: Additional fps modes.

## Hardsubs.AVI -> BD PGS image-based softsubs Workflow:

1. First, due to BD PGS limitations, make sure source video is in 480p, 720p, or 1080p.
    Hint: Use AVIsynth's spline64resize()
2. Load .avi or .avs file with AVISubDetector (use 32-bit avisynth or avi2fs)
3. Use the following settings for AVISubDetector:
    ![screenshot1](pics/AVISubDetector_settings1.png)
4. press "Start" and wait a while.
5. When done, close AVISubDetector.
6. Process the resulting .SRT into py3avi2bdnxml using the appropriate settings.
6. Move the resulting XML to the SubPic\ directory created by AVISubDetector
7. Open SubPic\output.xml using [bdsup2sub++](http://www.videohelp.com/software/BDSup2Sub).
8. Extend/delete/upscale/shift and otherwise modify subs as necessary.
9. Export to SUP(BD) format (Settings: Set Palette as "create new" filtered w/Lanczos3).
10. Play target video matching the resolution specified with MPC to view the result.
    File->Subtitles->Load Subtitles or Ctrl+L or drag and drop output.sup onto video to test.
12. Mux video.avi and output.sup together using mkvtoolsnix.
    Optional: specify a delay timing for syncing purposes.

## Example Usage Settings:

Note: [ ] means optional.

Syntax: py3avi2bdnxml.py input.srt
    [-h] [-q QUALITY] [-xo XOFFSET] [-yo YOFFSET]
    [-fps FRAMESPERSECOND] [-e SRTENCODING] [-ok] [-or]
    [-kf KANJIFILE] [-rf ROMAJIFILE] [-kr] [-ip] [-pl]
    [-d] [-o OUTPUT]

CorrectUsage: 
```
py3avi2bdnxml input.srt 
py3avi2bdnxml input.srt -o output.xml
py3avi2bdnxml input.srt -o output.xml -q 480p 
py3avi2bdnxml input.srt -o output.xml -ro -ip
py3avi2bdnxml input.srt -o output.xml -ko -ip
```

Optional Argument | Description
--- | ---
-h, --help        |    show this help message and exit
-q QUALITY, --quality QUALITY | specify quality 480p/720p/1080p, default=720p
-xo XOFFSET, --xOffset XOFFSET| specify how far kanji should be from left and right, >=2 and <=video.width, default=2
-yo YOFFSET, --yOffset YOFFSET| specify how far dialogue and romaji should be from bottom and top, >=2 and <=video.height, default=2
-fps FRAMESPERSECOND, --framesPerSecond FRAMESPERSECOND | specify conversion rate from SRT to BDN XML timecodes, default is 24000/1001
-e SRTENCODING, --srtEncoding SRTENCODING | specify encoding for input files, default=utf-8
-ok, --onlyKanji      | specify the only input file represents a line of vertical Kanji input
-or, --onlyRomaji    | specify the only input file represents Romaji input
-kf KANJIFILE, --kanjiFile KANJIFILE | specify an additional Kanji input file
-rf ROMAJIFILE, --romajiFile ROMAJIFILE | specify an additional Romaji input file
-kr, --kanjiRight    | alignment for Kanji should be on the Right ,default=Left
-ip, --enableImageProcessing | vertically flip romaji images and rotate kanji ones clockwise, or counterclockwise
-pl, --preferLast    | when resolving duplicate file entries for a subtitle, prefer the last one list, default=First
-d, --debug          | display calculated settings and other miscellaneous information
-o OUTPUT, --output OUTPUT | specify the output file name, default is to change to .xml
  
- Quality Options: 480p, 480p_43, 720p, 720p_43, 1080p, 1080p_43, (720p)
- FPS Options: 24, 24000/1001, (24000/1001)
    - Note: Other FPS modes will process without error but are considered highly experimental.
- XOffset: 2-4 recommended, Minimum: 2, Default: 2
- YOffset: 2-4 recommended, Minimum: 2, Default: 2

## Download and Install Guide:

```
Latest Version: 0.1-alpha
In Development: 0.1-beta Open an issue for bugs, feature or compile requests if something needs updating.
```
1. Click [here](//github.com/gdiaz384/py3avi2bdnxml/releases) or on "releases" at the top to download the latest version.
2. Extract py3avi2bdnxml.exe from the archive of your OS/architecture.
3. Place py3avi2bdnxml.exe in your environmental path.
    To find places to put it: cmd.exe -> echo %path%
4. (optional) Rename to something more memorable.
6. For usage, refer to the  **Workflow Example** and **Example Usage Guide**  sections.

## Release Notes:

- Due to console limitations, consider using [Notepad++](//notepad-plus-plus.org/download) to change the input to UTF-8 when debuging.
- If downloading directly from github instead of using a release.zip, remember to change the line ending back to Windows before attempting to use it by using Notepad++ (if applicable).

## Script Dependencies and Compile(exe) Guide

- Remember to change the line ending back to not-broken-because-of-github if downloading from github directly using [Notepad++](//notepad-plus-plus.org/download) before attempting to compile. 
- Pyinstaller compatible character encodings for .py files are ANSI and UTF-8 w/o BOM.
 
   - [Python 3.2-3.4](//www.python.org/downloads)  #remember to add to %path%
   - [pysrt](//github.com/byroot/pysrt) by byroot    #srt library dependency
   - [Pillow image library](//python-pillow.org)    #image library dependency
   - [lxml](//pypi.python.org/pypi/lxml), Windows: [lxml-3.2.5.win-amd64-py3.4.exe](//pypi.python.org/pypi/lxml/3.2.5)  #xml parsing dependency
   - [pyinstaller](http://www.pyinstaller.org)     #repackager

```
>python --version   #requires 3.2-3.4
> non-Windows: pip install lxml
For Windows, Download and install from the hosted binaries
>pip uninstall PIL   #uninstall python image library if installed
>pip install Pillow
>pip install pysrt
>pip install pyinstaller
>pyinstaller --version  #makes sure it installed
>pyinstaller --onefile py3avi2bdnxml.py  #Look for the output under the "dist" folder.
```

## License:

Script (.py): Pick your License (any), Examples: GPL (any) or BSD (any) or MIT/Apache.
Binaries (.exe): GPL 3.0
Also: The binaries in workflow.zip each have their own licenses.
