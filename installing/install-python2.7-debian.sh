#!/usr/bin/env bash

python  -V # prueba de version, se requiere la 2.7:
sudo pip install --upgrade pip  # actulizar el instalador pip
sudo pip install --upgrade setuptools  # upgrading some tools needed to install the packages
sudo apt-get install build-essential git cmake libqt4-dev libphonon-dev python2.7-dev libxml2-dev libxslt1-dev qtmobility-dev libqtwebkit-dev # required to install pyside
sudo easy_install PySide  # instala el modulo pyside1
sudo pip install mysql-connector  # intall the mysql module for accesing database (localy and fast)
sudo pip install pyqtgraph  # # install the module PyQtGraph for ploting using pyside or qt
pip install matplotlib # this is for interactive plts in pyqtgraph


