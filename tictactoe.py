from __future__ import annotations

from result import Ok, Err, Result
from typing import List

class TicTacToe:
    def __init__(self) -> None:
        self.board = ['']*9
        self.current_player = 'X'

    def make_move(self, move: int) -> Result[None, str]:
        if self.winner:
            return Err("Game is over")

        if self.board[move]:
            return Err("Invalid move")
        
        self.board[move] = self.current_player
        self.current_player = 'X' if self.current_player == 'O' else 'O'

        return Ok(None)

    @property
    def winner(self) -> str|None:
        # returns the winner of the game, 'T' if it is a tie, or None if the game is not over
        # board is a list of 9 strings, each string is either 'X', 'O', or ''
        
        # check rows
        for row in range(3):
            if self.board[row*3] == self.board[row*3+1] == self.board[row*3+2] != '':
                return self.board[row*3]
        
        # check columns
        for col in range(3):
            if self.board[col] == self.board[3+col] == self.board[6+col] != '':
                return self.board[col]

        # check diagonals
        if self.board[0] == self.board[4] == self.board[8] != '':
            return self.board[0]

        if self.board[2] == self.board[4] == self.board[6] != '':
            return self.board[2]

        # check tie
        if all(self.board):
            return 'T'

        return None
    
    # def __repr__(self) -> str:
    #     return '\n'.join('|'.join(' ' if not self.board[i*3+j] else self.board[i*3+j] for j in range(3)) for i in range(3))
        
class UltimateTicTacToe:
    def __init__(self) -> None:
        self.board = None
        self.previous_move = None

    @property
    def winner(self):
        # check rows
        for row in range(3):
            if self.board[row*3].winner == self.board[row*3+1].winner == self.board[row*3+2].winner != None:
                return self.board[row*3].winner
            
        # check columns
        for col in range(3):
            if self.board[col].winner == self.board[3+col].winner == self.board[6+col].winner != None:
                return self.board[col].winner
            
        # check diagonals
        if self.board[0].winner == self.board[4].winner == self.board[8].winner != None:
            return self.board[0].winner
        if self.board[2].winner == self.board[4].winner == self.board[6].winner != None:
            return self.board[2].winner
        
        # check tie
        if all([self.board[i].winner for i in range(9)]):
            return 'T'
        
        return None

    def make_starting_move(self, move: List[int]) -> None:
        board = self.board
        for i in move[:-1]:
            board = board[i]

        board.make_move(move[-1])

        self.previous_move = move[1:]
    
    def make_move(self, move: int) -> Result[None, str]:
        if isinstance(move, list):
            raise TypeError("move must be an int")

        if self.previous_move is None:
            return Err("Must make starting move first")
        
        board = self.board
        for i in self.previous_move:
            if board[i].winner:
                return Err("Game is over")
            board = board[i]

        board.make_move(move)
        self.previous_move = self.previous_move[1:] + [move]

        return Ok(None)
    
    def __getitem__(self, key: int) -> TicTacToe|UltimateTicTacToe:
        return self.board[key]
    
    @classmethod
    def create_game(cls, depth: int) -> UltimateTicTacToe:
        game = UltimateTicTacToe()
        game.board = [cls.create_game(depth-1) if depth > 1 else TicTacToe() for _ in range(9)]
        return game
    
if __name__ == "__main__":
    game = UltimateTicTacToe.create_game(2)
    game.make_starting_move([0,2,1])
    game.make_move(1)