"""
###########################################################################
version: 1.2 experimental
Written in: Python 2.7.3
author: Kaze
date created: 1/20/2013
date edited : 1/22/2013
supported directory format:
    <full directory tree of sub directories regardless of level>
updated: recursive functions added
        recursive copy,delete
        user defined destination paths
        choice of menu style or not
next update:
    <finish up the selective copying and deletion functions>
future updates (not in order):
    1: allow for the option to compile mangas into volumes instead of
         one main folder
    2: expand file type, extension list
    3: music organizer. sort through a directory and then output a sorted
        directory of music files sorted by metadatas: artist and/or album
usage: this program will take the contents of the old directory and then
move them into a new directory without subfolders
###########################################################################
"""
import os, sys, time
#global size limit symbolics
#the numerics are in bytes,
maxFileLoad = 1024*15000  #restrict max size limit to 15mb 
blockSize = 1024 * 5000   #will read 5mb at a time

#change the following constant values to change the behavior of the program

#controls whether or not the program will function as a copy or a move script
removeOldDirectory = False
#controls whether the functions will copy all files or dictated files
selectiveCopying = True 
#controls whether path for folder creation will be default or dictated
userDefinedPath = False
#controls the recursive removal of directories, if false will not remove original main folder
deleteMainDir = True
removefiles = True
#activates the menu style, and overpowers the initial settings
menuStyle = False

#function for getting and testing directories
def getDirs(userDefinedPath = userDefinedPath):
    
    #check if the from directory is an actual directory
    while True:
        dirFrom = raw_input('enter input directory location: ')
        if not os.path.isdir(dirFrom):
            print'Error: the input directory is either:'
            print'not a directory or does not exist'
        else:
            break
    dirTo = dirFrom + '_compiled'
    #make new directory 
    if userDefinedPath == False:
        while True:
            if os.path.isdir(dirTo):
                dirTo = dirTo + '_copy'
            else:
                os.mkdir(dirTo)
                break
    else:
        while True:
            dirTo = raw_input('full destination path: ')
            if not os.path.isdir(dirTo):
                os.mkdir(dirTo)
                break
            else:
                print 'Creation Error: Directory already exists'
    return (dirFrom,dirTo)

#directory function for selective copying/moving
def createSelectiveDir(userDefinedPath = userDefinedPath):
    #check if the input directory is an existing directory
    while True:
        dirFrom = raw_input('enter input directory location: ')
        if not os.path.isdir(dirFrom):
            print'Error: the input directory is either:'
            print'not a directory or does not exist'
        else:
            break
    extensionList = []
    stringOfSupportedTypes = 'music video image pdf book'
    while True:
        extension = raw_input('File type (music,video,image,pdf,book)(enter for break): ')
        if extension == '':
            break
        elif extension in stringOfSupportedTypes:
            extensionList.append(extension)
        else:
            print 'You have entered a non supported file type'
            print 'Please check the spelling'
    #list containing the sub folder paths
    folderPathDict = {}
    #folders creation
    if userDefinedPath == False:
        dirTo = dirFrom + ' Sorted'
        os.mkdir(dirTo)
        #creation of folders containing the sorted files
        for item in extensionList:
            folderPath = os.path.join(dirTo,item)
            os.mkdir(folderPath)
            folderPathDict[item]=(folderPath)
    else: #for user defined path
        dirPath = raw_input('Full destination path: ')
        os.mkdir(dirPath)
        #creation of folders containing the sorted files
        for item in extensionList:
            folderPath = os.path.join(dirPath,item)
            os.mkdir(folderPath)
            folderPathDict[item]=(folderPath)
    return (dirFrom,extensionList,folderPathDict)

    
#function for copying the files
#expanded to operate for bigger file sizes
def copyFile(pathFrom,pathTo,maxFileLoad = maxFileLoad):
    """
    copy one file pathFrom to pathTo, byte for byte
    uses binary file modes
    """
    chunksize = 0
    if os.path.getsize(pathFrom)<=maxFileLoad:
        #if file is less than 15mb
        #read the entire image file into memory
        fileFrom = open(pathFrom,'rb')
        bytesFrom = fileFrom.read()
        #write all bytes into new file
        bytesTo = open(pathTo, 'wb')
        bytesTo.write(bytesFrom)
        #manual closure of file objects
        fileFrom.close()
        bytesTo.close()
    else:
        #if file is bigger than 15mb
        fileFrom = open(pathFrom,'rb')
        fileTo = open(pathTo,'wb')
        totalsize = os.path.getsize(pathFrom)
        while True:
            #reads the data from the original file 5mb at a time into the memory
            bytesFrom = fileFrom.read(blockSize)
            #when there is no more data comming in from the read(), break from while loop
            if not bytesFrom: break
            #copy the 5mb read into memory into the new file
            print 'Nom nom nom...digesting byte chunks... ',100*(float(chunksize)/totalsize),'%'
            chunksize += blockSize
            fileTo.write(bytesFrom)
        print 'Digesting complete... 100.0%'
        #manual closure of file objects
        fileFrom.close()
        fileTo.close()      

#<full dir search>:recursive function
#<deep copy version>
def fullDirCopy(dirFrom,dirTo):
    fileCount = 0
    for filename in os.listdir(dirFrom):
        pathFrom = os.path.join(dirFrom,filename)
        pathTo = os.path.join(dirTo,filename)
        if not os.path.isdir(pathFrom): #if the tested file is not a directory
            try:
                print 'Copying: ',pathFrom,' to ',pathTo
                copyFile(pathFrom,pathTo)
                fileCount +=1
            except:
                print 'Error copying: ', pathFrom,' to ',pathTo,'--skipped'
                print sys.exc_info()[0],sys.exc_info()[1]
        else:
            try:
                subDirCounts = fullDirCopy(pathFrom,dirTo)
                fileCount += subDirCounts
            except:
                print 'Error Diving into directory ',pathFrom
                print sys.exc_info()[0],sys.exc_info()[1]
    return (fileCount)

#<full dir search>:recursive function
#>deep remove version>
def fullDirRemove(dirFrom):
    fileCount = 0
    for filename in os.listdir(dirFrom):
        pathFrom = os.path.join(dirFrom,filename)
        if not os.path.isdir(pathFrom):
            try:
                print 'Deleting: ',pathFrom
                os.remove(pathFrom)
                fileCount +=1
            except:
                print 'Error deleting: ', pathFrom,'--skipped'
                print sys.exc_info()[0],sys.exc_info()[1]
        else:
            try:
                subDirCounts = fullDirRemove(pathFrom)
                fileCount += subDirCounts[0]
            except:
                print 'File Removal: Error Diving into directory -> ',pathFrom
                print sys.exc_info()[0],sys.exc_info()[1]
    return (fileCount)

#recursive removal of directories
#checks for empty directories
    #if deleteMainDir is false, then it only deletes
    #empty subdirectories in the original path.
def fullDirDelete(dirFrom,deleteMainDir = deleteMainDir):
    for filename in os.listdir(dirFrom):
        pathFrom = os.path.join(dirFrom,filename)
        if os.path.isdir(pathFrom):
            if os.listdir(pathFrom)==[]:
                try:
                    print 'Deleting: ',pathFrom
                    os.rmdir(pathFrom)
                except:
                    print 'Error deleting: ', pathFrom,'--skipped'
                    print sys.exc_info()[0],sys.exc_info()[1]
            else:
                try:
                    fullDirDelete(pathFrom)
                except:
                    print 'Directory removal: Error Diving in directory -> ',pathFrom
                    print sys.exc_info()[0],sys.exc_info()[1]
    if not os.listdir(dirFrom)==[]:
        fullDirDelete(dirFrom)
    else:
        if deleteMainDir == True:
            os.rmdir(dirFrom)
            print 'Original directory deleted...'
        else:
            print 'Empty directories have been removed...'

                
#full dive: selective file copying function
#follows the full dive template: needs to be edited
def selectiveCopy(dirFrom,extensionList,folderPathDict):
    fileCount = 0
    for filename in os.listdir(dirFrom):
        pathFrom = os.path.join(dirFrom,filename)
        if not os.path.isdir(pathFrom): #if the tested file is not a directory
            if 'music' in extensionList: #mp3,flac
                pathTo = os.path.join(folderPathDict['music'],filename)
                if '.mp3' in filename or '.flac' in filename:
                    try:
                        print 'Copying: ',pathFrom,' to ',pathTo
                        copyFile(pathFrom,pathTo)
                        fileCount +=1
                    except:
                        print 'Error copying: ', pathFrom,' to ',pathTo,'--skipped'
                        print sys.exc_info()[0],sys.exc_info()[1]
            if 'video' in extensionList: #avi, mkv
                pathTo = os.path.join(folderPathDict['video'],filename)
                if '.avi' in filename or '.mkv' in filename:
                    try:
                        print 'Copying: ',pathFrom,' to ',pathTo
                        copyFile(pathFrom,pathTo)
                        fileCount +=1
                    except:
                        print 'Error copying: ', pathFrom,' to ',pathTo,'--skipped'
                        print sys.exc_info()[0],sys.exc_info()[1]
            if 'image' in extensionList: #jpg,png
                pathTo = os.path.join(folderPathDict['image'],filename)
                if '.jpg' in filename or '.png' in filename:
                    try:
                        print 'Copying: ',pathFrom,' to ',pathTo
                        copyFile(pathFrom,pathTo)
                        fileCount +=1
                    except:
                        print 'Error copying: ', pathFrom,' to ',pathTo,'--skipped'
                        print sys.exc_info()[0],sys.exc_info()[1]
            if 'pdf' in extensionList: #pdf only
                pathTo = os.path.join(folderPathDict['pdf'],filename)
                if '.pdf' in filename:
                    try:
                        print 'Copying: ',pathFrom,' to ',pathTo
                        copyFile(pathFrom,pathTo)
                        fileCount +=1
                    except:
                        print 'Error copying: ', pathFrom,' to ',pathTo,'--skipped'
                        print sys.exc_info()[0],sys.exc_info()[1]
            if 'book' in extensionList: # epub, mobi
                pathTo = os.path.join(folderPathDict['book'],filename)
                if '.epub' in filename or '.mobi' in filename:
                    try:
                        print 'Copying: ',pathFrom,' to ',pathTo
                        copyFile(pathFrom,pathTo)
                        fileCount +=1
                    except:
                        print 'Error copying: ', pathFrom,' to ',pathTo,'--skipped'
                        print sys.exc_info()[0],sys.exc_info()[1]
        else:
            try:
                subDirCounts = selectiveCopy(pathFrom,extensionList,folderPathDict)
                fileCount += subDirCounts
            except:
                print 'Selective Copy: Error Diving in directory -> ',pathFrom
                print sys.exc_info()[0],sys.exc_info()[1]
    return (fileCount)

#full dive: selective file removal function
#follows the full dive template: needs to be edited
def selectiveRemove(dirFrom,extensionList):
    fileCount = 0
    for filename in os.listdir(dirFrom):
        pathFrom = os.path.join(dirFrom,filename)
        if not os.path.isdir(pathFrom): #if the tested file is not a directory
            if 'music' in extensionList: #mp3,flac
                if '.mp3' in filename or '.flac' in filename:
                    try:
                        print 'Deleting: ',pathFrom
                        os.remove(pathFrom)
                        fileCount +=1
                    except:
                        print 'Error deleting: ', pathFrom,'--skipped'
                        print sys.exc_info()[0],sys.exc_info()[1]
            if 'video' in extensionList: #avi, mkv
                if '.avi' in filename or '.mkv' in filename:
                    try:
                        print 'Deleting: ',pathFrom
                        os.remove(pathFrom)
                        fileCount +=1
                    except:
                        print 'Error deleting: ', pathFromo,'--skipped'
                        print sys.exc_info()[0],sys.exc_info()[1]
            if 'image' in extensionList: #jpg,png
                if '.jpg' in filename or '.png' in filename:
                    try:
                        print 'Deleting: ',pathFrom
                        os.remove(pathFrom)
                        fileCount +=1
                    except:
                        print 'Error deleting: ', pathFrom,'--skipped'
                        print sys.exc_info()[0],sys.exc_info()[1]
            if 'pdf' in extensionList: #pdf only
                if '.pdf' in filename:
                    try:
                        print 'Deleting: ',pathFrom
                        os.remove(pathFrom)
                        fileCount +=1
                    except:
                        print 'Error deleting: ', pathFrom,'--skipped'
                        print sys.exc_info()[0],sys.exc_info()[1]
            if 'book' in extensionList: # epub, mobi
                if '.epub' in filename or '.mobi' in filename:
                    try:
                        print 'Deleting: ',pathFrom
                        os.remove(pathFrom)
                        fileCount +=1
                    except:
                        print 'Error deleting: ', pathFrom,'--skipped'
                        print sys.exc_info()[0],sys.exc_info()[1]
        else:
            try:
                subDirCounts = selectiveRemove(pathFrom,extensionList)
                fileCount += subDirCounts
            except:
                print 'Selective Remove: Error Diving into directory -> ',pathFrom
                print sys.exc_info()[0],sys.exc_info()[1]    
    return (fileCount)

#<full dive> full dir move
#follows the full dive copy algorithm template
def fullDirMove(dirFrom,dirTo):
    fileCount = 0
    for filename in os.listdir(dirFrom):
        pathFrom = os.path.join(dirFrom,filename)
        pathTo = os.path.join(dirTo,filename)
        if not os.path.isdir(pathFrom): #if the tested file is not a directory
            try:
                print 'Moving: ',pathFrom,' to ',pathTo
                os.renames(pathFrom,pathTo)
                fileCount +=1
            except:
                print 'Error moving: ', pathFrom,' to ',pathTo,'--skipped'
                print sys.exc_info()[0],sys.exc_info()[1]
        else:
            try:
                subDirCounts = fullDirMove(pathFrom,dirTo)
                fileCount += subDirCounts
            except:
                print 'Error Diving into directory ',pathFrom
                print sys.exc_info()[0],sys.exc_info()[1]
    return (fileCount)


#<full dive> selective move
#fullows the selective copy algorithm template
def selectiveMove(dirFrom,extensionList,folderPathList):
    fileCount = 0
    for filename in os.listdir(dirFrom):
        pathFrom = os.path.join(dirFrom,filename)
        if not os.path.isdir(pathFrom): #if the tested file is not a directory
            if 'music' in extensionList: #mp3,flac
                pathTo = os.path.join(folderPathDict['music'],filename)
                if '.mp3' in filename or '.flac' in filename:
                    try:
                        print 'Moving: ',pathFrom,' to ',pathTo
                        os.renames(pathFrom,pathTo)
                        fileCount +=1
                    except:
                        print 'Error moving: ', pathFrom,' to ',pathTo,'--skipped'
                        print sys.exc_info()[0],sys.exc_info()[1]
            if 'video' in extensionList: #avi, mkv
                pathTo = os.path.join(folderPathDict['video'],filename)
                if '.avi' in filename or '.mkv' in filename:
                    try:
                        print 'Moving: ',pathFrom,' to ',pathTo
                        os.renames(pathFrom,pathTo)
                        fileCount +=1
                    except:
                        print 'Error Moving: ', pathFrom,' to ',pathTo,'--skipped'
                        print sys.exc_info()[0],sys.exc_info()[1]
            if 'image' in extensionList: #jpg,png
                pathTo = os.path.join(folderPathDict['image'],filename)
                if '.jpg' in filename or '.png' in filename:
                    try:
                        print 'Moving: ',pathFrom,' to ',pathTo
                        os.renames(pathFrom,pathTo)
                        fileCount +=1
                    except:
                        print 'Error moving: ', pathFrom,' to ',pathTo,'--skipped'
                        print sys.exc_info()[0],sys.exc_info()[1]
            if 'pdf' in extensionList: #pdf only
                pathTo = os.path.join(folderPathDict['pdf'],filename)
                if '.pdf' in filename:
                    try:
                        print 'Moving: ',pathFrom,' to ',pathTo
                        os.renames(pathFrom,pathTo)
                        fileCount +=1
                    except:
                        print 'Error moving: ', pathFrom,' to ',pathTo,'--skipped'
                        print sys.exc_info()[0],sys.exc_info()[1]
            if 'book' in extensionList: # epub, mobi
                pathTo = os.path.join(folderPathDict['book'],filename)
                if '.epub' in filename or '.mobi' in filename:
                    try:
                        print 'Moving: ',pathFrom,' to ',pathTo
                        os.renames(pathFrom,pathTo)
                        fileCount +=1
                    except:
                        print 'Error moving: ', pathFrom,' to ',pathTo,'--skipped'
                        print sys.exc_info()[0],sys.exc_info()[1]
        else:
            try:
                subDirCounts = selectiveCopy(pathFrom,extensionList,folderPathDict)
                fileCount += subDirCounts
            except:
                print 'Selective moving: Error Diving in directory -> ',pathFrom
                print sys.exc_info()[0],sys.exc_info()[1]
    return (fileCount)

    
def main():
    if menuStyle == False:
        while True:
            if selectiveCopying == False:
                dirTuple = getDirs()
                if dirTuple:
                    print 'starting... \n'
                    start = time.clock()
                    counts = fullDirCopy(*dirTuple)
                    if removeOldDirectory==True:
                        delcounts = fullDirRemove(dirTuple[0])
                        fullDirDelete(dirTuple[0])
                        print ' Copied: ','files: ',counts
                        print ' Deleted: ','files: ',delcounts
            else:
                selectiveTuple = createSelectiveDir()
                if selectiveTuple:
                    print 'starting...\n'
                    start = time.clock()
                    counts = selectiveCopy(*selectiveTuple)
                    if removefiles == True:
                        delcounts = selectiveRemove(selectiveTuple[0],selectiveTuple[1])
                        fullDirDelete(selectiveTuple[0])
                        print 'Copied: ','files: ',counts
                        print 'Deleted: ','files: ',delcounts
            print 'Time taken: ',time.clock() - start, ' seconds'
            looper = raw_input('continue? (q to quit)')
            if looper == 'q': break
    return 0

if __name__ == '__main__':
    main()
