
import copy
import math
import random

PIECE_VALUES = {
    'p': 1, 'P': 1,
    'n': 3, 'N': 3,
    'b': 3, 'B': 3,
    'r': 5, 'R': 5,
    'q': 9, 'Q': 9,
    'k': 1000, 'K': 1000
}

KNIGHT_MOVES = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                (1, 2), (1, -2), (-1, 2), (-1, -2)]
KING_MOVES = [(1, 0), (-1, 0), (0, 1), (0, -1),
              (1, 1), (1, -1), (-1, 1), (-1, -1)]
DIAGONAL_DIRS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
STRAIGHT_DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

CENTER_SQUARES = {(3, 3), (3, 4), (4, 3), (4, 4)}

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
            enemy_color = str.islower
        else:
            forward = 1
            start_row = 1
            enemy_color = str.isupper

        nx, ny = x + forward, y
        if is_inside(nx, ny) and board[nx][ny] == " ":
            moves.append(((x, y), (nx, ny)))
            nx2 = nx + forward
            if x == start_row and is_inside(nx2, ny) and board[nx2][ny] == " ":
                moves.append(((x, y), (nx2, ny)))
        for dy in [-1, 1]:
            nx, ny = x + forward, y + dy
            if is_inside(nx, ny) and board[nx][ny] != " " and enemy_color(board[nx][ny]):
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
        # TODO: Castling
    
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
    new_board = copy.deepcopy(board)
    (sx, sy), (ex, ey) = move
    piece = new_board[sx][sy]
    new_board[sx][sy] = " "
    new_board[ex][ey] = piece
    return new_board

def evaluate_board(board):
    score = 0
    for x in range(8):
        for y in range(8):
            piece = board[x][y]
            if piece != " ":
                value = PIECE_VALUES.get(piece, 0)
                if (x, y) in CENTER_SQUARES:
                    value += 0.2
                if piece.isupper():
                    score += value
                else:
                    score -= value

    white_moves = len(generate_all_legal_moves(board, "Biały"))
    black_moves = len(generate_all_legal_moves(board, "Czarny"))
    score += 0.1 * (white_moves - black_moves)
    
    return score

class ChessBot:
    def __init__(self, bot_color="Czarny", search_depth=3):
        self.bot_color = bot_color
        self.search_depth = search_depth

    def get_move(self, board, current_turn):
        if current_turn != self.bot_color:
            print("It's not my turn!")
            return None
        
        legal_moves = generate_all_legal_moves(board, current_turn)
        print(f"Bot ({current_turn}) has {len(legal_moves)} legal moves available.")
        if not legal_moves:
            print("No legal moves available. This is checkmate or stalemate.")
            return None
        
        _, best_move = self.minimax(board, self.search_depth, -math.inf, math.inf, True, current_turn)
        if best_move is None:
            print("Minimax did not select a move. Possibly at a terminal position.")
        else:
            print(f"Bot selected move: {best_move}")
        return best_move

    def minimax(self, board, depth, alpha, beta, maximizing, current_turn):
        moves = generate_all_legal_moves(board, current_turn)
        
        if depth == 0 or not moves:
            return evaluate_board(board), None
        
        best_move = None
        if maximizing:
            max_eval = -math.inf
            for move in moves:
                new_board = make_move(board, move)
                next_turn = "Czarny" if current_turn == "Biały" else "Biały"
                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, False, next_turn)
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
                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, True, next_turn)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

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
    
    bot = ChessBot(bot_color="Czarny", search_depth=3)
    current_turn = "Biały"
    
    white_moves = generate_all_legal_moves(board, current_turn)
    if white_moves:
        move = random.choice(white_moves)
        board = make_move(board, move)
        print(f"White moved from {move[0]} to {move[1]}")
        current_turn = "Czarny"
    
    bot_move = bot.get_move(board, current_turn)
    if bot_move:
        board = make_move(board, bot_move)
        print(f"Bot moved from {bot_move[0]} to {bot_move[1]}")
    else:
        print("Bot could not find a move.")
