import time
import threading
import random
import os
from utils import add_event
from master_database import MasterDatabase
from bot import ChessBot


class Mode:    
    def __init__(self, name, one_player=False, human_color="Biały"):
        self.name = name
        self.board = self.initialize_board()
        self.current_turn = "Biały"
        self.timer = {"Biały": 600, "Czarny": 600}
        self.move_history = []
        self.running = True
        self.selected_piece = None
        self.valid_moves = []
        self.last_move = None
        self.winner = None
        self.game_type = "offline"  # offline and so
        self.game_mode = ""  # classic and so
        self.first_player_name = os.getlogin()
        self.second_player_name = "Dupa"
        self.session_id = ''

        self.one_player = one_player
        self.human_color = human_color
        self.bot_color = "Czarny" if human_color == "Biały" else "Biały"
        self.bot_has_moved = False
        if one_player:
            self.bot = ChessBot(bot_color=self.bot_color, search_depth=3)

        self.castling_rights = {
            "Biały": {"kingside": True, "queenside": True},
            "Czarny": {"kingside": True, "queenside": True}
        }
        self.start_timer()

    def coord_to_notation(self, coord):
        row, col = coord
        return chr(col + ord('a')) + str(8 - row)

    def get_move_notation(self, piece, start, end):
        # Produces long algebraic notation (e.g. "Pe2e4" or "Ke1g1" for castling)
        return piece + self.coord_to_notation(start) + self.coord_to_notation(end)

    def highlight_moves(self, x, y, buttons):
        piece = self.board[x][y]

        if piece == " ":
            return

        # Only allow moves if the piece belongs to the current turn
        if (self.current_turn == "Biały" and piece.islower()) or (self.current_turn == "Czarny" and piece.isupper()):
            return
        
        if self.one_player and self.current_turn == self.bot_color:
            return

        directions = {
            'p': [(1, 0)],
            'P': [(-1, 0)],
            'r': [(1, 0), (-1, 0), (0, 1), (0, -1)],
            'R': [(1, 0), (-1, 0), (0, 1), (0, -1)],
            'n': [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],
            'N': [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],
            'b': [(1, 1), (1, -1), (-1, 1), (-1, -1)],
            'B': [(1, 1), (1, -1), (-1, 1), (-1, -1)],
            'q': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
            'Q': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
            'k': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
            'K': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        }

        self.valid_moves = []

        if piece.lower() == 'p':
            forward = -1 if piece.isupper() else 1
            start_row = 6 if piece.isupper() else 1

            # Standard forward move
            if 0 <= x + forward < 8 and self.board[x + forward][y] == " ":
                self.valid_moves.append((x + forward, y))
   
                # Double move from starting position
                if x == start_row and 0 <= x + 2 * forward < 8 and self.board[x + forward][y] == " " and self.board[x + 2 * forward][y] == " ":
                    self.valid_moves.append((x + 2 * forward, y))

            # Diagonal capture moves
            for dx in [-1, 1]:
                if 0 <= x + forward < 8 and 0 <= y + dx < 8:
                    target = self.board[x + forward][y + dx]
                    if target != " " and target.islower() != piece.islower():
                        self.valid_moves.append((x + forward, y + dx))

            # En passant
            if self.last_move:
                last_piece, (sx, sy), (ex, ey) = self.last_move
                if last_piece.lower() == 'p' and abs(sx - ex) == 2 and sy == y and ex == x + forward:
                    en_passant_target = (x + forward, y + (1 if sy < y else -1))
                    self.valid_moves.append(en_passant_target)

        elif piece.lower() in ['r', 'b', 'q']:
            for direction in directions.get(piece.lower(), []):
                dx, dy = direction
                nx, ny = x + dx, y + dy

                while 0 <= nx < 8 and 0 <= ny < 8:
                    if self.board[nx][ny] != " " and self.board[nx][ny].islower() == piece.islower():
                        break
                    self.valid_moves.append((nx, ny))

                    if self.board[nx][ny] != " ":
                        break

                    nx += dx
                    ny += dy

        elif piece.lower() == 'n':
            for dx, dy in directions.get(piece.lower(), []):
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8 and (self.board[nx][ny] == " " or self.board[nx][ny].islower() != piece.islower()):
                    self.valid_moves.append((nx, ny))

        elif piece.lower() == 'k':
            for dx, dy in directions.get(piece.lower(), []):
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8 and (self.board[nx][ny] == " " or self.board[nx][ny].islower() != piece.islower()):
                    self.valid_moves.append((nx, ny))

            # Castling moves (very simplified check – you might want to add proper check and path safety)
            if self.castling_rights.get(self.current_turn):
                rights = self.castling_rights[self.current_turn]
                if rights.get("kingside"):
                    # Kingside: check that squares between king and rook are empty
                    if self.board[x][y+1] == " " and self.board[x][y+2] == " ":
                        self.valid_moves.append((x, y+2))

                if rights.get("queenside"):
                    if self.board[x][y-1] == " " and self.board[x][y-2] == " " and self.board[x][y-3] == " ":
                        self.valid_moves.append((x, y-2))

        self.check_for_check()

        return self.valid_moves

    def initialize_board(self):
        raise NotImplementedError("initialize_board must be implemented in subclasses")
    
    def check_checkmate(self):
        if not self.check_for_check():
            return False
        
        # Try every move from every piece
        for i in range(8):
            for j in range(8):
                if (self.current_turn == "Biały" and self.board[i][j].isupper()) or (
                    self.current_turn == "Czarny" and self.board[i][j].islower()):
                    self.highlight_moves(i, j, None)
                    for move in self.valid_moves:
                        piece = self.board[i][j]
                        # Save state
                        backup_from = self.board[i][j]
                        backup_to = self.board[move[0]][move[1]]
                        self.board[i][j] = " "
                        self.board[move[0]][move[1]] = piece
                        
                        still_in_check = self.check_for_check()
                        
                        # Undo the move
                        self.board[i][j] = backup_from
                        self.board[move[0]][move[1]] = backup_to
                        
                        if not still_in_check:
                            return False
        return True

    def check_for_check(self):
        king_symbol = 'K' if self.current_turn == "Biały" else 'k'
        king_position = None
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == king_symbol:
                    king_position = (i, j)
                    break
            if king_position:
                break
            
        if not king_position:
            return True

        x, y = king_position
        opponent_turn = "Czarny" if self.current_turn == "Biały" else "Biały"
        is_checked = False

        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if (opponent_turn == "Biały" and piece.isupper()) or (opponent_turn == "Czarny" and piece.islower()):
                    self.highlight_moves(i, j, None)
                    if (x, y) in self.valid_moves:
                        is_checked = True
                        break
            if is_checked:
                break

        if is_checked:
            self.show_check_warning()
        return is_checked

    def show_check_warning(self):
        print('Szach!')
        add_event(self.session_id, 'check')

    def prompt_promotion(self):
        add_event(self.session_id, 'promotion')
        return 'Q' if self.current_turn == "Biały" else 'q'
        # TODO wybór
        '''
        else:
            valid_pieces = ['Q', 'R', 'B', 'N'] if self.current_turn == "Biały" else ['q', 'r', 'b', 'n']
            while True:
                print("Choose promotion piece (Q/R/B/N):")
                choice = input().upper()
                if choice in ['Q', 'R', 'B', 'N']:
                    return choice if self.current_turn == "Biały" else choice.lower()'
        '''

    def is_valid_move(self, start, end):
        if not self.valid_moves:
            return False
        return (end[0], end[1]) in self.valid_moves
    
    def is_path_clear(self, start, end, piece):
        sx, sy = start
        ex, ey = end
        dx = ex - sx
        dy = ey - sy

        if piece.lower() in ['r', 'q']:
            if dx == 0:
                step = 1 if ey > sy else -1
                for y in range(sy + step, ey, step):
                    if self.board[sx][y] != " ":
                        return False
            elif dy == 0:
                step = 1 if ex > sx else -1
                for x in range(sx + step, ex, step):
                    if self.board[x][sy] != " ":
                        return False

        if piece.lower() in ['b', 'q']:
            if abs(dx) == abs(dy):
                step_x = 1 if ex > sx else -1
                step_y = 1 if ey > sy else -1
                for i in range(1, abs(dx)):
                    if self.board[sx + i * step_x][sy + i * step_y] != " ":
                        return False

        return True

    def move_piece(self, start, end, bypass_validity=False):
        sx, sy = start
        ex, ey = end
        piece = self.board[sx][sy]

        print('Moving piece:', piece, 'from', start, 'to', end)
        print('board before move:')
        self.print_board(self.board)

        if not bypass_validity and not self.is_valid_move(start, end):
            print("Invalid move!")
            return

        # Handle en passant capture:
        if piece.lower() == 'p' and sy != ey and self.board[ex][ey] == " ":
            # White pawn moving diagonally
            if piece == 'P':
                self.board[ex+1][ey] = " "
            # Black pawn moving diagonally
            elif piece == 'p':
                self.board[ex-1][ey] = " "

        # Handle castling move for king
        if piece.lower() == 'k' and abs(ey - sy) == 2:
            # Move the king
            self.board[ex][ey] = piece
            self.board[sx][sy] = " "
            # Move the rook accordingly
            if ey > sy:  # kingside
                rook_start = (sx, 7)
                rook_end = (sx, 5)
            else:  # queenside
                rook_start = (sx, 0)
                rook_end = (sx, 3)
            rook = self.board[rook_start[0]][rook_start[1]]
            self.board[rook_end[0]][rook_end[1]] = rook
            self.board[rook_start[0]][rook_start[1]] = " "
            # Invalidate castling rights for this color
            self.castling_rights[self.current_turn]["kingside"] = False
            self.castling_rights[self.current_turn]["queenside"] = False
        else:
            # Standard move
            self.board[ex][ey] = piece
            self.board[sx][sy] = " "

            # In case a rook or king moves, update castling rights:
            if piece.lower() == 'k':
                self.castling_rights[self.current_turn]["kingside"] = False
                self.castling_rights[self.current_turn]["queenside"] = False
            elif piece.lower() == 'r':
                if start == (7, 0):  # white queenside rook
                    self.castling_rights["Biały"]["queenside"] = False
                elif start == (7, 7):  # white kingside rook
                    self.castling_rights["Biały"]["kingside"] = False
                elif start == (0, 0):  # black queenside rook
                    self.castling_rights["Czarny"]["queenside"] = False
                elif start == (0, 7):  # black kingside rook
                    self.castling_rights["Czarny"]["kingside"] = False

            # Handle promotion for pawn reaching the last rank
            if piece.lower() == 'p' and (ex == 0 or ex == 7):
                self.board[ex][ey] = self.prompt_promotion()

        # Update move history with classic long notation
        move_notation = self.get_move_notation(piece, start, end)
        self.move_history.append(move_notation)
        self.last_move = (piece, start, end)

        self.current_turn = "Czarny" if self.current_turn == "Biały" else "Biały"

        if self.check_checkmate():
            self.winner = "Czarny" if self.current_turn == "Biały" else "Biały"
            add_event(self.session_id, 'end')
            self.running = False

        self.check_for_check()
        self.check_winner()

        print('Board after move:')
        self.print_board(self.board)

        if self.one_player and self.current_turn == self.bot_color and self.running and not self.bot_has_moved:
            add_event(self.session_id, 'bot_move_begin')
            self.bot_has_moved = False
            self.perform_bot_move()

    def check_winner(self):
        pieces = "".join("".join(row) for row in self.board)
        if "k" not in pieces:
            self.winner = "Biały"
            self.running = False
            add_event(self.session_id, 'end')
            return "Biały wygrał!"
        if "K" not in pieces:
            self.winner = "Czarny"
            self.running = False
            add_event(self.session_id, 'end')
            return "Czarny wygrał!"
        return None

    def resign(self):
        self.winner = "Czarny" if self.current_turn == "Biały" else "Biały"
        add_event(self.session_id, 'resign')
        self.running = False

    def draw(self):
        if self.game_type == "offline":
            self.winner = "Remis"
            add_event(self.session_id, 'draw')
            self.running = False
        else:
            print('zaimplementuj remis')  # TODO

    def start_timer(self):
        def timer_thread():
            while self.running:
                time.sleep(1)
                self.timer[self.current_turn] -= 1
                if self.timer[self.current_turn] <= 0:
                    self.running = False
                    self.winner = "Czarny" if self.current_turn == "Biały" else "Biały"
                    add_event(self.session_id, 'time_over')
        threading.Thread(target=timer_thread, daemon=True).start()

    def print_board(self, board):
        for row in board:
            print(" ".join(row))
        print()

    def perform_bot_move(self):
        if self.bot_has_moved:
            return
        
        bot_move = self.bot.get_move(self.board, self.current_turn)
        if bot_move is None:
            self.resign()
            return

        self.move_piece(bot_move[0], bot_move[1], bypass_validity=True)
        self.bot_has_moved = True
        add_event(self.session_id, 'bot_move_finish')
        print("Board after bot move:")
        self.print_board(self.board)

        winner = self.check_winner()
        if winner:
            self.winner = winner
            self.running = False
            add_event(self.session_id, 'end')


class ClassicMode(Mode):
    def __init__(self, one_player=False, human_color="Biały"):
        super().__init__("Classic", one_player, human_color)
        self.game_mode = "Klasyczny"

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
    def __init__(self, one_player=False, human_color="Biały"):
        super().__init__("Blitz", one_player, human_color)
        self.timer = {"Biały": 60, "Czarny": 60}
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


class GMMode(Mode):
    def __init__(self, name, one_player=True, human_color="Biały"):
        super().__init__(name, one_player, human_color)
        self.master_db = MasterDatabase()
        self.master_db.load_default_archmasters()
        self.game_mode = "arcymistrz"
        self.suggestions_enabled = False
        self.nerd_view_enabled = False
        
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
    
    def perform_bot_move(self):
        if not self.running or self.current_turn != self.bot_color:
            return
        
        move_suggestion = self.master_db.get_move_suggestion(self.board)
        
        if move_suggestion:
            start = move_suggestion['from']
            end = move_suggestion['to']
            self.move_piece(start, end)
            self.bot_has_moved = True
            add_event(self.session_id, {
                'type': 'arcymaster_move',
                'from': start,
                'to': end,
                'archmaster': move_suggestion['archmaster']
            })
        else:
            super().perform_bot_move()
    
    def toggle_suggestions(self):
        self.suggestions_enabled = not self.suggestions_enabled
        return self.suggestions_enabled
        
    def get_move_suggestions(self):
        if not self.suggestions_enabled:
            return []
        
        return self.master_db.get_move_statistics(self.board)
    
    def toggle_nerd_view(self):
        self.nerd_view_enabled = not self.nerd_view_enabled
        return self.nerd_view_enabled
    
    def get_nerd_view_data(self):
        current_stats = self.master_db.get_move_statistics(self.board)
        db_stats = self.master_db.get_database_stats()
        return {
            "move_suggestions": current_stats,
            "database_stats": db_stats
        }
    
    def import_pgn(self, file_path):
        """Import a PGN file into the master database"""
        return self.master_db.import_pgn(file_path)
    

class X960Mode(Mode):
    def __init__(self, one_player=False, human_color="Biały"):
        super().__init__("960", one_player, human_color)
        self.game_mode = "Fischer Losowy"

    def initialize_board(self):
        def generate_960_back_rank():
            # Implementation of Chess960 starting position
            while True:
                back = [''] * 8
                # Place bishops
                bishops = random.sample([0, 2, 4, 6], 2) + random.sample([1, 3, 5, 7], 2)
                back[bishops[0]] = 'b'
                back[bishops[1]] = 'b'
                
                # Place queen
                empty = [i for i in range(8) if back[i] == '']
                back[random.choice(empty)] = 'q'
                empty.remove(back.index('q'))
                
                # Place knights
                for _ in range(2):
                    idx = random.choice(empty)
                    back[idx] = 'n'
                    empty.remove(idx)
                
                # Place rook and king
                empty.sort()
                back[empty[0]] = 'r'
                back[empty[1]] = 'k'
                back[empty[2]] = 'r'
                
                if back.index('k') > back.index('r', empty[0]+1):
                    continue  # Invalid, retry
                
                return [p.lower() for p in back], [p.upper() for p in back]

        black, white = generate_960_back_rank()
        return [
            black,
            ["p"] * 8,
            [" "] * 8,
            [" "] * 8,
            [" "] * 8,
            [" "] * 8,
            ["P"] * 8,
            white
        ]