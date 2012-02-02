import os, sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

appName="KnowledgeKeeper"
appVersion="0.1"
appWebsite=""

def run():
#    import config
    app = QApplication(sys.argv)
    QApplication.setApplicationName("KnowledgeKeeper")

    import forms
    import ui

    # main window
    main = ui.main.MainWindow( app )
    main.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()

