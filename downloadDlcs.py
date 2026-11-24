import xml.etree.ElementTree as ET

from requests import get

from colorama import Fore

from time import sleep

import os, io, zipfile

OUT_DIR = "./dlc"  # Directory where the dlc files will be downloaded
LANGUAGE = [
        "all", 
        "en"
]  # en,fr,it,de,es,ko,zh,cn,pt,ru,tc,da,sv,no,nl,tr,th

TIER = [
    "all",
    "25",
    "50",
    "100",
    "retina",
    "iphone",
    "ipad",
    "ipad3",
    "mp3",
    "caf",
    "wav",
]  # 25,50,100,retina,iphone,ipad,ipad3,mp3,caf,wav

ALL_LANGUAGES = True    # Download the dlcs in every languages
ALL_TIERS = True        # Download the dlcs in every tier

BASE_URL = "http://oct2018-4-35-0-uam5h44a.tstodlc.eamobile.com/netstorage/gameasset/direct/simpsons/"

DOWNLOAD_QUEUE = []  # [ Url, Filename, Folder ]
DOWNLOADED = []


def log(severity: int, message: str):
    if severity == 0:
        print(Fore.BLUE + "[i] " + Fore.WHITE + message)
    elif severity == 1:
        print(Fore.YELLOW + "[!] " + Fore.WHITE + message)
    elif severity == 2:
        print(Fore.RED + "[!] " + Fore.WHITE + message)
    else:
        print(Fore.WHITE + message)


def downloadFile(url: str, filename: str):
    os.makedirs(OUT_DIR, exist_ok=True)
    filepath = os.path.join(OUT_DIR, filename)

    # skipping already downloaded files
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        # reading the index for comparison with the archive
        if "Index" in filename or filename.endswith(".xml"):
            with open(filepath, "rb") as existingFile:
                return existingFile.read()
        return None

    # file downloading with retries after connection error
    while True:
        try:
            response = get(url)
            if not response.status_code == 200:
                log(1, f"Non 200 response ({response.status_code}). Skipping... ({url})")
                return None

            data = response.content

            log(0, f"Downloaded {filename} ({len(data)} bytes).")
            with open(filepath, "wb+") as outFile:
                outFile.write(data)

            return data

        except Exception as e:
            log(1, f"Connection error ({e}). Retrying {filename} in 5 seconds...")
            sleep(5)



def getDLCIndexXml(url: str, filename: str):
    zippedFileData = downloadFile(url, filename)
    if not zippedFileData:
        return

    with zipfile.ZipFile(io.BytesIO(zippedFileData)) as z:
        data = z.read(z.infolist()[0])
        return data


def getDLCIndexes():
    log(0, "Getting DLC Indexes...")
    try:
        os.makedirs(OUT_DIR + "/dlc", exist_ok=True)
        masterIndex = getDLCIndexXml(BASE_URL + "dlc/DLCIndex.zip", "dlc/DLCIndex.zip")
        if not masterIndex:
            return []

        tree = ET.fromstring(masterIndex)
        lst = tree.findall("./IndexFile")
        return [item.get("index").replace(":", "/") for item in lst]

    except ET.ParseError as e:
        log(2, f"Failed to parse XML: {e}")
        return []


class DLCIndexParser(ET.XMLParser):
    def start(self, tag, attrs):
        if tag == "Package":
            self.tier = attrs["tier"]

            self.LocalDir = ""
            self.FileSize = ""
            self.UncompressedFileSize = ""
            self.IndexFileCRC = ""
            self.IndexFileSig = ""
            self.Version = ""
            self.FileName = ""
            self.Language = ""

        if tag == "LocalDir":
            self.LocalDir = attrs["name"]
        elif tag == "FileSize":
            self.FileSize = attrs["val"]
        elif tag == "UncompressedFileSize":
            self.UncompressedFileSize = attrs["val"]
        elif tag == "IndexFileCRC":
            self.IndexFileCRC = attrs["val"]
        elif tag == "IndexFileSig":
            self.IndexFileSig = attrs["val"]
        elif tag == "Version":
            self.Version = attrs["val"]
        elif tag == "FileName":
            self.FileName = attrs["val"]
        elif tag == "Language":
            self.Language = attrs["val"]

    def end(self, tag):
        if tag == "Package":
            return

        if self.tier == "" or self.Language == "":
            return

        if self.Language not in LANGUAGE and not ALL_LANGUAGES:
            return
        if self.tier not in TIER and not ALL_TIERS:
            return

        DOWNLOAD_QUEUE.append(
            [
                BASE_URL + self.FileName.replace(":", "/"),
                self.FileName.split(":")[-1],
                self.FileName.split(":")[0],
            ]
        )  # So i can download them later

    def data(self, data):
        pass

    def close(self):
        pass


if __name__ == "__main__":
    indexes = getDLCIndexes()

    # Process Data (Get Urls)
    for index in indexes:
        try:
            dlcIndexXml = getDLCIndexXml(BASE_URL + index, "dlc/" + index.split("/")[1])
            if not dlcIndexXml:
                continue

            parser = ET.XMLParser(target=DLCIndexParser())
            parser.feed(dlcIndexXml)
            parser.close()

            log(0, f"Processed {index}")
        except ET.ParseError as e:
            log(2, f"Failed to parse XML for index {index}: {e}")

    # Download Dlcs
    for download in DOWNLOAD_QUEUE:
        if download[0] in DOWNLOADED:
            continue

        os.makedirs(
            OUT_DIR + "/" + download[2], exist_ok=True
        )  # Make dlc subdirectory if it doesn't exist
        downloadFile(download[0], download[2] + "/" + download[1])

        DOWNLOADED.append(
            download[0]
        )  # So it doesn't download the same file multiple times
