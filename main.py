import exiftool
import os
import time
from datetime import datetime
import pathlib

#This program rearranges an existing photo library by EXIF in the metadata.
#This program will modify the old photo library and rename the files.
#This program will modify the each photo's created date in your system.
#this is done so that NextCloud photos can display your pictures in chronological order.
#This program will not modify the pictures size, resolution, etc 

#1. FOLDER STRUTURE
#The new folder structure will be Year/Month/photoFile

#2. PHOTO FILE NAMING
#Each picture will be renamed to match the exif. 
#Prefix IMG for pictures and VID for videos
#Date YY-MM-DD HH-MM-SS

#EXAMPLE OF OUTPUT: ../newPhotoLibrary/2023/01/IMG 23-01-01 13-50-35.JPG

#HANDLING OF UNSOPPORTED FILES
#There are cases where the pictures EXIF data is incosistent or inexistent.
#This program will move these pictures to the following folders
# ../oldPhotoLibrary/InconsistentMeta for incosistent file type between the file and the EXIF data
# ../oldPhotoLibrary/NoMeta for pictures without EXIF data

# Change OLD_PATH and NEW_PATH to any other path in you system as desired. 
# Current OLD_PATH and NEW_PATH use the newPhotoLibrary and oldPhotoLibrary that
# come with this repository

PATH = str(pathlib.Path(__file__).parent.resolve())
OLD_PATH = PATH+"/oldPhotoLibrary/"
NEW_PATH = PATH+'/newPhotoLibrary/'

def get_metadata(file):
    with exiftool.ExifToolHelper() as et:
        try:
            metadata = et.get_metadata(file)
            return(metadata)
        except:
            return(None)

def get_create_date(metadata):
    createDate=None
    for d in metadata:
        if 'QuickTime:CreateDate' in d:
            createDate = d['QuickTime:CreateDate']
        elif 'EXIF:CreateDate' in d:
            createDate = d['EXIF:CreateDate']
        elif 'EXIF:DateTimeOriginal' in d:
            createDate = d['EXIF:DateTimeOriginal']
    return createDate

def get_exif_file_format(metadata):
    for d in metadata:
        fileFormat = d['File:FileTypeExtension']
    return fileFormat.lower()

def get_photo_media_group(metadata):
    for d in metadata:
        if 'MakerNotes:MediaGroupUUID' in d.keys():
            return d['MakerNotes:MediaGroupUUID']
        elif 'MakerNotes:ImageUniqueID' in d.keys():
            return d['MakerNotes:ImageUniqueID']
        else:
            return None

def get_video_content_id(metadata):
    for d in metadata:
        if 'QuickTime:ContentIdentifier' in d.keys():
            return d['QuickTime:ContentIdentifier']
    return None

def get_file_name_extension(fileName):
    fileExtension = pathlib.Path(fileName).suffix
    return fileExtension.replace('.','').lower()

def get_files_only(path,fileList):
    newFileList = []
    for fileItem in fileList:
        if os.path.isfile(f'{path}{fileItem}'):
            newFileList.append(fileItem.lower())
    return newFileList


def validate_live_photos(livePhotosList):
    for item in livePhotosList:
        if item['primaryFile'] is None or item['secondaryFile'] is None:
            return False
    return True

def check_extension_format(fileExtension, fileFormat):
    if fileExtension == "jpg" or fileExtension == "jpeg":
        if fileFormat == "jpeg" or fileFormat == "jpg":
            return True
    elif fileExtension =="heic" and fileFormat == "heic":
        return True
    elif fileExtension =="png" and fileFormat == "png":
        return True
    return False

def check_live_photo_video(pictureFile, fileExtension, fileList):
    movFileName = pictureFile.replace("."+fileExtension,'.mov')
    mmp4FileName = pictureFile.replace("."+fileExtension,'.mp4')
    if movFileName in fileList:
        return movFileName
    elif mmp4FileName in fileList:
        return mmp4FileName
    return None

def get_photos(cleanFiles):
    noMeta = []
    live = []
    still = []
    inconsistentMeta = []
    counter = 0
    for fileItem in cleanFiles:
        counter += 1
        print(f'Processing {counter}/{len(cleanFiles)} Pass 1')
        photo_UUID = None
        video_UUID = None
        metadata = get_metadata(OLD_PATH+fileItem)
        if metadata:
            fileFormat = get_exif_file_format(metadata)
            fileExtension = get_file_name_extension(fileItem)
            if fileFormat in ['jpg', 'jpeg', 'heic', 'png']:
                photo_UUID = get_photo_media_group(metadata)
                if check_extension_format(fileExtension, fileFormat) is False:
                    inconsistentMeta.append(fileItem)
                    livePhotoVideoFileName = check_live_photo_video(fileItem, fileExtension, cleanFiles)
                    if livePhotoVideoFileName is not None:
                        secondaryMetadata = get_metadata(f'{OLD_PATH}{livePhotoVideoFileName}')
                        video_UUID = get_video_content_id(secondaryMetadata)
                        if photo_UUID is not None and video_UUID is not None and photo_UUID == video_UUID:
                            inconsistentMeta.append(livePhotoVideoFileName)
                else:
                    createDate = get_create_date(metadata)
                    if createDate:
                        livePhotoVideoFileName = check_live_photo_video(fileItem, fileExtension, cleanFiles)
                        if  livePhotoVideoFileName is not None:
                            secondaryMetadata = get_metadata(f'{OLD_PATH}{livePhotoVideoFileName}')
                            video_UUID = get_video_content_id(secondaryMetadata)
                            secondaryFormat = get_exif_file_format(secondaryMetadata)
                        if photo_UUID is not None and video_UUID is not None and photo_UUID == video_UUID:
                            live.append({'primaryFile':fileItem,
                                        'secondaryFile':livePhotoVideoFileName, 
                                        'created': createDate,
                                        'primaryFileFormat': fileFormat,
                                        'secondaryFileFormat': secondaryFormat})
                        else:
                            still.append({'primaryFile':fileItem,
                                          'secondaryFile':None,
                                          'created': createDate,
                                          'primaryFileFormat':fileFormat,
                                          'secondaryFileFormat':None})
        else:
            noMeta.append(fileItem)
    if validate_live_photos(live):
        return {'live':live,
                'still':still,
                'noMeta':noMeta,
                'inconsistentMeta':inconsistentMeta}
    else: return None
def get_videos(cleanFiles):
    single = []
    noMeta = []
    counter = 0
    for fileItem in cleanFiles:
        counter += 1
        print(f'Processing {counter}/{len(cleanFiles)} Pass 2')
        metadata = get_metadata(OLD_PATH+fileItem)
        if metadata:
            fileFormat = get_exif_file_format(metadata)
            if fileFormat in ['mov', 'mp4']:
                createDate = get_create_date(metadata)
                if createDate:
                    single.append({'primaryFile':fileItem,
                                   'secondaryFile':None,
                                   'created':createDate, 
                                   'primaryFileFormat':fileFormat,
                                   'secondaryFileFormat': None})
                else:
                    noMeta.append(fileItem)
    return {'single':single,
            'noMeta': noMeta}

def remove_photos_from_file_list(photos,cleanFiles):
    for item in photos['inconsistentMeta']:
        cleanFiles.remove(item)
    for item in photos['noMeta']:
        cleanFiles.remove(item)
    for item in photos['still']:
        cleanFiles.remove(item['primaryFile'])
    for item in photos['live']:
        cleanFiles.remove(item['primaryFile'])
        cleanFiles.remove(item['secondaryFile'])
    return cleanFiles

def remove_videos_from_file_list(videos, cleanFiles):
    for item in videos['single']:
        cleanFiles.remove(item['primaryFile'])
    for item in videos['noMeta']:
        cleanFiles.remove(item)
    return cleanFiles

def move_files(item):
    fileDate = datetime.strptime(item['created'], '%Y:%m:%d %H:%M:%S')
    if item['primaryFileFormat'] in ['jpg','jpeg','heic','png']:
        prefix = 'IMG'
    elif item['primaryFileFormat'] in ['mp4', 'mov']:
        prefix = 'VID'
    newNamePrimary = f"{prefix} {fileDate.strftime('%y-%m-%d %H-%M-%S')}.{item['primaryFileFormat']}"
    newFileLocation = f'{NEW_PATH}{fileDate:%Y}/{fileDate:%m}/'
    modTime = time.mktime(fileDate.timetuple())
    os.makedirs(newFileLocation, exist_ok=True)
    os.rename(f"{OLD_PATH}{item['primaryFile']}",f"{newFileLocation}{newNamePrimary}")
    os.utime(f'{newFileLocation}{newNamePrimary}', (modTime, modTime))
    if item['secondaryFile']:
        newNameSecondary = f"{prefix} {fileDate.strftime('%y-%m-%d %H-%M-%S')}.{item['secondaryFileFormat']}"
        os.rename(f"{OLD_PATH}{item['secondaryFile']}",f"{newFileLocation}{newNameSecondary}")
        os.utime(f'{newFileLocation}{newNameSecondary}', (modTime, modTime))

def move_no_metadata(item):
    newFileLocation = f'{OLD_PATH}NoMeta/'
    os.makedirs(newFileLocation, exist_ok=True)
    os.rename(f"{OLD_PATH}{item}",f"{newFileLocation}{item}")

def move_inconsistent_metadata(item):
    newFileLocation = f'{OLD_PATH}IncosistentMeta/'
    os.makedirs(newFileLocation, exist_ok=True)
    os.rename(f"{OLD_PATH}{item}",f"{newFileLocation}{item}")

def move_not_supported(item):
    newFileLocation = f'{OLD_PATH}NotSupported/'
    os.makedirs(newFileLocation, exist_ok=True)
    os.rename(f"{OLD_PATH}{item}",f"{newFileLocation}{item}")

def main():
    print(OLD_PATH)
    files = os.listdir(OLD_PATH)
    cleanFiles = get_files_only(OLD_PATH, files)
    totalFilesRead = len(cleanFiles)
    photos = get_photos(cleanFiles)
    if photos:
        cleanFiles = remove_photos_from_file_list(photos,cleanFiles)
    videos = get_videos(cleanFiles)
    if videos:
        cleanFiles = remove_videos_from_file_list(videos,cleanFiles)
    notSupported = cleanFiles

    print("\n")
    print(f"Total Files Read: {totalFilesRead}")
    print(f"Photos Live: {len(photos['live'])}")
    print(f"Photos Still: {len(photos['still'])}")
    print(f"Photos No Metadata: {len(photos['noMeta'])}")
    print(f"Videos Live: {len(photos['live'])}")
    print(f"Videos Single: {len(videos['single'])}")
    print(f"Videos No Metadata: {len(videos['noMeta'])}")
    print(f"Inconsistent Metadata: {len(photos['inconsistentMeta'])}")
    print(f"Not Supported Files: {len(notSupported)}")

    inp = input("\n Proceed arranging library Y/n: ").lower()
    if inp == 'y':
        for photo in photos['live']:
            move_files(photo)
        for photo in photos['still']:
            move_files(photo)
        for video in videos['single']:
            move_files(video)
        for file in photos['noMeta']:
            move_no_metadata(file)
        for file in videos['noMeta']:
            move_no_metadata(file)
        for file in photos['inconsistentMeta']:
            move_inconsistent_metadata(file)
        for file in notSupported:
            move_not_supported(file)

main()