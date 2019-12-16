
import sys



import functools
import sys
import traceback
import logging

logging.basicConfig(level=logging.DEBUG) # this will set all the debugging messages on


# for gui tools:
# from PySide2 import QtCore
# from PySide2 import QtGui
# from PySide2.QtCore import *
# from PySide2.QtGui import *
# from PySide2.QtUiTools import *
# from PySide2.QtUiTools import *
# from PySide2 import QtUiTools

from PyQt5 import QtWidgets, uic, QtGui, QtCore 

# aditional tools:
from functools import partial  # para facilitar el manejo de eventos

from Plot2D import Plot2D
from ControlScreen import ControlScreen
from MeasureScreen import MeasureScreen
from ConfigScreen import ConfigScreen

class View(QtCore.QObject):  # hereda de la clase QtGui.QmainWindow

    def __init__(self, controller, config):

        # ------------basic configuration:------------------

        super(View, self).__init__(parent=None)  # initialize the parent class (QtGui)
        self.controller = controller
        self.currentConfig = config

        self.window = QtWidgets.QMainWindow()


        # load ui file:
        uic.loadUi("./src/uifiles/mainwindow_proyecto1.ui", self.window)

        # window configuration:
        self.window.setWindowIcon(QtGui.QIcon("./src/icons/logo_n.png"))  # el punto significa el lugar donde esta el script
        self.window.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)  # transparent background
        self.window.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # borderless

        # Add de event handlers to de menu objects
        self.window.appsBt.clicked.connect(partial(self.menu_handler, self.window.appsBt))
        self.window.configBt.clicked.connect(partial(self.menu_handler, self.window.configBt))
        self.window.userBt.clicked.connect(partial(self.menu_handler, self.window.userBt))
        self.window.closeBt.clicked.connect(partial(self.menu_handler, self.window.closeBt))

        # add all menu buttons to search and managment:
        self.my_menu_bt = [
            self.window.appsBt,
            self.window.configBt,
            self.window.userBt,
            self.window.closeBt
        ]

        # add all button apps to search and managment:
        self.my_apps_bt = [
            self.window.CHHome,
            self.window.CHGraphics,
            self.window.CHControl,
            self.window.CHSustainability,
            self.window.Inelca_Bifasic_Measure
        ]

        # Add de event handlers to de app objects
        self.window.CHHome.clicked.connect(partial(self.app_handler, self.window.CHHome))
        self.window.CHGraphics.clicked.connect(partial(self.app_handler, self.window.CHGraphics))
        self.window.CHControl.clicked.connect(partial(self.app_handler, self.window.CHControl))
        self.window.CHSustainability.clicked.connect(partial(self.app_handler, self.window.CHSustainability))
        self.window.Inelca_Bifasic_Measure.clicked.connect(
            partial(self.app_handler, self.window.Inelca_Bifasic_Measure))

        # configure interactions in user interface:
        self.window.logg_in.clicked.connect(partial(self.user_handler, self.window.logg_in))
        

        # Set up the user page as first page
        self.window.stacked_views.setCurrentIndex(0)  # 0 for apps
        self.window.appsBt.setProperty('is_on', True)  # modifico la propiedad
        self.window.appsBt.setStyle(self.window.appsBt.style())  # actualizo la modificacion
        self.menu_last_pressed = self.window.appsBt

        # Set up the home page as default app view
        self.window.stacked_apps.setCurrentIndex(0)  # 0 for home)
        self.window.CHHome.setProperty('is_on', True)  # modifico la propiedad
        self.window.CHHome.setStyle(self.window.CHHome.style())  # actualizo la modificacion
        self.app_last_pressed = self.window.CHHome

        # --------- configuring Apps-------------

        # the config screen
        self.myConfigScreen = ConfigScreen(self, config)

        # home

        # the controll app:
        self.myControlScreen = ControlScreen(self)

        #the measure app:
        self.myMeasureScreen = MeasureScreen(self)

        self.window.show()
        print("view init done!")


    def user_handler(self, object_event):
        self.controller.myModel.autenticate_user()

    # necessary for pyside1
    def closeEvent(self, event):
        
        print("Closing the app")
        

        self.deleteLater()
        

    def menu_handler(self, bt_seleccionado):

        index = 0
        for button in self.my_menu_bt:
            if button == bt_seleccionado:
                button.setProperty('is_on', True)  # modifico la propiedad
                button.setStyle(button.style())  # actualizo la modificacion
                self.window.stacked_views.setCurrentIndex(index)  # becouse its ordered it works
            else:
                button.setProperty('is_on', False)
                button.setStyle(button.style())  # actualizo la modificacion
            index += 1  # add one
        if bt_seleccionado == self.window.closeBt:

            # close the sub program threads peacefully
            # self.controller.sd_controller.stop()
            # self.controller.myModel.myDatabaseManager.connection_verifier.stop()
            # apagar el plotter: self.my_plot.timer.stop()
            #self.controller.fast_routine.stop()

            # exit the main thread

            self.controller.myModel.XbeeGrid.end()
            sys.exit(0)

    # event handlers:
    def app_handler(self, bt_seleccionado):

        index = 0
        for button in self.my_apps_bt:
            if button == bt_seleccionado:
                button.setProperty('is_on', True)  # modifico la propiedad
                button.setStyle(button.style())  # actualizo la modificacion
                self.window.stacked_apps.setCurrentIndex(index)  # becouse its ordered it works
            else:
                button.setProperty('is_on', False)
                button.setStyle(button.style())  # actualizo la modificacion
            index += 1  # add one


# graphic functions:
def set_progress(progress_bar_, percentage):
    if percentage <= 30:
        print("menor a 30")
        value = "one"
    elif 50 >= percentage > 30:
        print("entre 50 y 30")
        value = "two"
    elif 80 >= percentage > 50:
        print("entre 80 y 50")
        value = "three"
    elif percentage > 80:
        print("mayor a 80")
        value = "four"

    print(progress_bar_.setProperty('p_val', value))  # modifico la propiedad
    progress_bar_.setStyle(progress_bar_.style())  # actualizo la modificacion
    progress_bar_.setValue(percentage)
