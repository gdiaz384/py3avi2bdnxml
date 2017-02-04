# py3srt2bdnxml

py3srt2bdnxml.py converts the imageTimings.srt produced by AVISubDetector to a BDN XML file that can be read by BDSup2Sub++.
It is meant to be part of a larger workflow to include foreign hardsubs as BD PGS (.sup) files in Matroska containers.

## Key Features:

- Works.
- Standard BDNXML output.xml file can be read by applications like BDSup2Sub++.
- Supports 23.976 and 24 fps modes. 
- Supports multiple resolutions (480, 720p, 1080p both 16:9 and 4:3 variants).
- Automatically remove quirks from SRT AVISubDetector file.

## Workflow Features:

- Provides a non-OCR way to include subs.
- Ideal for subs foriegn to one's native language.
- Ideal for difficult to OCR fonts and character sets.
- Automatic generates timing information from hardsubs in SRT format.
   - Change to .ASS format via Aegisub or Subtitle Edit.

## Planned Features:

- Future: Supports quirky SRT to "standard SRT" conversions.
- Future: Supports merging discrete AVISubDetector SRT files.
- Future: Supports Romaji and Kanji modes.
- Future: Additional fps modes.

## Example Usage Guide:

Syntax: py3srt2bdnxml myfile.srt [--quality  720p

Options (Default):
Quality: 480p, 480p_43, 720p, 720p_43, 1080p, 1080p_43, (720p)
FPS: 23.976, 24, (23.976) -All other FPS modes are experimental.


Note: [ ] means optional.

```
Syntax help:
py3srt2bdnxml -h
py3srt2bdnxml --help

Basic Usage:
py3srt2bdnxml myfile.srt
py3srt2bdnxml myfile.srt --quality 480p

Advanced Usage:
py3srt2bdnxml --infile myfile.srt --quality 480p --pixels-from-bottom 2

```

## Hardsubs.AVI -> BD PGS image-based softsubs Workflow:

1. First, due to BD PGS limitations, make sure source video is in 16:9 480p, 720p, or 1080p
e.g. add letterboxing via AVIsynth's addborder(), spline64resize() and transcode if necessary
2. load .avi or .avs file with aviSubDetector (use 32-bit avisynth or avi2fs)
3. Use the following settings for aviSubDetector:
[picture 1]()
[picture 2]()
4. press "Start" and wait a while
5. When done, close AVIsubDetector
6. feed the resulting .srt into py3srt2bdnxml w/appropriate quality setting
7. feed the resulting .xml into [bdsup2sub++](bdsup2sub++1.0.2_win32.exe)
8. extend/delete/upscale and otherwise modify subs as necessary
9. export to SUP(BD) format (Preffered: Set Palette as "create new" filtered w/Lanczos3)
10. play target video matching the resolution specified w/MPC
11. File->Subtitles->Load Subtitles or ctrl+L or drag and drop output.sup onto video to test
12. Mux video.h264 and output.sup together using mkvtoolsnix (optional: specify a delay timing for syncing purposes)

## Download and Install Guide:
```
Latest Version: 0.1-alpha
Development: in progress. Open an issue for bugs, feature or compile requests if something needs updating.
```
1. Click [here](//github.com/gdiaz384/py3srt2bdnxml/releases) or on "releases" at the top to download the latest version.
2. Extract py3srt2bdnxml.exe from the archive of your OS/architecture.
3. Place py3srt2bdnxml.exe in your enviornmental path.
  - To find places to put it: >echo %path%
4. (optional) Rename it to something more memorable.
6. Refer to the **Example Usage Guide** above for usage or **Workflow Example** below.

## Release Notes:
- Due to console limitations, consider using [Notepad++](//notepad-plus-plus.org/download) to change the input to utf-8 when debuging.
- If downloading a replacementList.txt from github directly instead of using a release.zip, remember to change the line ending back to Windows before attempting to use it by using Notepad++ (if applicable).

## Script Dependencies
- To compile: 
   - [Python 3.2-3.4](//www.python.org/downloads)
   - [pyinstaller](http://www.pyinstaller.org)
   - Pillow image library
   - pysrt by byroot
   - lxml

## Compile(exe) Guide:

- Remember to change the line ending back to not-broken-because-of-github if downloading from github directly using [Notepad++](//notepad-plus-plus.org/download) before attempting to compile. 
- Pyinstaller compatible character encodings for .py files are ANSI and utf-8 w/o BOM.

```
>python --version   #requires 3.2-3.4  Install from [Python.org](https://www.python.org/downloads/), remember to add to %path%
#xml parsing dependency
For non-Windows: pip install lxml
For Windows, Download and install (lxml-3.2.5.win-amd64-py3.4.exe)[https://pypi.python.org/pypi/lxml/3.2.5]
>pip uninstall pil   #uninstall python image library if installed
>pip install Pillow   #image library dependency
>pip install pysrt   #srt library dependency
>pip install pyinstaller  #repackager
>pyinstaller --version  #to make sure it installed
>pyinstaller --onefile py3srt2bdnxml.py
```
Look for the output under the "dist" folder.

## License:

Script (.py): Pick your License (any), Examples: GPL (any) or BSD (any) or MIT/Apache.
Binaries (.exe): GPL 3.0
Also: The binaries in workflow.zip each have their own licenses.
