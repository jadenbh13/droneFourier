import PySimpleGUI as sg
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
from fourierBackup import timeToFreq
import math
from topographical import skim
from scipy import signal


_VARS = {'window': False,
         'stream': False,
         'fig_agg': False,
         'pltFig': False,
         'xData': False,
         'yData': False,
         'audioData': np.array([])}

AppFont = 'Any 16'
sg.theme('DarkTeal2')
layout = [[sg.Canvas(key='figCanvas')],
          [sg.ProgressBar(4000, orientation='h',
                          size=(60, 20), key='-PROG-')],
          [sg.Button('Listen', font=AppFont),
           sg.Button('Stop', font=AppFont, disabled=True),
           sg.Button('Exit', font=AppFont)]]
_VARS['window'] = sg.Window('Microphone Waveform Pyplot',
                            layout, finalize=True,
                            location=(400, 100))


CHUNK = 1024
RATE = 44100
INTERVAL = 1
TIMEOUT = 10
pAud = pyaudio.PyAudio()
lx = 0
initialTime = time.time()
recTime = 0
finalTime = 0

allX = []
allY = []

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def drawPlot():
    _VARS['pltFig'] = plt.figure()
    plt.plot(_VARS['xData'], _VARS['yData'], '--k')
    plt.ylim(-4000, 4000)
    _VARS['fig_agg'] = draw_figure(
        _VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])

duration = 1
start = 5

def updatePlot(data):
    _VARS['fig_agg'].get_tk_widget().forget()
    plt.cla()
    plt.clf()
    print((time.time() - recTime))
    if lx == 0 and (time.time() - recTime) > start and (time.time() - recTime) < (start + duration):
        print("Recording")
        for axsMng in data:
            allY.append(axsMng)
    plt.plot(_VARS['xData'], data, '--k')
    plt.ylim(-4000, 4000)
    _VARS['fig_agg'] = draw_figure(
        _VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])


def writeFiles(file1, file2, file3, list1, list2, list3):
    filexr = open(file1,"w")
    filexr.close()
    fileyr = open(file2,"w")
    fileyr.close()
    fileangr = open(file3,"w")
    fileangr.close()
    for lb in range(0, len(list1)):
        with open(file1, "a") as file_object:
            file_object.write(str(list1[lb]) + '\n')
        with open(file2, "a") as file_object:
            file_object.write(str(list2[lb]) + '\n')
        with open(file3, "a") as file_object:
            file_object.write(str(list3[lb]) + '\n')

def stop():
    if _VARS['stream']:
        _VARS['stream'].stop_stream()
        _VARS['stream'].close()
        _VARS['window']['-PROG-'].update(0)
        _VARS['window'].FindElement('Stop').Update(disabled=True)
        _VARS['window'].FindElement('Listen').Update(disabled=False)


def callback(in_data, frame_count, time_info, status):
    _VARS['audioData'] = np.frombuffer(in_data, dtype=np.int16)
    return (in_data, pyaudio.paContinue)


def listen():
    _VARS['window'].FindElement('Stop').Update(disabled=False)
    _VARS['window'].FindElement('Listen').Update(disabled=True)
    _VARS['stream'] = pAud.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=RATE,
                                input=True,
                                frames_per_buffer=CHUNK,
                                stream_callback=callback)

    _VARS['stream'].start_stream()


plt.style.use('ggplot')
_VARS['xData'] = np.linspace(0, CHUNK, num=CHUNK, dtype=int)
_VARS['yData'] = np.zeros(CHUNK)
drawPlot()


while True:
    event, values = _VARS['window'].read(timeout=TIMEOUT)
    if (time.time() - recTime) >= (start + duration) and recTime != 0:
        lx += 1
        stop()
        pAud.terminate()
        break
    if event == sg.WIN_CLOSED or event == 'Exit':
        stop()
        pAud.terminate()
        break
    if event == 'Listen':
        listen()
        recTime = time.time()
    elif event == 'Stop':
        stop()
    elif _VARS['audioData'].size != 0:
        _VARS['window']['-PROG-'].update(np.amax(_VARS['audioData']))
        updatePlot(_VARS['audioData'])

_VARS['window'].close()

divNum = 4

realX = []
realY = []

for uy in range(0, len(allY)):
    if (uy % divNum) == 0:
        realTime = uy / RATE
        realX.append(uy)
        realY.append(allY[uy])

fourds = timeToFreq(realX, realY, (RATE / divNum))
fourierX = []
fourierY = []
phaseAngles = []
for ub in range(0, len(fourds[0])):
    if ub < (len(fourds[0]) / divNum) and fourds[0][ub] > 20:
        fourierX.append(fourds[0][ub])
        fourierY.append(fourds[1][ub])
        phaseAngles.append(fourds[2][ub])



allX = "allX.txt"
allY = "allY.txt"
allPhase = "allPhase.txt"

writeFiles(allX, allY, allPhase, fourierX, fourierY, phaseAngles)

equal = max(fourierX) / 25

arangeList = np.arange(0, max(fourierX), 150)
arangeList2 = np.arange(0, max(fourierX), equal)

topX = []
topY = []
closestPointsX = []
closestPointsY = []
closestAngles = []

for iun in range(0, (len(arangeList) - 1)):
    xF = []
    yF = []
    for ing in range(0, len(fourierX)):
        if arangeList[iun] < fourierX[ing] < arangeList[iun + 1]:
            xF.append(fourierX[ing])
            yF.append(fourierY[ing])
    middleX = min(xF) + ((max(xF) - min(xF)) / 2)
    #closestIndex = closePoint(fourierX, fourierY, middleX, max(yF))
    closestIndex = fourierY.index(max(yF))
    closestPointsX.append(middleX)
    closestPointsY.append(fourierY[closestIndex])
    closestAngles.append(phaseAngles[closestIndex])
    topX.append(middleX)
    topY.append(max(yF))

topX2 = []
topY2 = []
phase2 = []
for iui in range(0, (len(arangeList2) - 1)):
    xFs = []
    yFs = []
    for ink in range(0, len(fourierX)):
        if arangeList2[iui] < fourierX[ink] < arangeList2[iui + 1]:
            xFs.append(fourierX[ink])
            yFs.append(fourierY[ink])
    middleX = min(xFs) + ((max(xFs) - min(xFs)) / 2)
    closestIndex = fourierY.index(max(yF))
    phase2.append(phaseAngles[closestIndex])
    topX2.append(middleX)
    topY2.append(max(yFs))


#sk = skim(fourierX, fourierY)
#plt.scatter(realX, realY, s=5, color='red')
#print(len(allY) / CHUNK)
print("   ")
print(fourierX[fourierY.index(max(fourierY))])
print(max(fourierX))

writeFiles('normX.txt', 'normY.txt', 'normPhase.txt', topX2, topY2, phase2)

fig, axs = plt.subplots(3)
#plt.plot(allY)
axs[0].scatter(realX, realY, color="blue", s=8)
axs[1].scatter(topX2, topY2, color="green", s=8)
axs[2].scatter(fourierX, fourierY, color="red", s=8)
#plt.plot(allY, color="blue")
plt.show()
