from __future__ import annotations

import sys
import typing as t
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

from tictactoe import UltimateTicTacToe, TicTacToe

BOX_SIZE = 50

class ClickedSignalRelay(qtc.QObject):
    # qt needs this for passing type safe signals
    clicked = qtc.pyqtSignal(qtw.QGraphicsSceneMouseEvent, object)

# Custom QGraphicsRectItem to handle hover events
class HoverableRectItem(qtw.QGraphicsRectItem):

    def __init__(self, clickCallback: t.Callable[[qtw.QGraphicsSceneMouseEvent, HoverableRectItem], None], 
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._signal_relay = ClickedSignalRelay()
        self._signal_relay.clicked.connect(clickCallback)
        self.setAcceptHoverEvents(True)
        self.background = qtg.QBrush(qtg.QColor(255, 255, 255))
        self.setBrush(self.background)
        self.setPen(qtg.QPen(qtg.QColor(100, 100, 100), 2))

    def setChar(self, char: str) -> None:
        # safely clear any existing text
        for item in self.childItems():
            item.deleteLater()

        text = qtw.QGraphicsTextItem(char, parent=self)
        text.setFont(qtg.QFont('Arial', 30))
        text.setDefaultTextColor(qtg.QColor(100, 100, 100))
        rect = text.boundingRect()
        xPos = (self.rect().width() - rect.width()) / 2
        yPos = (self.rect().height() - rect.height()) / 2
        text.setPos(xPos, yPos)

    def hoverEnterEvent(self, event):
        """Event when mouse enters the rectangle"""
        self.setBrush(qtg.QBrush(qtg.QColor(200, 200, 255)))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Event when mouse leaves the rectangle"""
        self.setBrush(self.background)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        self._signal_relay.clicked.emit(event, self)
        super().mousePressEvent(event)

class SubGrid(qtw.QGraphicsRectItem):
    def __init__(self, id: int, clickCallback: t.Callable[[qtw.QGraphicsSceneMouseEvent, HoverableRectItem], None], 
                 x: int, y: int, width: int, height: int) -> None:
        super().__init__(x, y, width, height)
        self.id = id
        self.clickCallback = clickCallback
        self.setPen(qtg.QPen(qtg.QColor(0, 0, 0), 2))
        self.setBrush(qtg.QBrush(qtg.QColor(255, 255, 255)))

        self.initGrid()

    def initGrid(self) -> None:
        self.grid = []
        for i in range(3):
            for j in range(3):
                rect = HoverableRectItem(self.clickCallback, 0, 0, BOX_SIZE, BOX_SIZE)
                rect.setPos(j*BOX_SIZE, i*BOX_SIZE)
                rect.setParentItem(self)
                self.grid.append(rect)

    def updateGrid(self, game: UltimateTicTacToe|TicTacToe) -> None:
        self.clearGrid()
        if isinstance(game, UltimateTicTacToe):
            if game.winner:
                self.setWinner(game.winner)
                return
            for i, cell in enumerate(self.grid):
                if game.board[i].winner:
                    cell.setChar(game.board[i].winner)
                else:
                    cell.setChar('#')

        if isinstance(game, TicTacToe):
            for i, cell in enumerate(self.grid):
                if game.winner:
                    self.setWinner(game.winner)
                else:
                    cell.setChar(game.board[i])

    def clearGrid(self) -> None:
        # unsetWinner
        for item in self.childItems():
            if isinstance(item, qtw.QGraphicsTextItem):
                item.deleteLater()
            else:
                item.setAcceptHoverEvents(True)

        for cell in self.grid:
            cell.setChar('')

    def setWinner(self, winner: str) -> None:
        for item in self.grid:
            item.setAcceptHoverEvents(False)
            item.setBrush(qtg.QBrush(qtg.QColor(255, 255, 255)))

        self.setBrush(qtg.QBrush(qtg.QColor(200, 200, 200)))
        self.setPen(qtg.QPen(qtg.QColor(200, 200, 200), 2))
        text = qtw.QGraphicsTextItem(winner, parent=self)
        text.setFont(qtg.QFont('Arial', 80))
        rect = text.boundingRect()
        xPos = (self.rect().width() - rect.width()) / 2
        yPos = (self.rect().height() - rect.height()) / 2
        text.setPos(xPos, yPos + 5)

class MainWindow(qtw.QWidget):
    def __init__(self, game: UltimateTicTacToe) -> None:
        super().__init__()
        self.currentGame = game
        self.gameStack: t.List[UltimateTicTacToe|TicTacToe] = [game]
        self.setWindowTitle('Ultimate Tic Tac Toe - Endgame')
        self.setFixedSize(int(3.5*3*BOX_SIZE), int(3.75*3*BOX_SIZE))
        self.setLayout(qtw.QVBoxLayout())

        self.lbl_depth = qtw.QLabel(f"Depth: {len(self.gameStack)}")
        self.lbl_depth.setFont(qtg.QFont('Arial', 20))

        self.scene = qtw.QGraphicsScene()
        self.view = qtw.QGraphicsView(self.scene)

        self.initGrid()
        self.updateGrid()

        self.layout().addWidget(self.lbl_depth)
        self.layout().addWidget(self.view)
        self.show()

    def initGrid(self) -> None:
        self.grid = []
        for i in range(3):
            for j in range(3):
                id = i*3+j
                rect = SubGrid(id, self.handleClick, 0, 0, BOX_SIZE*3, BOX_SIZE*3)
                rect.setPos(j*BOX_SIZE*3, i*BOX_SIZE*3)
                self.scene.addItem(rect)
                self.grid.append(rect)

        # lines for main grid
        self.scene.addLine(BOX_SIZE*3, 0, BOX_SIZE*3, BOX_SIZE*9, qtg.QPen(qtg.QColor(0, 0, 0), 4))
        self.scene.addLine(BOX_SIZE*6, 0, BOX_SIZE*6, BOX_SIZE*9, qtg.QPen(qtg.QColor(0, 0, 0), 4))
        self.scene.addLine(0, BOX_SIZE*3, BOX_SIZE*9, BOX_SIZE*3, qtg.QPen(qtg.QColor(0, 0, 0), 4))
        self.scene.addLine(0, BOX_SIZE*6, BOX_SIZE*9, BOX_SIZE*6, qtg.QPen(qtg.QColor(0, 0, 0), 4))

    def updateGrid(self) -> None:
        self.lbl_depth.setText(f"Depth: {len(self.gameStack)}")

        for i, subgrid in enumerate(self.grid):
            game = self.currentGame.board[i]
            subgrid.updateGrid(game)

        if len(self.gameStack) == 1 and self.currentGame.winner:
            self.lbl_depth.setText(f"Winner: {self.currentGame.winner}")

    def handleClick(self, event: qtw.QGraphicsSceneMouseEvent, cell: HoverableRectItem) -> None:
        if event.button() == qtc.Qt.LeftButton:
            self.handleLeftClick(cell)
        if event.button() == qtc.Qt.RightButton:
            self.handleRightClick(cell)

    def handleLeftClick(self, cell: HoverableRectItem) -> None:
        parent: SubGrid = cell.parentItem()
        parentGame = self.currentGame.board[parent.id]
        if isinstance(parentGame, UltimateTicTacToe):
            self.currentGame = parentGame
            self.gameStack.append(parentGame)
            self.updateGrid()
        if isinstance(parentGame, TicTacToe):
            parentGame.make_move(parent.grid.index(cell))
            self.updateGrid()

    def handleRightClick(self, cell: HoverableRectItem) -> None:
        if len(self.gameStack) > 1:
            self.gameStack.pop()
            self.currentGame = self.gameStack[-1]
            self.updateGrid()
            self.view.update()

class App:
    def __init__(self, game: UltimateTicTacToe) -> None:
        self.game = game

    def run(self) -> None:
        app = qtw.QApplication(sys.argv)
        mw = MainWindow(self.game)
        sys.exit(app.exec())