import csv
import time
import sounddevice as sd
from scipy.io.wavfile import write
from sklearn import tree
import pandas as pd
import numpy
import requests
from oocsi import OOCSI
import pythoncom
import threading
import tkinter
import os
mysp = __import__("my-voice-analysis")

URL = "https://data.id.tue.nl/datasets/entity/1687/item/"
downloadUrl = "https://data.id.tue.nl/datasets/downloadPublic/GsM3kvz4WIpCGfJXZ5sNUVXoL4GSMRtruErw8PobRgdtdEbNXxOscgh+rLXSJecr"

# path could be modified
file = "analysis"
c = r"C:\Users\LENOVO\Desktop\PRAISE\venv\Scripts\soundfiles"

fs = 44100
seconds = 10.0
currentFileNumber = 0

atcRate = 0
f0range = 0
pause = 0
mood = 0

dataSets = []
presentationStatus = True


def endPresentation():
    global presentationStatus
    presentationStatus = False


def createButton():
    top = tkinter.Tk()
    endButton = tkinter.Button(text="Presentation is over", command=endPresentation)
    endButton.pack()
    top.mainloop()


# Start the button control in another thread so that it doesn't affect the main loop
t = threading.Thread(target=createButton)
t.start()

while presentationStatus:
    filePath = file + str(currentFileNumber)
    myRecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()
    write(c + '/' + filePath + '.wav', fs, myRecording)
    currentFileNumber += 1

for number in range(0, currentFileNumber):
    filePath = file + str(number)
    atcRate = mysp.myspatc(filePath, c)
    f0min = mysp.myspf0min(filePath, c)
    f0max = mysp.myspf0max(filePath, c)
    pause = mysp.mysppaus(filePath, c)
    mood = mysp.myspgend(filePath, c)

    f0range = f0max - f0min

    dataSet = [number, atcRate, f0range, pause, mood]
    dataSets.append(dataSet)

    HEADERS = {
        'api_token': 'CYW0tdu5ZnuV2RG25h/O4gNCbhC6n0XcbQI5gLJDh32mXnHPY3eq9+KKHprgRBuX',
        'resource_id': str(number),
        'token': "1234"
    }
    
    PARAMS = {
        "time-stamp": str(number * 60),
        "articulationRate": atcRate,
        "f0Range": f0range,
        "pause": pause,
        "mood": mood
    }

    # send the speech data
    r = requests.put(url=URL, headers=HEADERS, json=PARAMS)


# download the integrated datasets (path need to be personally modified)
downloadData = requests.get(downloadUrl)
with open(os.path.join(r"C:\Users\LENOVO\Desktop\PRAISE\venv\Scripts", "overallData.csv"), "wb") as f:
    f.write(downloadData.content)
trainingData = pd.read_csv(r"C:\Users\LENOVO\Desktop\PRAISE\venv\Scripts\overallData.csv")
relevantFeatures = ["articulationRate", "F0Range", "fillerWords", "speechMode"]
feature = trainingData[relevantFeatures]
target = trainingData["engagementLevel"]

model = tree.DecisionTreeClassifier()
model = model.fit(feature, target)
# learning finished, rank the importances of the features
importances = model.feature_importances_
importanceDict = {"articulationRate": importances[0], "F0Range": importances[1], "fillerWords": importances[2],
                  "speechMode": importances[3]}
rankedDict = sorted(importanceDict.items(), key=lambda x: x[1], reverse=True)
print(importances)
print(rankedDict[0][0])
print(rankedDict[1][0])

# send the oocsi message
oocsi = OOCSI('Praise', 'oocsi.id.tue.nl')
importantFeatures = {
    "FirstFeature": rankedDict[0][0],
    "SecondFeature": rankedDict[1][0]
}
oocsi.send('PraiseDiscussion', importantFeatures)
