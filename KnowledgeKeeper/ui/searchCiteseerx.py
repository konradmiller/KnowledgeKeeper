# QT4 related
from PyQt4.QtGui import *
from PyQt4.QtCore import *

# django orm models
import settings
from orm.models import *

import KnowledgeKeeper

# citeSeerX rearch wrappers
from KnowledgeKeeper.citeseerx import Search, get_document

class searchCiteseerx( QMainWindow ):
    def __init__( self, target, parent, searchstr="" ):
        self.parent = parent
        self.target = target
        self.dialog = QDialog( parent )
        self.form = KnowledgeKeeper.forms.searchCiteseerx.Ui_searchCiteseerx()
        search = self.form
        dialog = self.dialog
        search.setupUi(dialog)

        # if the target exists we add through the manual add dialog and cannot select multiple entries
        if target == None:
            search.searchResults.setSelectionMode(QAbstractItemView.ExtendedSelection)
        else:
            search.searchResults.setSelectionMode(QAbstractItemView.SingleSelection)

        search.searchResults.setColumnCount( 3 )
        search.searchResults.setSelectionBehavior( QAbstractItemView.SelectRows )
        search.searchResults.horizontalHeader().setResizeMode(0,QHeaderView.Stretch)
        search.searchResults.horizontalHeader().setResizeMode(1,QHeaderView.Stretch)
        search.searchResults.verticalHeader().hide()
        search.searchLine.setText( unicode(searchstr) )
        self.clear()

        dialog.connect( search.searchButton, SIGNAL('clicked()'), self.search )
        dialog.connect( search.searchResults, SIGNAL('itemSelectionChanged()'), self.onSelectionChanged )
        dialog.connect( search.addButton, SIGNAL('clicked()'), self.add )
#        dialog.connect( search.citationsButton, SIGNAL('clicked()'), self.findCitations )
        dialog.connect( search.citedInButton, SIGNAL('clicked()'), self.findCitedIn )
        dialog.connect( search.lookUpDOI, SIGNAL('clicked()'), self.lookUpDOI )

        dialog.show()
        dialog.adjustSize()

        dialog.exec_()


    def clear(self):
        self.form.searchResults.clear()
        self.form.searchResults.setRowCount( 0 )
        self.form.searchResults.setHorizontalHeaderLabels( [ "Title", "Authors", "Year" ] )


    def addResult(self, title, authors, year, doc):
        row = self.form.searchResults.rowCount()
        res = self.form.searchResults
        res.insertRow(row)
        res.selectRow(row)
        res.setRowHeight(row, 22)

        item = QTableWidgetItem(title)
        item.setData(Qt.UserRole, QVariant(doc))
        res.setItem(row, 0, item)

        item = QTableWidgetItem(authors)
        item.setData(Qt.UserRole, QVariant(doc));
        res.setItem(row, 1, item)

        item = QTableWidgetItem(year)
        item.setData(Qt.UserRole, QVariant(doc));
        res.setItem(row, 2, item)


    def search(self):
        s = Search(unicode(self.form.searchLine.text()))
        for i, doi in enumerate(s):
            if i == 5: break
            doc = get_document(doi)
            authors = ', '.join([a.name for a in doc.authors.all()])
            self.addResult(unicode(doc.title), unicode(authors), unicode(doc.year), doc)
            self.parent.app.processEvents()


    def lookUpDOI(self):
        doi = unicode(self.form.searchLine.text())
        doc = get_document(doi)
        authors = ', '.join([a.name for a in doc.authors.all()])
        self.addResult(unicode(doc.title), unicode(authors), unicode(doc.year), doc)
        self.parent.app.processEvents()


    def add(self):
        self.dialog.hide()

        if self.target == None:
            # add all selected items directly without review
            # we get each item at least thrice (once for every column), we might also select
            # multiple items with the same doi - resolve this though a "seen" list
            seen = []

            for item in self.form.searchResults.selectedItems():
                doc = item.data(Qt.UserRole).toPyObject()
                if doc.doi not in seen:
                    seen.append(doc.doi)
                    KnowledgeKeeper.ui.newDocument.newDocument( self.parent, doc )

        else:
            # fill out add dialog for review
            row = self.form.searchResults.currentRow()
            doc = self.form.searchResults.item(row, 0).data(Qt.UserRole).toPyObject()

            self.target.titleLine.setText(unicode(doc.title))
            self.target.authorsLine.setText(unicode(', '.join([a.name for a in doc.authors.all()])))
            self.target.yearLine.setText(unicode(doc.year))
            self.target.doiLine.setText(unicode(doc.doi))

        self.dialog.close()


    def onSelectionChanged(self):
        self.form.addButton.setEnabled( True )
#        self.form.citationsButton.setEnabled( True )
        self.form.citedInButton.setEnabled( True )


    def findCitedIn(self):
        row = self.form.searchResults.currentRow()
        doc = self.form.searchResults.item(row, 0).data(Qt.UserRole).toPyObject()
        self.clear()

        for doi in doc.citings.split(';'):
            cited_doc = get_document(doi)
            authors = ', '.join([a.name for a in cited_doc.authors.all()])
            self.addResult(unicode(cited_doc.title), unicode(authors), unicode(cited_doc.year), cited_doc)
            self.parent.app.processEvents()

