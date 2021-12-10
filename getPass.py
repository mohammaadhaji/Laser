from PyQt5 import QtCore, QtGui, QtWidgets
import hashlib


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(413, 180)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.lblID = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.lblID.setFont(font)
        self.lblID.setAlignment(QtCore.Qt.AlignCenter)
        self.lblID.setObjectName("lblID")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.lblID)
        self.txtID = QtWidgets.QLineEdit(Form)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.txtID.setFont(font)
        self.txtID.setObjectName("txtID")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.txtID)
        self.lblPass = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.lblPass.setFont(font)
        self.lblPass.setObjectName("lblPass")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.lblPass)
        self.txtPass = QtWidgets.QLineEdit(Form)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.txtPass.setFont(font)
        self.txtPass.setReadOnly(True)
        self.txtPass.setObjectName("txtPass")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.txtPass)
        self.btnGetPass = QtWidgets.QPushButton(Form)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.btnGetPass.setFont(font)
        self.btnGetPass.setObjectName("btnGetPass")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.btnGetPass)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout.setItem(0, QtWidgets.QFormLayout.FieldRole, spacerItem)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout.setItem(4, QtWidgets.QFormLayout.FieldRole, spacerItem1)
        self.verticalLayout.addLayout(self.formLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        self.btnGetPass.clicked.connect(self.getPass)

    def getPass(self):
        id = self.txtID.text()
        if not id:
            self.txtID.setFocus()
            return
        id += '@mohammaad_haji'
        lenght = 10
        password = hashlib.sha256(id.encode()).hexdigest()[:lenght]
        self.txtPass.setText(password)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Get Password"))
        self.lblID.setText(_translate("Form", "ID"))
        self.lblPass.setText(_translate("Form", "Password"))
        self.btnGetPass.setText(_translate("Form", "Get Password"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
