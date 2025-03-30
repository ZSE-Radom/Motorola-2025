import re
from collections import defaultdict

class PGNProcessor:
    def __init__(self):
        self.move_database = defaultdict(lambda: defaultdict(int))
        self.san_regex = re.compile(r"^([NKBQR])?([a-h])?([1-8])?x?([a-h][1-8])(=[NKBQR])?|^O-O(-O)?|^([a-h])[1-8]?x?([a-h][1-8])")

    def parse_pgn(self, file_path):
        current_game = []
        with open(file_path) as f:
            game_moves = []
            in_moves = False
            
            for line in f:
                line = line.strip()
                if line.startswith("["):
                    if in_moves:
                        self.process_game_moves(game_moves)
                        game_moves = []
                    in_moves = False
                    continue
                
                if line and not in_moves:
                    in_moves = True
                
                if in_moves:
                    line = re.sub(r"\{.*?\}", "", line)  # Remove comments
                    moves = re.findall(r"(\d+\.\s+)?(.*?)\s*(?:\d+\.\s+.*|$)", line)
                    for move in moves:
                        san_moves = move[1].split()
                        for m in san_moves:
                            if m and not m.endswith("."):
                                game_moves.append(m)

            if game_moves:
                self.process_game_moves(game_moves)

    def process_game_moves(self, moves):
        board = self.create_initial_board()
        turn = 'white'
        
        for move in moves:
            if move in ['1-0', '0-1', '1/2-1/2']:
                break
            
            san_move = move.replace("+", "").replace("#", "").replace("x", "")
            from_pos, to_pos = self.san_to_coordinates(board, san_move, turn)
            
            if from_pos and to_pos:
                fen_key = self.get_position_key(board, turn)
                self.move_database[fen_key][(from_pos, to_pos)] += 1
                self.apply_move(board, from_pos, to_pos, san_move)
                
            turn = 'black' if turn == 'white' else 'white'

    def san_to_coordinates(self, board, san, turn):
        # Handle castling
        if san == 'O-O':
            return self.get_kingside_castling(board, turn)
        if san == 'O-O-O':
            return self.get_queenside_castling(board, turn)

        # Handle pawn moves
        match = self.san_regex.match(san)
        if not match:
            return None, None

        piece_type = match.group(1) or 'P'
        dest = match.group(4)
        promotion = match.group(5)

        # Convert destination to coordinates
        to_col = ord(dest[0]) - ord('a')
        to_row = 8 - int(dest[1])

        # Find candidate pieces
        candidates = []
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece == ' ':
                    continue
                
                color = 'white' if piece.isupper() else 'black'
                if color != turn:
                    continue
                
                if piece.upper() == piece_type.upper():
                    candidates.append((row, col))

        # Filter valid moves
        for (row, col) in candidates:
            moves = self.get_valid_moves(board, row, col)
            if (to_row, to_col) in moves:
                return (row, col), (to_row, to_col)

        return None, None

    def apply_move(self, board, from_pos, to_pos, san):
        # Basic move application (needs expansion for special moves)
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        board[to_row][to_col] = board[from_row][from_col]
        board[from_row][from_col] = ' '

    def get_position_key(self, board, turn):
        # Create simplified position key (expand with castling rights and ep)
        pieces = []
        for row in board:
            for piece in row:
                pieces.append(piece if piece != ' ' else '1')
        return ''.join(pieces) + ('w' if turn == 'white' else 'b')

    def create_initial_board(self):
        return [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            [' ']*8,
            [' ']*8,
            [' ']*8,
            [' ']*8,
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]