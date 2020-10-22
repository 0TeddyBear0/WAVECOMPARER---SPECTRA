import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys
import time

import numpy as np

from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from scipy.io import wavfile
from scipy.fftpack import fft
from scipy import signal
from scipy.io.wavfile import read
from scipy.io.wavfile import read as wavread
import wave


class App(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.w = None
        self.setMinimumSize(QSize(250, 125))
        self.setWindowIcon(QIcon('ico.png'))
        self.title = 'SPECTRA'
        self.setWindowTitle(self.title)

        pybutton = QPushButton('SPECTRUM Analysis', self)
        pybutton.clicked.connect(self.analyzerWin)
        pybutton.resize(200, 30)
        pybutton.move(25, 25)

        pybutton = QPushButton('SPECTRUM Comparer', self)
        pybutton.clicked.connect(self.comparerWin)
        pybutton.resize(200, 30)
        pybutton.move(25, 50)

        pybutton = QPushButton('Info', self)
        pybutton.clicked.connect(self.infoBox)
        pybutton.resize(200, 30)
        pybutton.move(25, 75)

    def analyzerWin(self):
        self.AudioName = self.openFileNameDialog()
        if isinstance(self.AudioName, (bytes, str)) is False:
            self.AudioName = ""
        self.w = analyzer(self.AudioName)
        self.w.show()

    def comparerWin(self):
        self.cmp1 = self.openFileNameDialog()
        if isinstance(self.cmp1, (bytes, str)) is False:
            self.cmp1 = ""

        self.cmp2 = self.openFileNameDialog()
        if isinstance(self.cmp2, (bytes, str)) is False:
            self.cmp2 = ""
        self.w = comparer(self.cmp1, self.cmp2)
        self.w.show()

    def positiveBox(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Gli spettri di queste onde sono uguali!")
        msgBox.setStandardButtons(QMessageBox.Ok)
        returnValue = msgBox.exec()

    def negativeBox(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setText("Gli spettri di queste onde non sono uguali!")
        msgBox.setStandardButtons(QMessageBox.Ok)
        returnValue = msgBox.exec()

    def infoBox(self):
        msgBox = QMessageBox()
        msgBox.setMinimumSize(QSize(300, 300))
        msgBox.setText(
            '<img  src="backg.png"> <p style="text-align:center;">Per contattarci, scrvi una mail al seguente indirizzo:</p> <a href style="text-align:center;">info@tech-time.it</a>'
        )
        msgBox.setStandardButtons(QMessageBox.Ok)
        returnValue = msgBox.exec()

    def legendaBox(self, audiotxt1, audiotxt2):
        msgBox = QMessageBox()
        msgBox.setMinimumSize(QSize(300, 300))
        msgBox.setText(
            '<p> <span style="color:red">&diams; </span><span style="color:cyan">&diams; </span>'+audiotxt1+'</p>' +
            '<p><span style="color:blue">&diams; </span><span style="color:yellow">&diams; </span>'+audiotxt2+'</p>'
        )
        msgBox.setStandardButtons(QMessageBox.Ok)
        returnValue = msgBox.exec()

    def openFileNameDialog(self):
        self.setWindowIcon(QIcon('ico.png'))
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        AudioName, _ = QFileDialog.getOpenFileName(
            self, "SPECTRA - Seleziona un file audio", "", "Audio Files (*.wav);;All Files (*)", options=options)

        if AudioName:
            return AudioName


class analyzer(QtWidgets.QMainWindow):

    def __init__(self, AudioName):
        super().__init__()
        print(AudioName)
        self.setWindowIcon(QIcon('ico.png'))
        self.setWindowTitle("SPECTRA - ANALYZER")
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 1200
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.hide()

        fs, Audiodata = wavfile.read(AudioName)

        self.aly = QtWidgets.QWidget()
        self.setCentralWidget(self.aly)
        layout = QtWidgets.QVBoxLayout(self.aly)

        static_canvas = FigureCanvas(Figure(figsize=(7, 7)))
        layout.addWidget(static_canvas)

        static_canvas2 = FigureCanvas(Figure(figsize=(7, 7)))
        layout.addWidget(static_canvas2)

        static_canvas3 = FigureCanvas(Figure(figsize=(7, 7)))
        layout.addWidget(static_canvas3)

#--------------------------------------------------------------------------------------------------------------

        self._static_ax = static_canvas.figure.subplots()
        self._static_ax.plot(Audiodata, 'r-')
        self._static_ax.set_title('Segnale audio', size=10)

#--------------------------------------------------------------------------------------------------------------

        n = len(Audiodata)
        AudioFreq = fft(Audiodata)
        AudioFreq = AudioFreq[0:int(np.ceil((n+1)/2.0))]
        MagFreq = np.abs(AudioFreq)
        MagFreq = MagFreq / float(n)

        MagFreq = MagFreq**2
        if n % 2 > 0:
            MagFreq[1:len(MagFreq)] = MagFreq[1:len(MagFreq)] * 2
        else:
            MagFreq[1:len(MagFreq) - 1] = MagFreq[1:len(MagFreq) - 1] * 2

        self._static_ax2 = static_canvas2.figure.subplots()
        t2 = np.arange(0, int(np.ceil((n+1)/2.0)), 1.0) * (fs / n)
        self._static_ax2.plot(t2/1000.0, 10*np.log10(MagFreq))
        self._static_ax2.set_title('Frequenza (kHz)', size=10)
        self._static_ax2.set_ylabel('Potenza spettro (dB)')

#--------------------------------------------------------------------------------------------------------------
        N = 512
        f, t, Sxx = signal.spectrogram(Audiodata, fs, nfft=N)

        self._static_ax3 = static_canvas3.figure.subplots()
        self._static_ax3.pcolormesh(t, f, 10*np.log10(Sxx))

        self._static_ax3.set_ylabel('Frequenza [Hz]')
        self._static_ax3.set_title('Tempo [seg]', size=10)
        self.show()


class comparer(QtWidgets.QMainWindow):

    def __init__(self, cmp1, cmp2):

        super().__init__()
        self.app = App()
        self.setWindowIcon(QIcon('ico.png'))

        fs1, Audiodata1 = wavfile.read(cmp1)
        fs2, Audiodata2 = wavfile.read(cmp2)

        if np.array_equiv(Audiodata1, Audiodata2):
            self.app.positiveBox()
        else:
            self.comparedAnalysis(Audiodata1, Audiodata2, fs1, fs2)
            self.app.negativeBox()
            self.app.legendaBox(cmp1, cmp2)

    def comparedAnalysis(self, Audiodata1, Audiodata2, fs1, fs2):
        self.setWindowIcon(QIcon('ico.png'))
        self.setWindowTitle("SPECTRA - ANALYZER")
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 1200
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.hide()

        self.aly = QtWidgets.QWidget()
        self.setCentralWidget(self.aly)
        layout = QtWidgets.QVBoxLayout(self.aly)

        static_canvas1 = FigureCanvas(Figure(figsize=(7, 7)))
        layout.addWidget(static_canvas1)

        static_canvas2 = FigureCanvas(Figure(figsize=(7, 7)))
        layout.addWidget(static_canvas2)

        static_canvas3 = FigureCanvas(Figure(figsize=(7, 7)))
        layout.addWidget(static_canvas3)
#--------------------------------------------------------------------------------------------------------------
        self._static_ax1 = static_canvas1.figure.subplots()

        self._static_ax1.plot(Audiodata1, 'r-', alpha=0.7)
        self._static_ax1.plot(Audiodata2, 'b-', alpha=0.7)
        self._static_ax1.set_title('Segnale audio', size=10)
#--------------------------------------------------------------------------------------------------------------
        n1 = len(Audiodata1)
        n2 = len(Audiodata2)

        AudioFreq1 = fft(Audiodata1)
        AudioFreq2 = fft(Audiodata2)

        AudioFreq1 = AudioFreq1[0:int(np.ceil((n1+1)/2.0))]
        AudioFreq2 = AudioFreq2[0:int(np.ceil((n2+1)/2.0))]

        MagFreq1 = np.abs(AudioFreq1)
        MagFreq2 = np.abs(AudioFreq2)

        MagFreq1 = MagFreq1 / float(n1)
        MagFreq2 = MagFreq2 / float(n2)

        MagFreq1 = MagFreq1**2
        if n1 % 2 > 0:
            MagFreq1[1:len(MagFreq1)] = MagFreq1[1:len(MagFreq1)] * 2
        else:
            MagFreq1[1:len(MagFreq1) - 1] = MagFreq1[1:len(MagFreq1) - 1] * 2

        MagFreq2 = MagFreq2**2
        if n2 % 2 > 0:
            MagFreq2[1:len(MagFreq2)] = MagFreq2[1:len(MagFreq2)] * 2
        else:
            MagFreq2[1:len(MagFreq2) - 1] = MagFreq2[1:len(MagFreq2) - 1] * 2

        self._static_ax2 = static_canvas2.figure.subplots()

        t1 = np.arange(0, int(np.ceil((n1+1)/2.0)), 1.0) * (fs1 / n1)
        t2 = np.arange(0, int(np.ceil((n2+1)/2.0)), 1.0) * (fs2 / n2)

        self._static_ax2.plot(
            t1/1000.0, 10*np.log10(MagFreq1), 'c-', alpha=0.7)
        self._static_ax2.plot(
            t2/1000.0, 10*np.log10(MagFreq2), 'y-', alpha=0.7)

        self._static_ax2.set_title('Frequenza (kHz)', size=10)
        self._static_ax2.set_ylabel('Potenza spettro (dB)')

#--------------------------------------------------------------------------------------------------------------

        N = 512
        f1, t1, Sxx1 = signal.spectrogram(Audiodata1, fs1, nfft=N)

        f2, t2, Sxx2 = signal.spectrogram(Audiodata2, fs2, nfft=N)

        self._static_ax3 = static_canvas3.figure.subplots()

        self._static_ax3.pcolormesh(t1, f1, 10*np.log10(Sxx1))
        self._static_ax3.pcolormesh(t2, f2, 10*np.log10(Sxx2))

        self._static_ax3.set_ylabel('Frequenza [Hz]')
        self._static_ax3.set_title('Tempo [seg]', size=10)

        self.show()


if __name__ == '__main__':
    qapp = QtWidgets.QApplication(sys.argv)
    app = App()
    app.show()
    sys.exit(qapp.exec_())
