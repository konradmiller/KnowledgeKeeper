from PyQt4.QtGui import *
from PyQt4.QtCore import *
import settings
from orm.models import *

TITLE, AUTHOR, TAGS = range(3)
headerCaptions = { TITLE: 'Title', AUTHOR: 'Author', TAGS: 'Tags' }

class DocumentTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super(DocumentTableModel, self).__init__(parent)
        self.all_docs = KKDocument.objects.all()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if not section in headerCaptions:
                return QVariant()
            return QVariant(headerCaptions[section])
        return QVariant(section+1)

    def data(self, index, role):
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount(index)):
            return QVariant()

        if role == Qt.DisplayRole:
            if index.column() == TITLE:
                return QVariant(self.all_docs[index.row()].title)
            elif index.column() == AUTHOR:
                authors = ', '.join([x.name for x in self.all_docs[index.row()].authors.all()])
                return QVariant(authors)
            elif index.column() == TAGS:
                tags = ', '.join([x.tag for x in self.all_docs[index.row()].tags.all()])
                return QVariant(tags)
        return QVariant()

    def rowCount(self, index):
        return self.all_docs.count()

    def columnCount(self, index):
        return 3

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    table = QTableView()
    model = DocumentTableModel()
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setModel(model)
    wnd = table.show()
    sys.exit(app.exec_())

