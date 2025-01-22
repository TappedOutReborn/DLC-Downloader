# DLC-Downloader
DLC Downloader for The Simpsons: Tapped Out. It takes a while to download everything, so be patient.

## Usage
You will need about 30GB of free storage, and [python3](https://www.python.org) installed.
```
python3 downloadDlcs.py
```

## Configuration
If you want to for example change the language of dlcs the script downloads, you can do so at the top of the script.
```python
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

ALL_LANGUAGES = True # Download the dlcs in every languages
ALL_TIERS = True # Download the dlcs in every tier
```
