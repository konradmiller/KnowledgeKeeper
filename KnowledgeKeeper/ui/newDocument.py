# QT4 related
from PyQt4.QtGui import *
from PyQt4.QtCore import *

# django orm models
import settings
from orm.models import *

from KnowledgeKeeper.db import addToDB

# indexing pdfs
from pdfdumper import pdfWords
import KnowledgeKeeper.forms
from KnowledgeKeeper.whoosh import addToIndex

import KnowledgeKeeper

class Document( QMainWindow ):
    def __init__( self, parent=None ):
        self.parent = parent
        self.dialog = QDialog( parent )
        self.newDoc = KnowledgeKeeper.forms.newDocument.Ui_newDocument()
        newDoc = self.newDoc
        dialog = self.dialog
        newDoc.setupUi(dialog)
        self.initializeForm()

        dialog.connect( newDoc.cancelButton, SIGNAL('clicked()'), SLOT('close()') )
        dialog.connect( newDoc.browseButton, SIGNAL('clicked()'), self.browseFile )
        dialog.connect( newDoc.okButton,     SIGNAL('clicked()'), self.doIt )
        dialog.connect( newDoc.searchButton, SIGNAL('clicked()'), self.onSearchCiteseerX )

        dialog.show()
        dialog.adjustSize()
        dialog.exec_()


    def browseFile( self ):
        import os.path
        self.newDoc.documentLine.setText( QFileDialog.getOpenFileName(self.dialog, 'Open file', os.path.expanduser('~')) )


    def indexNewFile( self, title, authors, tags, file ):
        addToIndex( self.parent.whoosh_ix, unicode(" ".join([title, authors, tags])), file )


    def delFromDB(self, title, authors, tags, file):
        title, authors, tags, file = map(unicode, (title, authors, tags, file))


    def onSearchCiteseerX(self):
        KnowledgeKeeper.ui.searchCiteseerx.searchCiteseerx( self.newDoc, self.parent )


###########################################################################


class newDocument( Document ):
    def __init__( self, parent=None, doc=None ):
        self.doc = doc
        Document.__init__( self, parent )


    def initializeForm( self ):
        if self.doc != None:
            doc = self.doc
            self.newDoc.titleLine.setText( unicode(doc.title) )
            self.newDoc.authorsLine.setText( ', '.join([x.name for x in doc.authors.all()]) )
            self.newDoc.yearLine.setText( unicode(doc.year) )
            self.newDoc.doiLine.setText( unicode(doc.doi) )


    def doIt( self ):
        title   = unicode(self.newDoc.titleLine.text())
        authors = unicode(self.newDoc.authorsLine.text())
        tags    = unicode(self.newDoc.tagsLine.text())
        year    = unicode(self.newDoc.yearLine.text())
        doi     = unicode(self.newDoc.doiLine.text())
        file    = unicode(self.newDoc.documentLine.text())

        # input sanatation
        y, ok = self.newDoc.yearLine.text().toInt()
        if not ok:
            msg = 'You must enter a year!'
            response = QMessageBox.question(self.parent, 'Error', msg, QMessageBox.Ok)
            if response == QMessageBox.Ok: # yes, this cannot fail, but if we don't do this qt will
                return False               # garbagecollect away the floor under the messageboxes feet
            return False                   # a well whatever just in case

        import string
        import random

        chars = string.letters + string.digits
        randomFilename = ""
        for i in range(8):
            randomFilename = randomFilename + random.choice(chars)

        if file == "":
            commentFileName = randomFilename
        else:
            # use the pdf name
            # strip the directory and append the 8 random chars
            # .txt is appended later and it is put in a different directory
            commentFileName = file
            while True:
                startidx = commentFileName.find( str('/') )
                if startidx == -1: break
                commentFileName = commentFileName[startidx+1:]
            commentFileName += randomFilename

        addToDB(title, authors, tags, year, file, commentFileName, doi)
        self.indexNewFile(title, authors, tags, file)
        self.dialog.close()
        self.parent.populateTable()

        return True

###########################################################################


class editDocument( Document ):
    def __init__( self, parent=None ):
        self.parent = parent
        if not self.parent.infoTable.selectedItems():
            return # no item is selected
        Document.__init__( self, parent )


    def initializeForm( self ):
        row = self.parent.infoTable.selectedItems()[0].row()
        doc = self.parent.infoTable.item(row, 0).data(Qt.UserRole).toPyObject()
        self.newDoc.titleLine.setText( unicode(doc.title) )
        self.newDoc.authorsLine.setText( ', '.join([x.name for x in doc.authors.all()]) )
        self.newDoc.tagsLine.setText( ', '.join([x.tag  for x in doc.tags.all()]) )
        self.newDoc.yearLine.setText( unicode(doc.year) )
        self.newDoc.doiLine.setText( unicode(doc.doi) )
        self.newDoc.documentLine.setText( doc.localFile )


    def doIt( self ):
        row = self.parent.infoTable.selectedItems()[0].row()
        doc = self.parent.infoTable.item(row, 0).data(Qt.UserRole).toPyObject()
        oldFile = doc.localFile
        commentFileName = doc.commentFile
        doc.delete()

        title   = unicode(self.newDoc.titleLine.text())
        authors = unicode(self.newDoc.authorsLine.text())
        tags    = unicode(self.newDoc.tagsLine.text())
        year    = unicode(self.newDoc.yearLine.text())
        doi     = unicode(self.newDoc.doiLine.text())
        file    = unicode(self.newDoc.documentLine.text())

        # input sanatation
        y, ok = self.newDoc.yearLine.text().toInt()
        if not ok:
            msg = 'You must enter a year!'
            response = QMessageBox.question(self.parent, 'Error', msg, QMessageBox.Ok)
            if response == QMessageBox.Ok: # yes, this cannot fail, but if we don't do this qt will
                return False               # garbagecollect away the floor under the messageboxes feet
            return False                   # a well whatever just in case

        addToDB(title, authors, tags, year, file, commentFileName, doi)

        if oldFile != file:
            if oldFile != "":
                # there is an old now invalid file in the whoosh index
                pass # TODO: remove from index
            if file != "":
                # there is a new file to be added to index
                self.indexNewFile(title, authors, tags, file)

        self.dialog.close()
        self.parent.populateTable()
        return True
