import re
from collections import defaultdict

class PGNProcessor:
    def __init__(self):
        self.move_database = defaultdict(lambda: defaultdict(int))
        self.san_regex = re.compile(
            r"^(?P<piece>[NKBQR])?"
            r"(?P<file>[a-h])?"
            r"(?P<rank>[1-8])?"
            r"(?P<capture>x)?"
            r"(?P<dest>[a-h][1-8])"
            r"(?P<promotion>=[NKBQR])?"
            r"(?P<check>[\+#]?)$"
        )
        self.castling_regex = re.compile(r"^O-O(-O)?[\+#]?$")

    def parse_pgn(self, file_path):
        """Main method to process PGN files"""
        with open(file_path) as f:
            pgn_text = f.read()

        games = pgn_text.split("\n\n[Event ")
        for game_text in games[1:]:  # Skip empty first element
            game_text = "[Event " + game_text
            self.process_game(game_text)

    def process_game(self, game_text):
        """Process individual game from PGN"""
        moves = self.extract_moves(game_text)
        game_state = self.initial_game_state()

        for san_move in moves:
            if san_move in ["1-0", "0-1", "1/2-1/2"]:
                break

            move_info = self.parse_san(san_move, game_state)
            if not move_info:
                continue

            from_pos, to_pos, promotion = move_info
            self.record_move(game_state, from_pos, to_pos)
            self.apply_move(game_state, from_pos, to_pos, promotion)

    def initial_game_state(self):
        """Initialize game state tracking"""
        return {
            "board": self.create_initial_board(),
            "castling": {"K": True, "Q": True, "k": True, "q": True},
            "en_passant": None,
            "turn": "white"
        }

    def create_initial_board(self):
        """Create standard chess starting position"""
        return [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p'] * 8,
            [' '] * 8,
            [' '] * 8,
            [' '] * 8,
            [' '] * 8,
            ['P'] * 8,
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]

    def extract_moves(self, game_text):
        """Extract move list from PGN text"""
        moves = []
        in_comment = False
        for line in game_text.split("\n"):
            line = line.strip()
            if line.startswith("["):
                continue
            for token in line.split():
                if token.startswith("{"):
                    in_comment = True
                if in_comment:
                    if token.endswith("}"):
                        in_comment = False
                    continue
                if any(c in token for c in (".", "$")):
                    continue
                moves.extend(token.split("-"))
        return [m for m in moves if m and m[0] not in ("$", "[")]

    def parse_san(self, san, game_state):
        """Convert SAN notation to board coordinates"""
        san = san.replace("+", "").replace("#", "").replace("!", "").replace("?", "")

        # Handle castling
        if self.castling_regex.match(san):
            return self.parse_castling(san, game_state)

        # Handle standard moves
        match = self.san_regex.match(san)
        if not match:
            return None

        groups = match.groupdict()
        piece_type = groups["piece"] or "P"
        dest = groups["dest"]
        to_pos = self.notation_to_coords(dest)

        # Find candidate pieces
        candidates = []
        for x in range(8):
            for y in range(8):
                piece = game_state["board"][x][y]
                if piece.upper() == piece_type.upper():
                    if game_state["turn"] == "white" and piece.isupper():
                        candidates.append((x, y))
                    elif game_state["turn"] == "black" and piece.islower():
                        candidates.append((x, y))

        # Filter by file/rank disambiguation
        if groups["file"]:
            candidates = [c for c in candidates if chr(c[1] + ord('a')) == groups["file"]]
        if groups["rank"]:
            candidates = [c for c in candidates if str(8 - c[0]) == groups["rank"]]

        # Find valid moves
        for candidate in candidates:
            moves = self.generate_moves(game_state, candidate)
            if to_pos in moves:
                promotion = groups["promotion"][1].upper() if groups["promotion"] else None
                if game_state["turn"] == "black" and promotion:
                    promotion = promotion.lower()
                return candidate, to_pos, promotion

        return None

    def parse_castling(self, san, game_state):
        """Handle castling moves"""
        row = 7 if game_state["turn"] == "white" else 0
        king_pos = (row, 4)

        if "O-O-O" in san:
            rook_from = (row, 0)
            rook_to = (row, 3)
            king_to = (row, 2)
        else:
            rook_from = (row, 7)
            rook_to = (row, 5)
            king_to = (row, 6)

        return king_pos, king_to, None

    def generate_moves(self, game_state, from_pos):
        """Generate possible moves for a piece"""
        x, y = from_pos
        piece = game_state["board"][x][y]
        moves = []

        if piece.upper() == "P":
            return self.generate_pawn_moves(game_state, from_pos)
        if piece.upper() == "N":
            return self.generate_knight_moves(from_pos)
        # Add other piece move generators

        return moves

    def generate_pawn_moves(self, game_state, from_pos):
        """Generate pawn moves including en passant"""
        x, y = from_pos
        moves = []
        direction = -1 if game_state["board"][x][y].isupper() else 1
        start_row = 6 if direction == -1 else 1

        # Standard moves
        if game_state["board"][x + direction][y] == " ":
            moves.append((x + direction, y))
            if x == start_row and game_state["board"][x + 2*direction][y] == " ":
                moves.append((x + 2*direction, y))

        # Captures
        for dy in [-1, 1]:
            if 0 <= y + dy < 8:
                if game_state["board"][x + direction][y + dy] != " ":
                    moves.append((x + direction, y + dy))
                elif (x + direction, y + dy) == game_state["en_passant"]:
                    moves.append((x + direction, y + dy))

        return moves

    def generate_knight_moves(self, from_pos):
        """Generate knight moves"""
        x, y = from_pos
        moves = []
        for dx, dy in [(-2,-1), (-2,1), (-1,-2), (-1,2),
                      (1,-2), (1,2), (2,-1), (2,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                moves.append((nx, ny))
        return moves

    def record_move(self, game_state, from_pos, to_pos):
        """Update move database"""
        position_key = self.get_position_key(game_state, "Czarny")
        self.move_database[position_key][(from_pos, to_pos)] += 1

    def get_position_key(self, board, current_turn):
        """Generate position key matching PGN processor's format"""
        pieces = []
        for row in board:
            for piece in row:
                pieces.append(piece if piece != ' ' else '1')  # PGN uses '1' for empty
        color = 'w' if current_turn == "Biały" else 'b'
        return ''.join(pieces) + color

    def apply_move(self, game_state, from_pos, to_pos, promotion):
        """Update game state after move"""
        x1, y1 = from_pos
        x2, y2 = to_pos
        piece = game_state["board"][x1][y1]

        # Handle special moves
        if piece.upper() == "K":
            # Update castling rights
            game_state["castling"][piece.upper()] = False
            game_state["castling"][piece.upper().lower()] = False

            # Handle castling
            if abs(y2 - y1) == 2:
                rook_from = (x1, 7 if y2 > y1 else 0)
                rook_to = (x1, 5 if y2 > y1 else 3)
                game_state["board"][rook_to[0]][rook_to[1]] = game_state["board"][rook_from[0]][rook_from[1]]
                game_state["board"][rook_from[0]][rook_from[1]] = " "

        # Update board state
        game_state["board"][x2][y2] = piece
        game_state["board"][x1][y1] = " "

        # Handle promotion
        if promotion:
            game_state["board"][x2][y2] = promotion

        # Update en passant
        if piece.upper() == "P" and abs(x2 - x1) == 2:
            game_state["en_passant"] = ((x1 + x2) // 2, y1)
        else:
            game_state["en_passant"] = None

        # Switch turns
        game_state["turn"] = "black" if game_state["turn"] == "white" else "white"

    @staticmethod
    def notation_to_coords(notation):
        """Convert chess notation (e.g., 'e4') to board coordinates"""
        if len(notation) != 2:
            return None
        col = ord(notation[0]) - ord('a')
        row = 8 - int(notation[1])
        return (row, col) if 0 <= row < 8 and 0 <= col < 8 else None
