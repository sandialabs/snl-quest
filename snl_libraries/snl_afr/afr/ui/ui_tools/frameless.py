from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QCursor, QMouseEvent

class FramelessWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setMouseTracking(True)
        self.edgeMargin = 10
        self._dragPos = None
        self.resizeDirection = None
        self.setMinimumSize(100, 100)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._dragPos = event.globalPosition().toPoint()
            self.resizeDirection = self.getResizeDirection(event.position().toPoint())

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.NoButton:
            self.setCursor(self.getCursorShape(self.getResizeDirection(event.position().toPoint())))
        elif event.buttons() == Qt.LeftButton and self._dragPos:
            newPos = event.globalPosition().toPoint()
            diff = newPos - self._dragPos
            if self.resizeDirection:
                self.resizeWindow(diff)
            else:
                self.move(self.pos() + diff)
            self._dragPos = newPos

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._dragPos = None
        self.resizeDirection = None
        self.setCursor(Qt.ArrowCursor)

    def getResizeDirection(self, pos):
        xPos, yPos = pos.x(), pos.y()
        left = xPos < self.edgeMargin
        right = xPos > self.width() - self.edgeMargin
        top = yPos < self.edgeMargin
        bottom = yPos > self.height() - self.edgeMargin

        if left and top:
            return "top-left"
        elif left and bottom:
            return "bottom-left"
        elif right and top:
            return "top-right"
        elif right and bottom:
            return "bottom-right"
        elif left:
            return "left"
        elif right:
            return "right"
        elif top:
            return "top"
        elif bottom:
            return "bottom"
        return None

    def getCursorShape(self, direction):
        if direction in ["top-left", "bottom-right"]:
            return Qt.SizeFDiagCursor
        elif direction in ["top-right", "bottom-left"]:
            return Qt.SizeBDiagCursor
        elif direction in ["left", "right"]:
            return Qt.SizeHorCursor
        elif direction in ["top", "bottom"]:
            return Qt.SizeVerCursor
        return Qt.ArrowCursor

    def resizeWindow(self, diff):
        direction = self.resizeDirection
        newRect = self.geometry()

        if "left" in direction:
            newRect.setLeft(newRect.left() + diff.x())
        if "right" in direction:
            newRect.setRight(newRect.right() + diff.x())
        if "top" in direction:
            newRect.setTop(newRect.top() + diff.y())
        if "bottom" in direction:
            newRect.setBottom(newRect.bottom() + diff.y())

        if newRect.width() < self.minimumWidth():
            if "left" in direction:
                newRect.setLeft(newRect.right() - self.minimumWidth())
            else:
                newRect.setRight(newRect.left() + self.minimumWidth())
        if newRect.height() < self.minimumHeight():
            if "top" in direction:
                newRect.setTop(newRect.bottom() - self.minimumHeight())
            else:
                newRect.setBottom(newRect.top() + self.minimumHeight())

        self.setGeometry(newRect)

if __name__ == "__main__":
    app = QApplication([])
    window = FramelessWindow()
    window.resize(400, 300)
    window.show()
    app.exec()
