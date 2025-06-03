import sys
from PySide6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QVBoxLayout, QApplication
from PySide6.QtCore import QPropertyAnimation, QRectF, QSequentialAnimationGroup, QPointF, QSizeF, QObject, QEasingCurve, Property, Qt
from PySide6.QtGui import QColor, QBrush

class AnimatedRectItem(QGraphicsRectItem, QObject):
    def __init__(self, rect, parent=None):
        QGraphicsRectItem.__init__(self, rect, parent)
        QObject.__init__(self)

        # Set flat design with rounded corners
        self.setPen(Qt.NoPen)
        self.setBrush(self.create_flat_brush())

    def create_flat_brush(self):
        # Flat color brush with the provided green color
        return QBrush(QColor(129, 194, 65))

    def set_pos(self, pos):
        self.setPos(pos)

    def get_pos(self):
        try:
            return QGraphicsRectItem.pos(self)
        except RecursionError:
            pass

    pos = Property(QPointF, get_pos, set_pos)

class ProgressAnimationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create a graphics view and scene for the animation
        self.graphics_view = QGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)

        # Remove scroll bars
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Set transparent background
        self.graphics_view.setStyleSheet("background: transparent; border: none;")
        self.graphics_scene.setBackgroundBrush(QBrush(Qt.transparent))

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.graphics_view)
        self.setLayout(layout)

        # Initialize variables for the animation
        self.block_size = QSizeF(50, 50)
        self.blocks_loaded = [None, None, None]  # Track blocks loaded for each button
        self.animation_groups = []  # Keep references to animation groups

    def animate_progress(self, button_index):
        animation_group = QSequentialAnimationGroup()

        # Clear the previous block if it exists
        if self.blocks_loaded[button_index] is not None:
            self.graphics_scene.removeItem(self.blocks_loaded[button_index])

        block = AnimatedRectItem(QRectF(0, 0, self.block_size.width(), self.block_size.height()))
        start_x = 50 + button_index * (self.block_size.width() + 10)  # Calculate horizontal position
        block.setPos(QPointF(start_x, -self.block_size.height()))  # Start position above the scene
        self.graphics_scene.addItem(block)

        # Adjust the end position to be one block size from the bottom
        end_y = self.graphics_view.height() - self.block_size.height() * 2  # One block size from the bottom
        animation = QPropertyAnimation(block, b"pos")
        animation.setDuration(1000)
        animation.setStartValue(QPointF(start_x, -self.block_size.height()))
        animation.setEndValue(QPointF(start_x, end_y))
        animation.setEasingCurve(QEasingCurve.OutBounce)

        animation_group.addAnimation(animation)
        self.blocks_loaded[button_index] = block

        # Keep a reference to the animation group
        self.animation_groups.append(animation_group)

        animation_group.start()

        #print(f"Animation started for block at: {start_x}, {end_y}")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ProgressAnimationWidget()
    window.show()

    sys.exit(app.exec())
