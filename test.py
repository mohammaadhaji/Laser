import sys
from PyQt5 import QtWidgets, QtCore, QtGui

class MemoPad(QtWidgets.QMainWindow):
    def __init__(self):
        super(MemoPad, self).__init__()
        self.findIndex = -1

        self.resize(400, 400)
        self.setWindowTitle('Memo pad')
        self.textEdit = QtWidgets.QTextEdit(self)
        self.setCentralWidget(self.textEdit)

        self.fileMenu = self.menuBar().addMenu('File')
        self.openAction = self.fileMenu.addAction('Open')
        self.saveAction = self.fileMenu.addAction('Save')
        
        self.editMenu = self.menuBar().addMenu('Edit')
        self.findAction = self.editMenu.addAction('Find')
        self.replaceAction = self.editMenu.addAction('Replace')
        
        self.formatMenu = self.menuBar().addMenu('Format')
        self.fontAction = self.formatMenu.addAction('Font')

        self.openAction.triggered.connect(self.openFile)
        self.saveAction.triggered.connect(self.saveFile)
        self.findAction.triggered.connect(lambda : FindDialog(self).show())
        self.replaceAction.triggered.connect(lambda : ReplaceDialog(self).show())
        self.fontAction.triggered.connect(self.changeFont)

    def openFile(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None, 'Open file', '', 'Text file(*.py)')
        if fileName == '':
            return
        with open(fileName, mode='r') as f:
            self.textEdit.setPlainText( f.read() )

    def saveFile(self):
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(None, 'Save file', '', 'Text file(*.py)')
        if fileName == '':
            return
        with open(fileName, mode='w') as f:
            f.write( self.textEdit.toPlainText() )

    def findText(self, findText, reverse=False):
        if findText == '':
            return
        
        text = self.textEdit.toPlainText()
        if reverse:
            self.findIndex = text.rfind( findText, 0, self.findIndex )
        else:
            self.findIndex = text.find( findText, self.findIndex + 1 )
        
        if self.findIndex == -1:
            return
        
        textCursor = self.textEdit.textCursor()
        textCursor.setPosition(self.findIndex)
        textCursor.setPosition(self.findIndex + len(findText), QtGui.QTextCursor.KeepAnchor)
        self.textEdit.setTextCursor(textCursor)
        self.activateWindow()
        
    def replace(self, findText, replaceText):
        text = self.textEdit.toPlainText()
        if findText == self.textEdit.textCursor().selectedText():
            index = self.textEdit.textCursor().selectionStart()
            replaced = text[ : index ] + replaceText + text[index + len(findText) : ]
            self.textEdit.setPlainText(replaced)
        self.findText(findText)

    def replaceAll(self, findText, replaceText):
        self.textEdit.setPlainText(
            self.textEdit.toPlainText().replace(findText, replaceText)
        )

    def changeFont(self):
        font, ok = QtWidgets.QFontDialog.getFont(self.textEdit.currentFont(), self)
        if not ok:
            return
        self.textEdit.setFont(font)

class Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.label_0 = QtWidgets.QLabel('Find what')
        self.label_1 = QtWidgets.QLabel('Replace with')
        self.lineEdit_0 = QtWidgets.QLineEdit()
        self.lineEdit_1 = QtWidgets.QLineEdit()
        self.button_0 = QtWidgets.QPushButton('Find next')
        self.button_1 = QtWidgets.QPushButton('Find beafore')
        self.button_2 = QtWidgets.QPushButton('Replace')
        self.button_3 = QtWidgets.QPushButton('Replace all')
        self.button_4 = QtWidgets.QPushButton('Cancel')

        self.setLayout( QtWidgets.QGridLayout() )
        self.layout().addWidget( self.label_0,    0, 0, 1, 1 )
        self.layout().addWidget( self.label_1,    1, 0, 1, 1 )
        self.layout().addWidget( self.lineEdit_0, 0, 1, 1, 1 )
        self.layout().addWidget( self.lineEdit_1, 1, 1, 1, 1 )
        self.layout().addWidget( self.button_0,   0, 2, 1, 1 )
        self.layout().addWidget( self.button_1,   1, 2, 1, 1 )
        self.layout().addWidget( self.button_2,   2, 2, 1, 1 )
        self.layout().addWidget( self.button_3,   3, 2, 1, 1 )
        self.layout().addWidget( self.button_4,   4, 2, 1, 1 )
        # self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        # self.lineEdit_0.textChanged.connect(lambda : self.parent().findText(self.lineEdit_0.text()))
        self.button_0.clicked.connect(lambda : self.parent().findText(self.lineEdit_0.text()))
        self.button_1.clicked.connect(lambda : self.parent().findText(self.lineEdit_0.text(), True))
        self.button_2.clicked.connect(lambda : self.parent().replace( self.lineEdit_0.text(), self.lineEdit_1.text() ))
        self.button_3.clicked.connect(lambda : self.parent().textEdit.replaceAll( self.lineEdit_0.text(), self.lineEdit_1.text() ))
        self.button_4.clicked.connect(lambda : self.reject())
        
class FindDialog(Dialog):
    def __init__(self, parent=None):
        super(FindDialog, self).__init__(parent)
        self.setWindowTitle('Find')
        self.label_1.hide()
        self.lineEdit_1.hide()
        self.button_2.hide()
        self.button_3.hide()

class ReplaceDialog(Dialog):
    def __init__(self, parent=None):
        super(ReplaceDialog, self).__init__(parent)
        self.setWindowTitle('Replace')
        self.button_1.hide()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    memoPad = MemoPad()
    memoPad.show()
    app.exec()