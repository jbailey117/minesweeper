SQUARESIZE = 64
MAPHEIGHT = 8
MAPLENGTH = 10
MINES = 10

from PyQt5.QtWidgets import QGraphicsView, QOpenGLWidget, QGraphicsPixmapItem, QFrame
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import QRectF, Qt, QSize
from random import randint
import numpy as np

def toPixMap(folder:str, file:str) -> QPixmap:
    return QPixmap(f"sprites/{folder}/{file}.png")

class MapManager(QGraphicsView):
    queue = set()
    edges =  set()
    score = None
    flags = MINES
    def __init__(self, scene, window):
        super().__init__(scene)
        self.setWindowTitle("Minesweeper")
        self.scene = scene
        self.setScene(self.scene)
        self.window = window
        self.map = self.Map(scene, self, window)
        self.hover = None
        self.setMinimumSize(QSize(MAPLENGTH * SQUARESIZE, MAPHEIGHT * SQUARESIZE))
        self.setFrameShape(QFrame.NoFrame)
        self.setContentsMargins(0, 0, 0, 0)
        self.setViewportMargins(0, 0, 0, 0)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setViewport(QOpenGLWidget())

    def load_queue(self):
        for square in MapManager.queue:
            square.update()
        MapManager.queue.clear()
        if MAPHEIGHT * MAPLENGTH - MINES == MapManager.score:
            self.window.setDisabled(True)
            self.window.timer.stop()
            self.window.solvedGames += 1
            self.window.restart()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.press_pos = event.pos()
        return super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        square = self.map.squares[(int((scene_pos.x()) // SQUARESIZE), int((scene_pos.y()) // SQUARESIZE))]
        if event.button() == Qt.MouseButton.LeftButton:
            square.uncover()
        elif event.button() == Qt.MouseButton.RightButton:
            square.flag()
        elif event.button() == Qt.MouseButton.MiddleButton:
            square.altUncover()
        self.load_queue()
        return super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        square = self.map.squares[(int((scene_pos.x()) // SQUARESIZE), int((scene_pos.y()) // SQUARESIZE))]
        if self.hover != square:
            if self.hover:
                self.hover.tint = False
                self.hover.update()
            square.tint = True
            square.update()
            self.hover = square
        return super().mouseMoveEvent(event)
    
    class Map:
        def __init__(self, scene, manager, window):
            self.scene = scene
            self.manager = manager
            self.window = window
            
            self.pixmap = QPixmap(MAPLENGTH * SQUARESIZE, MAPHEIGHT * SQUARESIZE)
            self.pixmap.fill(Qt.GlobalColor.transparent)

            self.square = QGraphicsPixmapItem(self.pixmap)
            self.square.setPos(0, 0)
            self.scene.addItem(self.square)

            self.create_map()

        def create_map(self):
            self.squares = {}
            for x in range(MAPLENGTH):
                for y in range(MAPHEIGHT):
                    self.squares[x, y] = self.Square(self, (x, y))

            self.redraw()

        def redraw(self):
            painter = QPainter(self.pixmap)
            for square in self.squares:
                self.draw_Square(painter, self.squares[square])
            painter.end()
            self.square.setPixmap(self.pixmap)

        def draw_Square(self, painter:QPainter, square):
            def style(arr):
                def strip(num):
                    two = np.sum(num == 2)
                    if two:
                        for n in [1, -1]:
                            pass
                    mirrorn = [[1,-1],[2,-3],[3,-2],[1,-1]]
                    for idx, n in enumerate([2,4,5,7]):
                        nidx = np.sum(num == n)
                        if nidx:
                            for x in mirrorn[idx]:
                                num = np.delete(num, np.where(num == (n + x))[0])
                    return num
                
                num = np.array([])

                for idx, n in np.ndenumerate(arr):
                    if n:
                        num = np.append(num, (idx[0] + 1))
                num = strip(num)
                file = ""
                for x in num:
                    file += str(int(x))
                if file:    
                    return file
                else:
                    return "0"
            rect = QRectF(square.cords[0] * SQUARESIZE, square.cords[1] * SQUARESIZE, SQUARESIZE, SQUARESIZE)

            if square.covered:
                painter.drawPixmap(rect.topLeft(), toPixMap("sand", "0"))
            if square.flagged:
                painter.drawPixmap(rect.topLeft(), toPixMap("basic", "flag"))
            if not square.covered:
                if square.mine:
                    painter.fillRect(rect, Qt.GlobalColor.red)
                elif square.number:
                    painter.drawPixmap(rect.topLeft(), toPixMap("sand", style(square.surrounding("covered"))))
                    painter.drawPixmap(rect.topLeft(), toPixMap("basic", str(square.number)))
                else:
                    painter.drawPixmap(rect.topLeft(), toPixMap("grass", style(square.surrounding("number"))))
            if square.tint:
                painter.drawPixmap(rect.topLeft(), toPixMap("basic", "tint"))

        def update_Square(self, x, y):
            painter = QPainter(self.pixmap)
            self.draw_Square(painter, self.squares[(x, y)])
            painter.end()
            self.square.setPixmap(self.pixmap)

        class Square:
            surroundingOffset:list = [[-1, -1],[0, -1],[1, -1],[-1,0 ],[1, 0],[-1, 1],[0, 1],[1, 1]]
            surroundingSquares:np.ndarray
            sprite:QPixmap

            def __init__(self, map, cords:set):
                self.map = map
                self.cords:set = cords
                self.mine:bool = False
                self.flagged:bool = False
                self.covered:bool = True
                self.number:int = None
                self.tint:bool = False

            def update(self):
                self.map.update_Square(*self.cords)

            def mapSurroundings(self):
                try:
                    self.surroundingSquares
                except(AttributeError):
                    surroundingSquares = np.empty(0, dtype=object)
                    for surroundingOffset in self.surroundingOffset:
                        square = None
                        try:
                            square = self.map.squares[(self.cords[0] + surroundingOffset[0], self.cords[1] + surroundingOffset[1])]
                        except(KeyError):
                            pass
                        surroundingSquares = np.append(surroundingSquares, square)
                    self.surroundingSquares = surroundingSquares

            def uncover(self):
                global score
                self.mapSurroundings()
                if not self.covered or self.flagged:
                    return
                elif MapManager.score == None:
                    mines = [self.cords]
                    for square in self.surroundingSquares:
                        if square:
                            mines.append(square.cords)
                    for mine in range(MINES):
                        while True:
                            cord = (randint(0, MAPLENGTH-1), randint(0, MAPHEIGHT-1))
                            if (not cord in mines):
                                self.map.squares[cord].mine = True
                                mines.append(cord)
                                break
                    MapManager.score = 0
                    self.map.window.startTimer()
                elif self.mine:
                    self.covered = False
                    self.update()
                    self.map.window.setDisabled(True)
                    self.map.window.timer.stop()
                    return
                MapManager.score += 1
                self.covered = False
                self.number = int(np.sum(self.surrounding("mine")))
                if not self.number:
                    for square in self.surroundingSquares:
                        if square:
                            square.uncover()
                else:
                    MapManager.edges.add(self.cords)
                    pass
                MapManager.queue.add(self)
                for square in self.surroundingSquares:
                    if square:
                        MapManager.queue.add(square)

            def altUncover(self):
                if self.covered:
                    return
                if np.sum(self.surrounding("flagged")) == self.number:
                    for square in self.surroundingSquares:
                        if square:
                            square.uncover()
                    if self.cords in MapManager.edges:
                        MapManager.edges.remove(self.cords)

            def flag(self, force = False):
                if self.covered:
                    if force:
                        self.flagged = True
                    elif self.flagged:
                        self.flagged = False
                        MapManager.flags += 1
                    elif MapManager.flags > 0:
                        self.flagged = True
                        MapManager.flags -= 1
                    else:
                        return
                self.map.window.flagLabel.flags.setText(f"{MapManager.flags}")
                MapManager.queue.add(self)

            def surrounding(self, attr:str) -> np.ndarray:
                surrounding = np.empty(0, dtype=bool)
                for square in self.surroundingSquares:
                    try:
                        if getattr(square, attr):
                            surrounding = np.append(surrounding, True)
                        else:
                            surrounding = np.append(surrounding, False)
                    except(AttributeError):
                        surrounding = np.append(surrounding, False)
                return surrounding
