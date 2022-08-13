import os
import sys
import requests
import json

APIKey = ""

videoLink = ""
title = ""

def validLinkArg():
    global videoLink
    videoLink = str(sys.argv[1:][0])

    validation = videoLink.find("youtube.com/watch?v=")
    if validation == -1:
        return False
    return True
def getVideoID(link):
    pos = link.find("watch?v=")
    if pos == -1:
        return ""
    pos += 8

    videoID = ""
    for i in link[pos:]:
        if i == '&':
            break
        videoID += i
    return videoID

def createVideoInformationsURL(videoID):
    keyedUrl = "https://www.googleapis.com/youtube/v3/videos?key="+APIKey+"&part=snippet&id="+videoID
    return keyedUrl
def createVideoRatingURL(videoID):
    keyedUrl = "https://returnyoutubedislikeapi.com/votes?videoId="+videoID
    return keyedUrl
def createFirstCommentsURL(videoID):
    keyedUrl = "https://www.googleapis.com/youtube/v3/commentThreads?key="+APIKey+"&part=snippet, replies&videoId="+videoID+"&order=relevance&maxResults=100"
    return keyedUrl
def createThumbnailURL(videoID):
    keyedUrl = "https://img.youtube.com/vi/"+videoID+"/maxresdefault.jpg"
    return keyedUrl

def sendUrlRequest(urlRequest):
    data = requests.get(urlRequest)
    return data.json()

def getVideoInformations(urlRequest):
    reqData = sendUrlRequest(urlRequest)
    result = reqData["items"][0]

    return result
def getVideoRating(urlRequest):
    reqData = sendUrlRequest(urlRequest)
    return reqData
def getAllComments(urlRequest):
    reqData = sendUrlRequest(urlRequest)

    baseURL = str(urlRequest)
    itemsArray = []
    while True:
        currentItem = reqData["items"]
        for i in currentItem:
            itemsArray.append(i)

        if "nextPageToken" in reqData:
            urlRequest = baseURL + "&pageToken=" + reqData["nextPageToken"]
            reqData = sendUrlRequest(urlRequest)
        else:
            break
    return itemsArray

def getCommentsCountFromArray(comments):
    count = len(comments)
    return count
def getThumbnailURL(urlRequest):
    imageData = requests.get(urlRequest)
    return imageData.content


def getTitleFromVideoInformations(videoInformations):
    title = videoInformations["snippet"]["title"]
    return title

def transformDataToJson(informations, ratings, commentsCount, comments):
    videoDump = """"informations":"""+json.dumps(informations)
    ratingsDump = """"ratings":"""+json.dumps(ratings)
    commentsCount = """"commentsCount":"""+json.dumps(commentsCount)
    commentsDump = """"comments":"""+json.dumps(comments)


    completeJson = "{"+videoDump+", "+ratingsDump+", "+commentsCount+","+commentsDump+"}"
    return completeJson

class nameCreator:
    def __normalizeFileName(self, fileName):
        validchars = "-_.() "
        out = ""
        for c in fileName:
            if str.isalpha(c) or str.isdigit(c) or (c in validchars):
                out += c
            else:
                out += "_"
        return out

    def __createPathName(self, name):
        global title
        pathName = title + name
        pathName = self.__normalizeFileName(pathName)
        return pathName

    def createDictionaryName(self):
        dictionaryName = self.__createPathName(" - Data")
        return dictionaryName
    def createFileName(self):
        fileName = self.createDictionaryName()+"/"+self.__createPathName(" - DataAndComments.json")
        return fileName
    def createThumbnailName(self):
        thumbnailName = self.createDictionaryName()+"/"+self.__createPathName("- Thumbnail.jpg")
        return thumbnailName

class fileSaving:

    def __init__(self, jsonData, thumbnailData):
        self.__jsonData = jsonData
        self.__thumbnailData = thumbnailData
        self.__nc = nameCreator()

    def createFilesContainer(self):
        folderName = self.__nc.createDictionaryName()
        if os.path.exists(folderName) == False:
            os.mkdir(folderName)

    def saveDataToFile(self):
        fileName = self.__nc.createFileName()
        file = open(fileName, "w")
        file.write(self.__jsonData)
        file.close()

    def saveThumbnail(self):
        thumbnailName = self.__nc.createThumbnailName()
        thumbnail = open(thumbnailName, "wb")
        thumbnail.write(self.__thumbnailData)
        thumbnail.close()

def downloadCommentsAndInfo():
    ID = getVideoID(videoLink)

    reqInfo = createVideoInformationsURL(ID)
    informations = getVideoInformations(reqInfo)

    global title
    title = getTitleFromVideoInformations(informations)

    reqRatings = createVideoRatingURL(ID)
    rating = getVideoRating(reqRatings)

    reqComments = createFirstCommentsURL(ID)
    comments = getAllComments(reqComments)

    commentsCount = getCommentsCountFromArray(comments)

    reqThumbnils = createThumbnailURL(ID)
    thumbnail = getThumbnailURL(reqThumbnils)


    json = transformDataToJson(informations, rating, commentsCount, comments)

    fs = fileSaving(json, thumbnail)
    fs.createFilesContainer()
    fs.saveDataToFile()
    fs.saveThumbnail()

def configurationPreperations():
    global APIKey
    if(os.path.exists('config.txt') == False):
        APIKey = input("Please specify your API Key: ")
        print("If you want to check your API Key please edit config file by parsing key in this file")

        APIKeyFileWriter = open("config.txt", "w")
        APIKeyFileWriter.write(APIKey)
    else:
        apiKeyFile = open("config.txt", "r")
        APIKey = apiKeyFile.readline()

def main():
    argumentCount = len(sys.argv[1:])

    if argumentCount == 0:
        print("No links given!")
    elif argumentCount == 1:
        linkValidation = validLinkArg()

        if linkValidation == False:
            print(sys.argv[1:][0]+" is not valid URL!")
            return

        downloadCommentsAndInfo()
    else:
        print("Bad Arguments given!")


if __name__ == "__main__":
    configurationPreperations()
    main()