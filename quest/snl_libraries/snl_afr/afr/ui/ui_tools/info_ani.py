from PySide6.QtCore import QPropertyAnimation, QEasingCurve

def about_page_drop(frame, minimize_button):
    """
    Animate the drop-down effect for the frame and handle minimize button click.

    :param frame: The frame object to animate.
    :type frame: QFrame
    :param minimize_button: The button object to minimize the frame.
    :type minimize_button: QPushButton
    """

    def minimize_frame():
        animation.setEndValue(0)
        animation.start()

    height = frame.height()
    newheight = 650 if height == 0 else 650

    animation = QPropertyAnimation(frame, b"maximumHeight")
    animation.setDuration(250)
    animation.setStartValue(height)
    animation.setEndValue(newheight)
    animation.setEasingCurve(QEasingCurve.InOutQuart)
    animation.start()

    minimize_button.clicked.connect(minimize_frame)