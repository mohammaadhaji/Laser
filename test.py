from PyQt5 import QtCore, QtWidgets
# from functools import cached_property
from werkzeug.utils import cached_property

class ToolBoxPage(QtCore.QObject):
    destroyed = QtCore.pyqtSignal()
    def __init__(self, button, scrollArea):
        super().__init__()
        self.button = button
        self.scrollArea = scrollArea
        self.widget = scrollArea.widget()
        self.widget.destroyed.connect(self.destroyed)

    def beginHide(self, spacing):
        self.scrollArea.setMinimumHeight(1)
        # remove the layout spacing as showing the new widget will increment
        # the layout size hint requirement
        self.scrollArea.setMaximumHeight(self.scrollArea.height() - spacing)
        # force the scroll bar off if it's not visible before hiding
        if not self.scrollArea.verticalScrollBar().isVisible():
            self.scrollArea.setVerticalScrollBarPolicy(
                QtCore.Qt.ScrollBarAlwaysOff)

    def beginShow(self, targetHeight):
        if self.scrollArea.widget().minimumSizeHint().height() <= targetHeight:
            # force the scroll bar off it will *probably* not required when the
            # widget will be shown
            self.scrollArea.setVerticalScrollBarPolicy(
                QtCore.Qt.ScrollBarAlwaysOff)
        else:
            # the widget will need a scroll bar, but we don't know when;
            # we will show it anyway, even if it's a bit ugly
            self.scrollArea.setVerticalScrollBarPolicy(
                QtCore.Qt.ScrollBarAsNeeded)
        self.scrollArea.setMaximumHeight(0)
        self.scrollArea.show()

    def setHeight(self, height):
        if height and not self.scrollArea.minimumHeight():
            # prevent the layout considering the minimumSizeHint
            self.scrollArea.setMinimumHeight(1)
        self.scrollArea.setMaximumHeight(height)

    def finalize(self):
        # reset the min/max height and the scroll bar policy
        self.scrollArea.setMinimumHeight(0)
        self.scrollArea.setMaximumHeight(16777215)
        self.scrollArea.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAsNeeded)


class AnimatedToolBox(QtWidgets.QToolBox):
    _oldPage = _newPage = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pages = []

    @cached_property
    def animation(self):
        animation = QtCore.QVariantAnimation(self)
        animation.setDuration(250)
        animation.setStartValue(0.)
        animation.setEndValue(1.)
        animation.valueChanged.connect(self._updateSizes)
        return animation

    @QtCore.pyqtProperty(int)
    def animationDuration(self):
        return self.animation.duration()

    @animationDuration.setter
    def animationDuration(self, duration):
        self.animation.setDuration(max(50, min(duration, 500)))

    @QtCore.pyqtSlot(int)
    @QtCore.pyqtSlot(int, bool)
    def setCurrentIndex(self, index, now=False):
        if self.currentIndex() == index:
            return
        if now:
            if self.animation.state():
                self.animation.stop()
                self._pages[index].finalize()
            super().setCurrentIndex(index)
            return
        elif self.animation.state():
            return
        self._oldPage = self._pages[self.currentIndex()]
        self._oldPage.beginHide(self.layout().spacing())
        self._newPage = self._pages[index]
        self._newPage.beginShow(self._targetSize)
        self.animation.start()

    @QtCore.pyqtSlot(QtWidgets.QWidget)
    @QtCore.pyqtSlot(QtWidgets.QWidget, bool)
    def setCurrentWidget(self, widget):
        for i, page in enumerate(self._pages):
            if page.widget == widget:
                self.setCurrentIndex(i)
                return

    def _index(self, page):
        return self._pages.index(page)

    def _updateSizes(self, ratio):
        if self.animation.currentTime() < self.animation.duration():
            newSize = round(self._targetSize * ratio)
            oldSize = self._targetSize - newSize
            if newSize < self.layout().spacing():
                oldSize -= self.layout().spacing()
            self._oldPage.setHeight(max(0, oldSize))
            self._newPage.setHeight(newSize)
        else:
            super().setCurrentIndex(self._index(self._newPage))
            self._oldPage.finalize()
            self._newPage.finalize()

    def _computeTargetSize(self):
        if not self.count():
            self._targetSize = 0
            return
        l, t, r, b = self.getContentsMargins()
        baseHeight = (self._pages[0].button.sizeHint().height()
            + self.layout().spacing())
        self._targetSize = self.height() - t - b - baseHeight * self.count()

    def _buttonClicked(self):
        button = self.sender()
        for i, page in enumerate(self._pages):
            if page.button == button:
                self.setCurrentIndex(i)
                return

    def _widgetDestroyed(self):
        self._pages.remove(self.sender())

    def itemInserted(self, index):
        button = self.layout().itemAt(index * 2).widget()
        button.clicked.disconnect()
        button.clicked.connect(self._buttonClicked)
        scrollArea = self.layout().itemAt(index * 2 + 1).widget()
        page = ToolBoxPage(button, scrollArea)
        self._pages.insert(index, page)
        page.destroyed.connect(self._widgetDestroyed)
        self._computeTargetSize()

    def itemRemoved(self, index):
        if self.animation.state() and self._index(self._newPage) == index:
            self.animation.stop()
        page = self._pages.pop(index)
        page.destroyed.disconnect(self._widgetDestroyed)
        self._computeTargetSize()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._computeTargetSize()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    toolBox = AnimatedToolBox()
    for i in range(8):
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        for b in range((i + 1) * 2):
            layout.addWidget(QtWidgets.QPushButton('Button {}'.format(b + 1)))
        layout.addStretch()
        toolBox.addItem(container, 'Box {}'.format(i + 1))
    toolBox.show()
    sys.exit(app.exec())