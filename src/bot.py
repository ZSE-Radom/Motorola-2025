import copy
import math
import random

PIECE_VALUES = {
    'p': 1, 'P': 1,
    'n': 3, 'N': 3,
    'b': 3, 'B': 3,
    'r': 5, 'R': 5,
    'q': 10, 'Q': 10,
    'k': 15, 'K': 15
}

KNIGHT_MOVES = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                (1, 2), (1, -2), (-1, 2), (-1, -2)]
KING_MOVES = [(1, 0), (-1, 0), (0, 1), (0, -1),
              (1, 1), (1, -1), (-1, 1), (-1, -1)]
DIAGONAL_DIRS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
STRAIGHT_DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

CENTER_SQUARES = {(3, 3), (3, 4), (4, 3), (4, 4)}

PAWN_TABLE = [
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
    [0.1, 0.1, 0.2, 0.3, 0.3, 0.2, 0.1, 0.1],
    [0.05, 0.05, 0.1, 0.25, 0.25, 0.1, 0.05, 0.05],
    [0.0, 0.0, 0.0, 0.2, 0.2, 0.0, 0.0, 0.0],
    [0.05, -0.05, -0.1, 0.0, 0.0, -0.1, -0.05, 0.05],
    [0.05, 0.1, 0.1, -0.2, -0.2, 0.1, 0.1, 0.05],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
]

KNIGHT_TABLE = [
    [-0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5],
    [-0.4, -0.2,  0.0,  0.0,  0.0,  0.0, -0.2, -0.4],
    [-0.3,  0.0, 0.1, 0.15, 0.15, 0.1,  0.0, -0.3],
    [-0.3, 0.05, 0.15, 0.2, 0.2, 0.15, 0.05, -0.3],
    [-0.3,  0.0, 0.15, 0.2, 0.2, 0.15,  0.0, -0.3],
    [-0.3, 0.05, 0.1, 0.15, 0.15, 0.1, 0.05, -0.3],
    [-0.4, -0.2,  0.0, 0.05, 0.05,  0.0, -0.2, -0.4],
    [-0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5],
]

def is_inside(x, y):
    return 0 <= x < 8 and 0 <= y < 8

def is_enemy(piece, other):
    if other == " ":
        return False
    return piece.isupper() != other.isupper()

def generate_piece_moves(board, x, y):
    moves = []
    piece = board[x][y]
    if piece == " ":
        return moves

    if piece.lower() == 'p':
        if piece.isupper():
            forward = -1
            start_row = 6
        else:
            forward = 1
            start_row = 1

        nx, ny = x + forward, y
        if is_inside(nx, ny) and board[nx][ny] == " ":
            moves.append(((x, y), (nx, ny)))
            nx2 = nx + forward
            if x == start_row and is_inside(nx2, ny) and board[nx2][ny] == " ":
                moves.append(((x, y), (nx2, ny)))
        for dy in [-1, 1]:
            nx, ny = x + forward, y + dy
            if is_inside(nx, ny) and board[nx][ny] != " " and is_enemy(piece, board[nx][ny]):
                moves.append(((x, y), (nx, ny)))
    
    elif piece.lower() == 'n':
        for dx, dy in KNIGHT_MOVES:
            nx, ny = x + dx, y + dy
            if is_inside(nx, ny):
                if board[nx][ny] == " " or is_enemy(piece, board[nx][ny]):
                    moves.append(((x, y), (nx, ny)))
    
    elif piece.lower() == 'b':
        for dx, dy in DIAGONAL_DIRS:
            nx, ny = x + dx, y + dy
            while is_inside(nx, ny):
                if board[nx][ny] == " ":
                    moves.append(((x, y), (nx, ny)))
                else:
                    if is_enemy(piece, board[nx][ny]):
                        moves.append(((x, y), (nx, ny)))
                    break
                nx += dx
                ny += dy

    elif piece.lower() == 'r':
        for dx, dy in STRAIGHT_DIRS:
            nx, ny = x + dx, y + dy
            while is_inside(nx, ny):
                if board[nx][ny] == " ":
                    moves.append(((x, y), (nx, ny)))
                else:
                    if is_enemy(piece, board[nx][ny]):
                        moves.append(((x, y), (nx, ny)))
                    break
                nx += dx
                ny += dy

    elif piece.lower() == 'q':
        for dx, dy in DIAGONAL_DIRS + STRAIGHT_DIRS:
            nx, ny = x + dx, y + dy
            while is_inside(nx, ny):
                if board[nx][ny] == " ":
                    moves.append(((x, y), (nx, ny)))
                else:
                    if is_enemy(piece, board[nx][ny]):
                        moves.append(((x, y), (nx, ny)))
                    break
                nx += dx
                ny += dy

    elif piece.lower() == 'k':
        for dx, dy in KING_MOVES:
            nx, ny = x + dx, y + dy
            if is_inside(nx, ny):
                if board[nx][ny] == " " or is_enemy(piece, board[nx][ny]):
                    moves.append(((x, y), (nx, ny)))
    
    return moves

def generate_all_moves(board, turn):
    moves = []
    for x in range(8):
        for y in range(8):
            piece = board[x][y]
            if piece == " ":
                continue
            if (turn == "Biały" and piece.isupper()) or (turn == "Czarny" and piece.islower()):
                moves.extend(generate_piece_moves(board, x, y))
    return moves

def get_king_position(board, color):
    target = 'K' if color == "Biały" else 'k'
    for x in range(8):
        for y in range(8):
            if board[x][y] == target:
                return (x, y)
    return None

def is_in_check(board, color):
    king_pos = get_king_position(board, color)
    if not king_pos:
        return True
    opponent = "Czarny" if color == "Biały" else "Biały"
    opp_moves = generate_all_moves(board, opponent)
    for move in opp_moves:
        (_, _), (ex, ey) = move
        if (ex, ey) == king_pos:
            return True
    return False

def generate_all_legal_moves(board, turn):
    legal_moves = []
    all_moves = generate_all_moves(board, turn)
    for move in all_moves:
        new_board = make_move(board, move)
        if not is_in_check(new_board, turn):
            legal_moves.append(move)
    return legal_moves

def make_move(board, move):
    new_board = [row.copy() for row in board]
    (sx, sy), (ex, ey) = move
    piece = new_board[sx][sy]
    new_board[sx][sy] = " "
    if piece.lower() == 'p':
        if (piece.isupper() and ex == 0) or (piece.islower() and ex == 7):
            new_piece = 'Q' if piece.isupper() else 'q'
            new_board[ex][ey] = new_piece
        else:
            new_board[ex][ey] = piece
    else:
        new_board[ex][ey] = piece
    return new_board

def evaluate_board(board):
    score = 0
    # Check for checkmate/stalemate
    white_moves = generate_all_legal_moves(board, "Biały")
    black_moves = generate_all_legal_moves(board, "Czarny")
    
    if not white_moves and is_in_check(board, "Biały"):
        return -math.inf  # Black wins
    if not black_moves and is_in_check(board, "Czarny"):
        return math.inf   # White wins
    if not white_moves or not black_moves:
        return 0  # Stalemate
        
    for x in range(8):
        for y in range(8):
            piece = board[x][y]
            if piece == " ":
                continue
            value = PIECE_VALUES.get(piece, 0)
            if piece == 'P':
                value += PAWN_TABLE[x][y]
            elif piece == 'p':
                value += PAWN_TABLE[7 - x][y]
            elif piece == 'N':
                value += KNIGHT_TABLE[x][y]
            elif piece == 'n':
                value += KNIGHT_TABLE[7 - x][y]
            # Add mobility bonus
            if piece.isupper():
                moves = generate_piece_moves(board, x, y)
                value += len(moves) * 0.1
            else:
                moves = generate_piece_moves(board, x, y)
                value -= len(moves) * 0.1
            # Add center control bonus
            if (x, y) in CENTER_SQUARES:
                value += 0.15 if piece.isupper() else -0.15
            if piece.isupper():
                score += value
            else:
                score -= value
    return score

def order_moves(board, moves, current_turn, maximizing):
    def move_score(move):
        (sx, sy), (ex, ey) = move
        score = 0
        captured = board[ex][ey]
        attacker = board[sx][sy]
        if captured != " ":
            victim_val = PIECE_VALUES.get(captured, 0)
            attacker_val = PIECE_VALUES.get(attacker, 0)
            score += (victim_val - attacker_val) * 10
        if (ex, ey) in CENTER_SQUARES:
            score += 0.2
        return score
    return sorted(moves, key=move_score, reverse=maximizing)

class ChessBot:
    def __init__(self, bot_color="Czarny", search_depth=4, move_database=None):
        self.bot_color = bot_color
        self.search_depth = search_depth
        self.move_database = move_database
        self.current_line = []  # Stores tuples of (position_key, count, move)
        self.next_moves = []    # For displaying possible continuations

        # Initialize current_line with opening moves from the database
        if self.move_database:
            initial_board = [
                ["r", "n", "b", "q", "k", "b", "n", "r"],
                ["p", "p", "p", "p", "p", "p", "p", "p"],
                [" "] * 8,
                [" "] * 8,
                [" "] * 8,
                [" "] * 8,
                ["P", "P", "P", "P", "P", "P", "P", "P"],
                ["R", "N", "B", "Q", "K", "B", "N", "R"]
            ]
            initial_position_key = self.get_position_key(initial_board, "Biały")
            if initial_position_key in self.move_database:
                opening_moves = self.move_database[initial_position_key]
                self.current_line = [
                    (initial_position_key, count, self.parse_move_notation(move))
                    for move, count in opening_moves.items()
                ]
                self.next_moves = sorted(self.current_line, key=lambda x: x[1], reverse=True)[:5]


    def get_position_key(self, board, current_turn):
            """Generate position key matching PGN processor's simplified format (without castling/en passant)."""
            pieces = []
            for row in board:
                for piece in row:
                    pieces.append(piece if piece != ' ' else '1')
            color = 'w' if current_turn == "Biały" else 'b'
            return ''.join(pieces) + color


    def get_move(self, board, current_turn):
        if current_turn != self.bot_color:
            return None

        # Try using move database
        if self.move_database:
            position_key = self.get_position_key(board, current_turn)
            # Check current_line for matching position
            if self.current_line:
                matching_moves = [m for m in self.current_line if m[0] == position_key]
                if matching_moves:
                    best_move = max(matching_moves, key=lambda x: x[1])[2]
                    self.current_line = [m for m in self.current_line if m[0] == position_key]
                    self.next_moves = self.current_line[:5]
                    return best_move

            # Fetch new moves from database
            possible_moves = self.move_database.get(position_key, {})
            if possible_moves:
                structured_moves = [
                    (position_key, count, self.parse_move_notation(move))
                    for move, count in possible_moves.items()
                ]
                self.current_line = structured_moves
                self.next_moves = sorted(structured_moves, key=lambda x: x[1], reverse=True)[:5]
                best = max(possible_moves.items(), key=lambda x: x[1])[0]
                return self.parse_move_notation(best)

        # Fallback to minimax
        return self.get_standard_move(board, current_turn)

    def parse_move_notation(self, move_notation):
        """Convert SAN-like move (e2e4) to board coordinates."""
        if len(move_notation) < 4:
            return None
        from_sq = move_notation[:2]
        to_sq = move_notation[2:4]
        from_row = 8 - int(from_sq[1])
        from_col = ord(from_sq[0]) - ord('a')
        to_row = 8 - int(to_sq[1])
        to_col = ord(to_sq[0]) - ord('a')
        return ((from_row, from_col), (to_row, to_col))
    
    def get_standard_move(self, board, current_turn):
        maximizing = (self.bot_color == "Biały")
        legal_moves = generate_all_legal_moves(board, current_turn)
        
        if not legal_moves:
            return None
        
        _, best_move = self.minimax(board, self.search_depth, -math.inf, math.inf, maximizing, current_turn)
        return best_move

    def minimax(self, board, depth, alpha, beta, maximizing, current_turn):
        moves = generate_all_legal_moves(board, current_turn)
        moves = order_moves(board, moves, current_turn, maximizing)
        
        if depth == 0 or not moves:
            return evaluate_board(board), None
        
        best_move = None
        if maximizing:
            max_eval = -math.inf
            for move in moves:
                new_board = make_move(board, move)
                next_turn = "Czarny" if current_turn == "Biały" else "Biały"
                eval_score, _ = self.minimax(new_board, depth-1, alpha, beta, False, next_turn)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = math.inf
            for move in moves:
                new_board = make_move(board, move)
                next_turn = "Czarny" if current_turn == "Biały" else "Biały"
                eval_score, _ = self.minimax(new_board, depth-1, alpha, beta, True, next_turn)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def get_next_moves_suggestion(self):
        """Return possible continuation moves for UI display"""
        return [f"{self.coord_to_notation(start)}-{self.coord_to_notation(end)}" 
                for (start, end) in self.next_moves[:3]]

    def coord_to_notation(self, coord):
        """Convert board coordinates to chess notation"""
        row, col = coord
        return chr(col + ord('a')) + str(8 - row)
    
    def evaluate_board(board):
        score = 0
        metrics = {
            'material': 0,
            'positional': 0,
            'mobility': 0,
            'center_control': 0
        }

        for x in range(8):
            for y in range(8):
                piece = board[x][y]
                if piece == " ": continue
                
                value = PIECE_VALUES.get(piece, 0)
                metrics['material'] += value if piece.isupper() else -value

                # Ocena pozycyjna
                if piece == 'P': metrics['positional'] += PAWN_TABLE[x][y]
                elif piece == 'p': metrics['positional'] -= PAWN_TABLE[7-x][y]
                elif piece == 'N': metrics['positional'] += KNIGHT_TABLE[x][y]
                elif piece == 'n': metrics['positional'] -= KNIGHT_TABLE[7-x][y]

                # Mobilność
                moves = generate_piece_moves(board, x, y)
                mobility = len(moves) * 0.1
                if piece.isupper():
                    metrics['mobility'] += mobility
                else:
                    metrics['mobility'] -= mobility

                # Kontrola centrum
                if (x, y) in CENTER_SQUARES:
                    control = 0.15 if piece.isupper() else -0.15
                    metrics['center_control'] += control

        total = sum(metrics.values())
        return total, metrics

if __name__ == "__main__":
    board = [
        ["r", "n", "b", "q", "k", "b", "n", "r"],
        ["p", "p", "p", "p", "p", "p", "p", "p"],
        [" "] * 8,
        [" "] * 8,
        [" "] * 8,
        [" "] * 8,
        ["P", "P", "P", "P", "P", "P", "P", "P"],
        ["R", "N", "B", "Q", "K", "B", "N", "R"]
    ]
    
    bot = ChessBot(bot_color="Czarny", search_depth=4)
    current_turn = "Biały"
    
    white_moves = generate_all_legal_moves(board, current_turn)
    if white_moves:
        move = random.choice(white_moves)
        board = make_move(board, move)
        current_turn = "Czarny"
    
    bot_move = bot.get_move(board, current_turn)
    if bot_move:
        board = make_move(board, bot_move)