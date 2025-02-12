import time
import threading
import random
from typing import Dict, List, Tuple

from bot import ChessBot


class Mode:
    name: str
    board: List[List[str]]
    current_turn: str
    timer: Dict[str, int]
    running: bool
    move_history: List[str]
    last_move: List[str]
    game_type: str
    players: Dict[str, str or None]
    party_id: str
    moves: Dict[str, List[Tuple[int, int]]]
    one_player: bool
    bot: ChessBot
    def __init__(self, name, **kwargs):
        self.name = name
        self.board = self.initialize_board()
        self.current_turn = "white"
        self.timer = {
            "white": 600,
            "black": 600
        }
        self.running = False
        self.move_history = []
        self.last_move = []
        self.game_type = kwargs.get("game_type", "offline")
        self.players = {
            "white": None,
            "black": None
        }
        self.party_id = kwargs.get("party_id", None)
        self.moves = {
            'p': [(1, 0)],
            'r': [(1, 0), (-1, 0), (0, 1), (0, -1)],
            'n': [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],
            'b': [(1, 1), (1, -1), (-1, 1), (-1, -1)],
            'q': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
            'k': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
        }

        self.one_player = kwargs.get("one_player", False)

        vars(self).update(kwargs)

        if getattr(self, "one_player", False):
            self.bot = ChessBot(bot_color="black")

    def start_game(self):
        self.running = True
        self.start_timer()

    def start_timer(self):
        def timer_thread():
            while self.running:
                time.sleep(1)
                self.timer[self.current_turn] -= 1
                if self.timer[self.current_turn] <= 0:
                    self.running = False
                    self.winner = "black" if self.current_turn == "white" else "white"

        threading.Thread(target=timer_thread, daemon=True).start()

    def initialize_board(self):
        raise NotImplementedError("initialize_board must be implemented in subclasses")

    def is_valid_move_small_board(self, board: List[List[str]], start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        current_piece = board[start[0]][start[1]]

        if current_piece == " ":
            return False

        valid_fields = []

        if current_piece.lower() == 'p':
            if start[0] == 1:
                self.moves[current_piece].append((2, 0))

        for direction in self.moves[current_piece]:
            dx, dy = direction
            nx, ny = start[0] + dx, start[1] + dy
            if nx < 0 or nx >= 8 or ny < 0 or ny >= 8:
                continue


        if not valid_fields:
            return False

        return (end[0], end[1]) in valid_fields

    def is_valid_move_full_board(self, board: List[List[str]], start: Tuple[int, int], end: Tuple[int, int]):
        current_piece = board[start[0]][start[1]]

        if current_piece == " ":
            return False

        valid_fields = []

        if current_piece.lower() == 'p':
            self.moves[current_piece].append((2, 0))

        for direction in self.moves[current_piece]:
            dx, dy = direction
            nx, ny = start[0] + dx, start[1] + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                if board[nx][ny] != " ":
                    if board[nx][ny].islower() == current_piece.islower():
                        break
                    elif board[nx][ny].isupper() == current_piece.isupper():
                        break

                    if board[nx][ny].islower() == current_piece.isupper():
                        valid_fields.append((nx, ny))
                        break
                valid_fields.append((nx, ny))

                if board[nx][ny] != " ":
                    break

                nx += dx
                ny += dy

        if not valid_fields:
            return False

        return (end[0], end[1]) in valid_fields

    def is_valid_move(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        current_piece = self.board[start[0]][start[1]]
        print(current_piece)
        if current_piece == " ":
            return False

        board = self.board.copy()
        if current_piece.isupper():
            board.reverse()

        if current_piece.lower() in ['r', 'b', 'q']:
            return self.is_valid_move_full_board(board, start, end)
        else:
            return self.is_valid_move_full_board(board, start, end)


    def make_move(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        if not self.is_valid_move(start, end):
            return False

        current_piece = self.board[start[0]][start[1]]
        self.board[start[0]][start[1]] = " "
        self.board[end[0]][end[1]] = current_piece
        self.last_move.append((current_piece, start, end))
        self.move_history.append(f"{current_piece}: {start} -> {end}")

        return True


class ClassicMode(Mode):
    def __init__(self, **kwargs):
        super().__init__("Classic", **kwargs)

    def initialize_board(self):
        return [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            [" "] * 8,
            [" "] * 8,
            [" "] * 8,
            [" "] * 8,
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"]
        ]


class BlitzMode(Mode):
    def __init__(self, **kwargs):
        super().__init__("Blitz", **kwargs)
        self.timer = {"white": 60, "black": 60}
        self.game_mode = "Blitz"

    def initialize_board(self):
        return [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            [" "] * 8,
            [" "] * 8,
            [" "] * 8,
            [" "] * 8,
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"]
        ]


class X960Mode(Mode):
    def __init__(self, **kwargs):
        super().__init__("960", **kwargs)
        self.game_mode = "Fischer Losowy"

    def initialize_board(self):
        figures = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
        board = [[" "] * 8 for _ in range(8)]
        random.shuffle(figures)
        for i in range(8):
            board[0][i] = figures[i]
            board[1][i] = 'p'
            board[6][i] = 'P'
            board[7][i] = figures[i].upper()

        return board
