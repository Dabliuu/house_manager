#!/usr/bin/env bash

python  -V
python -m pip install --upgrade pip
pip3 install --upgrade setuptools


#for python 3.6 in windows do:
pip3 install PyQt5
pip3 install PySide2
python -m pip install --user numpy scipy matplotlib ipython jupyter pandas sympy nose
pip3 install MySQL-connector-python
#pip install mysql-connector
pip3 install pyqtgraph

#for audio recording
pip3 install pyaudio

#for python 3.4 in windows do:
#finde .exex to install PySide
python -m pip install --user numpy scipy matplotlib ipython jupyter pandas sympy nose
pip3 install pyqtgraph
