# PhotoOrganizer
This program rearranges an existing photo library by EXIF in the metadata.
This program will modify the old photo library and rename the files.
This program will modify the each photo's created date in your system. 
This is done so that NextCloud photos can display your pictures in chronological order.
This program will not modify the pictures size, resolution, etc 

1. FOLDER STRUTURE
The new folder structure will be Year/Month/photoFile

2. PHOTO FILE NAMING
Each picture will be renamed to match the exif. 
Prefix IMG for pictures and VID for videos
Date YY-MM-DD HH-MM-SS

EXAMPLE OF OUTPUT: ../newPhotoLibrary/2023/01/IMG 23-01-01 13-50-35.JPG


REQUIREMENTS:
Requires that exif tool https://exiftool.org python and pip be installed in your computer.

INSTRUCTIONS:
1. Copy your photo library to the "oldPhotoLibrary" downloaded with this program 

In the command line

2. Change directory to the folder where you saved this repository
3. Type "source bin/activate"
4. Type "pip install -r requirements.txt"
5. Type "python main.py"
6. Check for the status. The program makes two passes one for pictures and another one for videos. 
7. Once processing is done read the summary and type "y" or "n". Typing "y" will rearrange the pictures in oldPhotoLibrary
8. Check the newPhotoLibrary folder
9. Copy the contents of the newPhotoLibrary to your nextCloud folder preserving timestamps
   - In linux/macOS type "cp -R -p newPhotoLibrary/ NextPhotoLibrary/"
