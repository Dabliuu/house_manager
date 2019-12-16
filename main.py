
#   _______________________________________________________________________________________
#  || - - - - - - - - - - - ||            |                                               ||
#  || - - ||||||||||||\ - - ||   AUTHOR:  |  Juan David Ramirez                           ||
#  || - - - ||| |||- ||| - -||____________|_______________________________________________||
#  || - - - ||| |||- ||| - -||            |                                               ||
#  || - - - ||| ||||||/ - - ||     DATE:  |  Junio de 2019                                ||
#  || - - - ||| - - - - - - ||____________|_______________________________________________||
#  || - - - ||| ||||||\ - - ||            |                                               ||
#  || - - - ||| |||- ||| - -||   E-MAIL:  |  juan.ramirez.villegas@correounivalle.edu.co  ||
#  || - - - ||| ||||||/ - - ||____________|_______________________________________________||
#  || - - -|||| |||- ||\ - -||                                                            ||
#  || -|||||| - - - - - - - ||               * * * * USE WISELY * * * *                   ||                                   
#  || - - - - - - - - - - - ||____________________________________________________________||                                                             
#  ****************************************************************************************

import sys
import logging
import os


sys.path.append(os.path.abspath("./src/control"))
sys.path.append(os.path.abspath("./src/view"))
sys.path.append(os.path.abspath("./src/model"))


from controllers import Controller
from models import Model
from views import View

from PyQt5 import QtWidgets 
import json

#custom qt widgets (chek box):    http://doc.qt.io/archives/qt-4.8/stylesheet-examples.html
#                                 https://doc.qt.io/archives/qq/qq20-qss.html
#                                 https://stackoverflow.com/questions/40672817/how-to-make-color-for-checked-qradiobutton-but-looks-like-standard
#                                 http://doc.qt.io/qt-5/stylesheet-examples.html

CONFIG_FILE_ROUTE = os.path.abspath("./config.json")
logging.basicConfig(level=logging.DEBUG) # this will set all the debugging messages on

def main():

    # reload(sys)
    # sys.setdefaultencoding('utf8')

    app = QtWidgets.QApplication(sys.argv)
    
    #Read JSON data into the datastore variable
    try:
        with open(CONFIG_FILE_ROUTE, 'r') as f:
            configuration_dic = json.load(f)
            print("the config loaded is: "+str(configuration_dic))
    except IOError as e:
        logging.error("error reading config gile: "+e)

    my_controller = Controller(configuration_dic)
    my_view = View(my_controller, configuration_dic)
    my_model = Model(my_controller, configuration_dic)

    my_controller.add_view_model(my_view, my_model)  # for the bilateral comunication

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


