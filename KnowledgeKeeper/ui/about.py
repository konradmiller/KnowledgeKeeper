# Copyright: Damien Elmes <anki@ichi2.net>
# -*- coding: utf-8 -*-
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

from PyQt4.QtGui import *
import KnowledgeKeeper.forms
from KnowledgeKeeper import appVersion

def show( parent ):
    dialog = QDialog(parent)
    abt = KnowledgeKeeper.forms.about.Ui_About()
    abt.setupUi(dialog)
    abouttext = '<p>' + "KnowledgeKeeper"
    abouttext += '<p>' + "Version %s" % appVersion + '<br>'
    abouttext += '<p>' + "Written by Konrad Miller"
    abt.label.setText( abouttext )
    dialog.show()
    dialog.adjustSize()
    dialog.exec_()
