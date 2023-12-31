from gui import App
from tictactoe import UltimateTicTacToe

def main():
    tictactoe = UltimateTicTacToe.create_game(depth=3)
    app = App(tictactoe)
    app.run()

if __name__ == '__main__':
    main()