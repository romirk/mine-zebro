import json
import os

LOCAL_FOLDER ="/home/pi/local"
GLOBAL_FOLDER="/home/pi/global"

SETTINGS={}

VERBOSE=True

for folder in (GLOBAL_FOLDER,LOCAL_FOLDER):
    try: #load settings
        with open(os.path.join(folder,"settings.json"),"r") as f:
            if VERBOSE:
                new=json.load(f)
                SETTINGS.update(new)
                print("Loaded settings:",new.keys())
            else:
                SETTINGS.update(json.load(f))
    except FileNotFoundError: #if settings file is missing, create one
        print("Settings missing, creating settings file")
        with open(os.path.join(folder,"settings.json"),"w") as f:
            json.dump({},f)
