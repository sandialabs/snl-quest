from PySide6.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
)


def about_quest_window(self):
    """Pop down the quest about window."""
    height = self.quest_about.height()

    if height == 0:
        newheight = 450

    else:
        newheight = 450

    self.animation = QPropertyAnimation(self.quest_about, b"maximumHeight")
    self.animation.setDuration(250)
    self.animation.setStartValue(height)
    self.animation.setEndValue(newheight)
    self.animation.setEasingCurve(QEasingCurve.InOutQuart)
    self.animation.start()


def quest_hide_window(self):
    """Hide the pop down quest window."""
    height = self.quest_about.height()

    if height == 0:
        newheight = 450

    else:
        newheight = 0

    self.animation = QPropertyAnimation(self.quest_about, b"maximumHeight")
    self.animation.setDuration(250)
    self.animation.setStartValue(height)
    self.animation.setEndValue(newheight)
    self.animation.setEasingCurve(QEasingCurve.InOutQuart)
    self.animation.start()
