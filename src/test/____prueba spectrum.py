import numpy as np


#import PyQt5 as Qt
import pyqtgraph as pg


import struct
import pyaudio
from scipy.fftpack import fft

import sys
import time

import matplotlib.pyplot as plt

class AudioStream(object):
    def __init__(self):

        # pyqtgraph stuff
        pg.setConfigOptions(antialias=True)
        self.traces = dict()
        self.app = pg.QtGui.QApplication(sys.argv)
        self.win = pg.GraphicsWindow(title='Spectrum Analyzer')
        self.win.setWindowTitle('Spectrum Analyzer')
        self.win.setGeometry(5, 115, 1910, 1070)

        # x labels for signal
        wf_xlabels = [(0, '0'), (512, '512'), (1024, '1024')]
        wf_xaxis = pg.AxisItem(orientation='bottom')
        wf_xaxis.setTicks([wf_xlabels])

        # y labels for signal
        wf_ylabels = [(-32768, "-32768"),(-16000,"-16000"),(0, '0'), (16000, '16000'), (32767, '32767')]
        wf_yaxis = pg.AxisItem(orientation='left')
        wf_yaxis.setTicks([wf_ylabels])

        # x label for furier
        sp_xlabels = [(0, '0'), (1000, "1000"),(4000, '4000'), (10000,"10000"), (22050, '22050')]
        sp_xaxis = pg.AxisItem(orientation='bottom')
        sp_xaxis.setTicks([sp_xlabels])

        # automatic labels on furiers y plot

        self.waveform = self.win.addPlot(
            title='WAVEFORM', row=1, col=1, axisItems={'bottom': wf_xaxis, 'left': wf_yaxis},
        )
        self.spectrum = self.win.addPlot(
            title='SPECTRUM', row=2, col=1, axisItems={'bottom': sp_xaxis},
        )

        # pyaudio stuff
        self.FORMAT = pyaudio.paInt16
        self.nBytes = 2
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            #output=True, # no need to use the speakers
            frames_per_buffer=self.CHUNK,
        )
        # waveform and spectrum x points
        self.x = np.arange(self.CHUNK) # create a vector array for the x points of the waveform: (0,2,4,..2046,2048)
        #self.f = np.linspace(0, self.RATE / 2, self.CHUNK / 2) # create a vector array from 0 to 22050 with 512 points (0,2,4,..2046,2048)
        self.f = np.fft.rfftfreq(self.CHUNK) * self.RATE
        print("pasó")

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(pg.QtCore, 'PYQT_VERSION'):
            pg.QtGui.QApplication.instance().exec_()

    def set_plotdata(self, name, data_x, data_y):
        if name in self.traces:
            self.traces[name].setData(data_x, data_y)
        else:
            if name == 'waveform':
                self.traces[name] = self.waveform.plot(pen='r', width=5)
                self.waveform.setYRange(-32768, 32767, padding=0)
                self.waveform.setXRange(0, self.CHUNK, padding=0.005)
            if name == 'spectrum':
                self.traces[name] = self.spectrum.plot(pen='g', width=5)
                self.spectrum.setYRange(-10, 32767, padding=0)
                self.spectrum.setXRange(
                    0, self.RATE/2, padding=0.005)

    def update(self):
        wf_data = self.stream.read(self.CHUNK) # t this pint it is only represented by bytes in /0xFF form
        # print(wf_data)
        # print(len(wf_data))

        wf_data = np.fromstring(wf_data, dtype=np.int16)
        #wf_data = struct.unpack(str(2 * self.CHUNK) + 'B', wf_data) # now they are integer values that represent each byte as UNSIGNED BYTE 'B'
        #wf_data = np.array(wf_data, dtype='b')[::2]

        """
        # for debugging porpouse
        print(wf_data)
        print(len(wf_data))
        fig, ax = plt.subplots()
        ax.plot(wf_data)
        plt.show()
        sys.exit(1)
        """

        self.set_plotdata(name='waveform', data_x=self.x, data_y=wf_data,)

        sp_data = np.fft.rfft(np.array(wf_data, dtype=np.int16)) #get rid of the offset
        sp_data = np.abs(sp_data) / 100 # divide by 100 for normalization proposes

        """
        # for debugging porpouse
        print(wf_data)
        print(len(wf_data))
        fig, ax = plt.subplots()
        ax.plot(self.f,sp_data)
        plt.show()
        sys.exit(1)
        """

        self.set_plotdata(name='spectrum', data_x=self.f, data_y=sp_data)

    def animation(self):
        timer = pg.QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(20)
        self.start()


if __name__ == '__main__':

    audio_app = AudioStream()
    audio_app.animation()