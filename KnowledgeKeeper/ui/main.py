# system
import os, os.path # for mkdir etc (whoosh)
import subprocess  # for Popen

# QT4
from PyQt4.QtGui import *
from PyQt4.QtCore import *

# Django (its sql orm model)
import settings
from orm.models import *

# whoosh
from whoosh.fields import Schema, STORED, ID, KEYWORD, TEXT
import whoosh.index as index
from whoosh.qparser import QueryParser

# citeSeerX rearch wrappers
from KnowledgeKeeper.citeseerx import Search, get_document

import KnowledgeKeeper


##################################
# stuff needed for tree-view
class tree():
    def __init__(self, doi):
        self.doi      = doi
        self.children = []
        self.parents  = []

    def newChild(self, child):
        if child not in self.children:
            self.children.append( child )

    def addParent(self, parent):
        self.parents.append( parent )

    def isRoot(self):
        return len(self.parents) == 0

    def isLeaf(self):
        return len(self.children) == 0

    def addChildrenToWidget(self, widget, prepend=None):
    # prepend is the item that we append to, it is None for the root
        doc = get_document(self.doi)
        item = QTreeWidgetItem(prepend, QStringList([unicode(doc.title)]))

        if prepend == None:
            # add to root
             widget.insertTopLevelItem( 0, item )
        else:
            # add to prepend item
            prepend.addChild( item )

        for c in self.children:
            c.addChildrenToWidget(widget, item)

    def addParentsToWidget(self, widget, prepend=None):
        doc = get_document(self.doi)
        item = QTreeWidgetItem(prepend, QStringList([unicode(doc.title)]))

        if prepend == None:
            # add to root
             widget.insertTopLevelItem( 0, item )
        else:
            # add to prepend item
            prepend.addChild( item )

        for c in self.parents:
            c.addParentsToWidget(widget, item)


def uniq( seq ):
    set = {}
    map(set.__setitem__, seq, [])
    return set.keys()
##################################


class MainWindow( QMainWindow ):
    def __init__( self, app ):
        QMainWindow.__init__(self)

        self.app = app

        # create or load whoosh index
        self.whoosh_schema = Schema(title=TEXT(stored=True), content=TEXT, path=ID(stored=True), tags=KEYWORD, icon=STORED)
        if not os.path.exists("whoosh_index"):
            os.mkdir("whoosh_index")
            self.whoosh_ix = index.create_in("whoosh_index", self.whoosh_schema)
        else:
            self.whoosh_ix = index.open_dir("whoosh_index")

        self.setupMainWindow()
        self.createActions()
        self.createToolbar()
        self.createMenu()
        self.populateTable()

        self.connect(self.mainWin.actionAbout, SIGNAL("triggered()"), self.onAbout)


    def setupMainWindow(self):
        self.mainWin = KnowledgeKeeper.forms.main.Ui_MainWindow()
        self.mainWin.setupUi(self)
        self.resize(600, 600)
        self.setWindowTitle('KnowledgeKeeper')

        self.infoTable = QTableWidget()
        self.infoTable.setSelectionMode( QAbstractItemView.SingleSelection )
        self.infoTable.setSelectionBehavior( QAbstractItemView.SelectRows )
        self.infoTable.setObjectName( "infoTable" )
        self.infoTable.setColumnCount( 5 )
        self.infoTable.itemChanged.connect( self.infoTableItemChanged )

        self.infoTree = QTreeWidget()
        self.infoTree.setObjectName( "infoTree" )
        self.infoTree.header().hide()

        self.DAGlabel= QLabel() # the QImage pixmap is loaded into this
        self.DAGlabel.setBackgroundRole(QPalette.Base)
        self.DAGlabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.DAGlabel.adjustSize()
        self.DAGlabel.setScaledContents(True)

        self.infoDAG = QScrollArea()
        self.infoDAG.setBackgroundRole(QPalette.Light)
        self.infoDAG.setWidget(self.DAGlabel)
        self.infoDAG.setWidgetResizable(True)

        self.DAGscaleFactor = 1.0
        self.scaleDAG( self.DAGscaleFactor )


        # use a widgetstack so none of the two widgets are garbage collected
        self.mainWidget = QStackedWidget()
        self.mainWidget.addWidget( self.infoTable )
        self.mainWidget.addWidget( self.infoTree )
        self.mainWidget.addWidget( self.infoDAG )
        self.setCentralWidget( self.mainWidget )

        self.onTableView() # switch to infoTable as central Widget


    def createActions(self):
        self.view = QAction(QIcon('icons/view.png'), 'View', self)
        v = self.view
        v.setShortcut('F3')
        v.setStatusTip('View Document')
        self.connect(v, SIGNAL('triggered()'), self.onViewDocument)

        self.quit = QAction(QIcon('icons/exit.png'), 'Quit', self)
        q = self.quit
        q.setShortcut('Ctrl+Q')
        self.connect(q, SIGNAL('triggered()'), SLOT('close()') )

        self.add = QAction(QIcon('icons/add.png'), 'Add', self)
        a = self.add
        a.setShortcut('Ctrl+N')
        a.setStatusTip('New Entry')
        self.connect(a, SIGNAL('triggered()'), self.onAddDocument)

        self.delete = QAction(QIcon('icons/delete.png'), 'Delete', self)
        delete = self.delete
        delete.setShortcut('Del')
        delete.setStatusTip('Delete Entry')
        self.connect(delete, SIGNAL('triggered()'), self.onDeleteDocument)

        self.edit = QAction(QIcon('icons/edit.png'), 'Edit', self)
        ed = self.edit
        ed.setShortcut('F2')
        ed.setStatusTip('Edit Entry')
        self.connect(ed, SIGNAL('triggered()'), self.onEditDocument)

        self.note = QAction(QIcon('icons/note.png'), 'Note', self)
        no = self.note
        no.setShortcut('F4')
        no.setStatusTip('Add/Edit Note')
        self.connect(no, SIGNAL('triggered()'), self.onEditNote)

        self.searchOnCiteSeerX = QAction(QIcon('icons/search.png'), 'Search on CiteSeerX', self)
        fi = self.searchOnCiteSeerX
        fi.setStatusTip('Search CiteSeerX')
        self.connect(fi, SIGNAL('triggered()'), self.onSearchSiteSeerX)

        self.tableview = QAction('Table View', self)
        tv = self.tableview
        tv.setStatusTip('Table View')
        self.connect(tv, SIGNAL('triggered()'), self.onTableView)

        self.treeview = QAction('Tree View', self)
        trv = self.treeview
        trv.setStatusTip('Tree View')
        self.connect(trv, SIGNAL('triggered()'), self.onTreeView)

        self.dagview = QAction('Directed Acyclic Graph View', self)
        dag = self.dagview
        dag.setStatusTip('DAG View')
        self.connect(dag, SIGNAL('triggered()'), self.onDAGView)

        self.rebuildWhooshIndex = QAction('Rebuild the search Index', self)
        rwi = self.rebuildWhooshIndex
        rwi.setStatusTip('Rebuild Search Index')
        self.connect(rwi, SIGNAL('triggered()'), self.onRebuildWhooshIndex)


    def createToolbar(self):
        self.toolbar = self.addToolBar('Main Toolbar')
        tb = self.toolbar
#        tb.addAction(self.exit)
        tb.addAction(self.view)
        tb.addAction(self.add)
        tb.addAction(self.delete)
        tb.addAction(self.edit)
        tb.addAction(self.note)
        tb.addAction(self.searchOnCiteSeerX)
        tb.addSeparator()

        # searchbar in toolbar
        tb.addWidget(QLabel("Search:"))
        self.searchbar = QLineEdit()
        tb.addWidget(self.searchbar)

        self.searchbutton = QPushButton(QIcon('icons/find.png'), 'Find')
        tb.addWidget(self.searchbutton)
        self.connect( self.searchbutton, SIGNAL('clicked()'), self.onSearch )


    def createMenu(self):
        menubar = self.menuBar()
        file = menubar.addMenu('&File')
        file.addAction(self.rebuildWhooshIndex)
        file.addSeparator()
        file.addAction(self.quit)

        view = menubar.addMenu('&View')
        view.addAction(self.tableview)
        view.addAction(self.treeview)
        view.addAction(self.dagview)


    # refreshes central widget
    def populateTable(self, searchterm=None):
        self.infoTable.clear()
        self.infoTable.setHorizontalHeaderLabels( [ "Title", "Authors", "Tags", "Year", "Read" ] )
        self.infoTable.setRowCount(0)
        self.infoTable.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.infoTable.verticalHeader().hide()

        if( searchterm == None or searchterm == "" ):
            papers = KKDocument.objects.all()
            for p in papers:
                a = ', '.join([x.name for x in p.authors.all()])
                t = ', '.join([x.tag  for x in p.tags.all()])
                self.newEntry(p.title, a, t, p.year, p)
            return # were done here - all papers printed

        # only if there is a searchterm:
        # search full text with whoosh
        print "FINDING %s" % searchterm
        searcher = self.whoosh_ix.searcher()
        parser = QueryParser("content", schema = self.whoosh_schema)
        query = parser.parse(unicode(searchterm))
        whoosh_results = searcher.search(query)

        print "FOUND", len(whoosh_results), "Objects"

        for r in whoosh_results:
            p = KKDocument.objects.get(localFile=r['path'])
            a = ', '.join([x.name for x in p.authors.all()])
            t = ', '.join([x.tag  for x in p.tags.all()])
            self.newEntry(p.title, a, t, p.year, p)


    def newEntry(self, title, authors, tags, year, doc):
        row = self.infoTable.rowCount()
        self.infoTable.insertRow(row)
        self.infoTable.selectRow(row)
        self.infoTable.setRowHeight(row, 22)

        item = QTableWidgetItem(unicode(title))
        item.setData(Qt.UserRole, QVariant(doc))
        item.setFlags( item.flags() & ~Qt.ItemIsUserCheckable )
        self.infoTable.setItem(row, 0, item)

        item = QTableWidgetItem(unicode(authors))
        item.setFlags( item.flags() & ~Qt.ItemIsUserCheckable )
        self.infoTable.setItem(row, 1, item)

        item = QTableWidgetItem(unicode(tags))
        item.setFlags( item.flags() & ~Qt.ItemIsUserCheckable )
        self.infoTable.setItem(row, 2, item)

        item = QTableWidgetItem(unicode(year))
        item.setFlags( item.flags() & ~Qt.ItemIsUserCheckable )
        self.infoTable.setItem(row, 3, item)

        item = QTableWidgetItem(unicode(""))
        item.setFlags( Qt.ItemIsUserCheckable | Qt.ItemIsEnabled )
        item.setData(Qt.UserRole, QVariant(doc))

        if doc.read: item.setCheckState( Qt.Checked )
        else:        item.setCheckState( Qt.Unchecked )

        self.infoTable.setItem(row, 4, item)


    def onAddDocument(self):
        KnowledgeKeeper.ui.newDocument.newDocument( self )


    def onDeleteDocument(self):
        selected = self.infoTable.selectedItems()
        if not selected: return

        row = selected[0].row()
        doc = self.infoTable.item(row, 0).data(Qt.UserRole).toPyObject()

        msg = "Are you sure you want to delete: %s?" % doc.title
        reply = QMessageBox.question(self, 'Are you Sure?', msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            doc.delete()
            self.populateTable( unicode(self.searchbar.text()) )


    def onEditDocument(self):
        KnowledgeKeeper.ui.newDocument.editDocument( self )


    def onSearch(self):
        self.populateTable( unicode(self.searchbar.text()) )


    def onAbout(self):
        KnowledgeKeeper.ui.about.show( self )


    def onViewDocument(self):
        selected = self.infoTable.selectedItems()
        if not selected: return

        row = selected[0].row()
        doc = self.infoTable.item(row, 0).data(Qt.UserRole).toPyObject()

        if doc.localFile != "":
            subprocess.Popen(args=['/usr/bin/acroread', doc.localFile])


    def onEditNote(self):
        selected = self.infoTable.selectedItems()
        if not selected: return

        row = selected[0].row()
        doc = self.infoTable.item(row, 0).data(Qt.UserRole).toPyObject()
        subprocess.Popen(args=['/usr/bin/gvim', 'comments/' + unicode(doc.commentFile) + '.txt'])


    def onSearchSiteSeerX(self):
        selected = self.infoTable.selectedItems()
        if not selected: return

        row    = selected[0].row()
        doc    = self.infoTable.item(row, 0).data(Qt.UserRole).toPyObject()
        search = KnowledgeKeeper.ui.searchCiteseerx.searchCiteseerx( None, self, searchstr=unicode(doc.title) )


    def rebuildTree(self):
        # just add all entries that don't have a doi
        # build a tree with the rest
        doiTreeNodes = {}
        allDois      = []

        papers = KKDocument.objects.all()
        for p in papers:
            if p.doi == "":
                tree(p.doi).addChildrenToWidget( self.infoTree )
            else:
                allDois.append( p.doi )

        allDois = uniq( allDois )

        for doi in allDois:
            doiTreeNodes[doi] = tree(doi)

        for doi in allDois:
            doc = get_document(doi)
            for c in doc.citings.split(';'):
                if c in allDois:
                    doiTreeNodes[doi].newChild( doiTreeNodes[c] )
                    doiTreeNodes[c].addParent( doiTreeNodes[doi] )

        self.infoTree.clear()

        reverse = False
        if reverse:
            for doi in allDois:
                if doiTreeNodes[doi].isLeaf():
                    doiTreeNodes[doi].addParentsToWidget( self.infoTree )
        else:
            for doi in allDois:
                if doiTreeNodes[doi].isRoot():
                    doiTreeNodes[doi].addChildrenToWidget( self.infoTree )


    def cleanAndWrapStr(self, dirtystr):
        import string
        okChars    = string.letters + string.digits + ' '
        cleanstr   = ''.join([x for x in dirtystr if x.lower() in okChars])

        softmax    = 10
        wrappedstr = ""
        curword    = ""
        for word in cleanstr.split():
            if len(curword) < softmax:
                if curword == "":
                    curword += word
                else:
                    curword += ' ' + word
            else:
                wrappedstr += curword + '\\n'
                curword = word

        wrappedstr += curword
        return str(wrappedstr)


    def rebuildDAG(self):
        # we will only build a DAG with the nodes that actually have a relationship
        # all single nodes are omitted, this includes the ones without a known DOI
        allDois  = []
        DAG      = []

        papers = KKDocument.objects.all()
        for p in papers:
            if p.doi != "": allDois.append( p.doi )

        allDois = uniq( allDois )

        for doi in allDois:
            doc = get_document(doi)
            for c in doc.citings.split(';'):
                if c in allDois:
                    child  = self.cleanAndWrapStr(get_document(c).title)
                    parent = self.cleanAndWrapStr(get_document(doi).title)
                    DAG.append( (parent, child) )

        import pydot

        g = pydot.graph_from_edges(DAG, directed=True)
        g.write_jpeg('dag.jpg', prog='dot')


    def showDAG(self):
        pixmap = QPixmap("dag.jpg")
        self.DAGlabel.setPixmap( pixmap )


    def onTableView(self):
        self.mainWidget.setCurrentIndex(0)


    def onTreeView(self):
        self.mainWidget.setCurrentIndex(1)
        self.rebuildTree()

    def onRebuildWhooshIndex(self):
        print "REBUILD NOT BOUND"
        pass
        if os.path.exists("whoosh_index"):
            os.rmdir("whoosh_index")
        self.whoosh_ix = index.create_in("whoosh_index", self.whoosh_schema)



    def onDAGView(self):
        self.mainWidget.setCurrentIndex(2)
        self.rebuildDAG()
        self.showDAG()


    def adjustScrollBar( self, scrollBar, factor ):
        scrollBar.setValue(int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep()/2)))


    def scaleDAG( self, factor ):
        pixmap = QPixmap(self.DAGlabel.pixmap())
        self.DAGlabel.resize(self.DAGscaleFactor * pixmap.size())
        self.adjustScrollBar(self.infoDAG.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.infoDAG.verticalScrollBar(), factor)


    def infoTableItemChanged( self, item ):
        if not item.flags() & Qt.ItemIsUserCheckable:
            # not interested in a change in the items which are not checkable
            return

        doc = item.data(Qt.UserRole).toPyObject()
        if doc.read == item.checkState():
            # not interested if it is set on initialization and equal to db entry
            return

        # otherwise update database because we toggled the "read" state
        doc.read = item.checkState()
        doc.save()


