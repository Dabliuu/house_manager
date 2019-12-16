#!/usr/bin/env bash

python  -V # prueba de version, se requiere la 2.7:
sudo apt-get update
sudo pip install --upgrade pip  # actulizar el instalador pip
sudo pip install --upgrade setuptools  # upgrading some tools needed to install the packages
sudo apt-get install qt5-default pyqt5-dev pyqt5-dev-tools
sudo easy_install PySide2  # instala el modulo pyside2
sudo pip install mysql-connector  # intall the mysql module for accesing database (localy and fast)
sudo pip install pyqtgraph  # # install the module PyQtGraph for ploting using pyside or qt
pip install matplotlib # this is for interactive plts in pyqtgraph