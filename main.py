import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGraphicsScene
)
from PyQt5.QtCore import (
    Qt,
    QTimer,
)
from PyQt5.QtGui import QPixmap
import numpy as np
from mapGenerator import MapManager, MINES
from basicSolver import solve

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        windowLayout = QVBoxLayout()

        self.setWindowTitle("Minesweeper")
        self.setStyleSheet("background-color: #317e1c")
        self.labelStyle = """color: white;font-size: 30px;font-weight: bold;font: HWYGOTH"""

        self.time = 0
        self.solvedGames = 0
        self.solvedGamesList = np.empty(0)
        self.topLayout = QHBoxLayout()
        self.flagLabel = self.Flags(self)
        self.topLayout.addWidget(self.flagLabel)
        self.clockLabel = self.Clock(self)
        self.topLayout.addWidget(self.clockLabel)
        restartButton = self.Restart(self)
        self.topLayout.addWidget(restartButton)
        self.topLayout.setContentsMargins(0, 0, 0, 0)
        topWidget = QWidget()
        topWidget.setLayout(self.topLayout)
        windowLayout.addWidget(topWidget)

        self.scene = QGraphicsScene()
        self.manager = MapManager(self.scene, self)
        self.manager.setMouseTracking(True)
        windowLayout.addWidget(self.manager)


        windowWidget = QWidget()
        windowWidget.setLayout(windowLayout)
        self.setCentralWidget(windowWidget)
        self.setMouseTracking(True)

    def startTimer(self):
        if self.time == 0:
            self.timer = QTimer()
            self.timer.timeout.connect(self.update)
            self.timer.start(10)

    def update(self):
        self.time += 0.01
        self.clockLabel.clock.setText(f"{int(self.time)}")
        for cord in MapManager.edges.copy():
            solve(self.manager.map.squares[cord])
            pass
        self.manager.load_queue()

    def restart(self):
        self.time = 0
        self.flagLabel.flags.setText(f"{MINES}")
        self.clockLabel.clock.setText("000")
        MapManager.queue.clear()
        MapManager.edges.clear()
        MapManager.flags = MINES
        MapManager.score = None
        self.manager.map.create_map()
        
        self.setDisabled(False)
        self.manager.map.squares[(5,4)].uncover()

    def closeEvent(self, a0):
        self.solvedGamesList = np.append(self.solvedGamesList, self.solvedGames)
        print(np.mean(self.solvedGamesList), len(self.solvedGamesList))
        return super().closeEvent(a0)

    class Flags(QWidget):
        def __init__(self, window):
            super().__init__()
            self.window = window
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)

            flagImage = QLabel()
            flagImage.setPixmap(QPixmap("Minesweeper/sprites/basic/flag.png"))
            flagImage.setAlignment(Qt.AlignRight)

            self.flags = QLabel(f"{MapManager.flags}")
            self.flags.setStyleSheet(window.labelStyle)

            layout.addWidget(flagImage)
            layout.addWidget(self.flags)

            self.setLayout(layout)

    class Clock(QWidget):
        def __init__(self, window):
            super().__init__()
            self.window = window
            layout = QHBoxLayout()

            clockImage = QLabel()
            clockImage.setPixmap(QPixmap("Minesweeper/sprites/basic/clock.png"))

            self.clock = QLabel("000")
            self.clock.setStyleSheet(window.labelStyle)

            layout.addWidget(clockImage)
            layout.addWidget(self.clock)

            self.setLayout(layout)

    class Restart(QLabel):
        def __init__(self, window):
            super().__init__()
            self.window = window
            self.setText("Restart")
            self.setStyleSheet(window.labelStyle + """;background-color: #32a83a""")
            self.setAlignment(Qt.AlignCenter)
        def mouseReleaseEvent(self, ev):
            self.window.restart()
            self.window.solvedGamesList = np.append(self.window.solvedGamesList, self.window.solvedGames)
            self.window.solvedGames = 0
            return super().mouseReleaseEvent(ev)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
