import re
import os
import time

class PGNParser:
    def __init__(self):
        self.games = []
        
    def parse_file(self, file_path):
        """Parse a PGN file and extract games"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Split content into separate games
            game_texts = self._split_games(content)
            
            parsed_games = []
            for game_text in game_texts:
                game = self._parse_game(game_text)
                if game:
                    parsed_games.append(game)
                    
            self.games.extend(parsed_games)
            return len(parsed_games)
        except Exception as e:
            print(f"Error parsing PGN file {file_path}: {str(e)}")
            return 0
            
    def _split_games(self, content):
        """Split PGN content into separate games"""
        # Pattern to find game boundaries (starts with a new tag section)
        pattern = r'(?=\[Event\s+")'
        games = re.split(pattern, content)
        # Remove any empty strings
        return [g for g in games if g.strip()]
        
    def _parse_game(self, game_text):
        """Parse a single game from PGN text"""
        try:
            # Split header and movetext
            parts = game_text.split('\n\n', 1)
            if len(parts) < 2:
                return None
                
            header_text, movetext = parts
            
            # Parse header
            headers = self._parse_headers(header_text)
            
            # Parse moves
            moves = self._parse_moves(movetext)
            
            # Create game object
            game = {
                'headers': headers,
                'moves': moves,
                'positions': self._calculate_positions(moves)
            }
            
            return game
        except Exception as e:
            print(f"Error parsing game: {str(e)}")
            return None
            
    def _parse_headers(self, header_text):
        """Parse PGN headers into a dictionary"""
        headers = {}
        pattern = r'\[(\w+)\s+"([^"]*)"\]'
        matches = re.findall(pattern, header_text)
        
        for key, value in matches:
            headers[key] = value
            
        return headers
        
    def _parse_moves(self, movetext):
        """Parse the movetext section of a PGN game"""
        # Remove comments
        movetext = re.sub(r'\{[^}]*\}', '', movetext)
        
        # Remove variations
        movetext = re.sub(r'\([^)]*\)', '', movetext)
        
        # Remove result
        movetext = re.sub(r'(1-0|0-1|1/2-1/2|\*)\s*$', '', movetext)
        
        # Remove move numbers and extra whitespace
        clean_text = re.sub(r'\d+\.+\s*', '', movetext)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # Split into individual moves
        if clean_text:
            return clean_text.split()
        else:
            return []
            
    def _calculate_positions(self, moves):
        """Calculate board positions after each move"""
        positions = []
        board = self._create_initial_board()
        
        # Store initial position
        positions.append({
            'fen': self._board_to_fen(board),
            'move_index': 0,
            'next_move': moves[0] if moves else None
        })
        
        # Apply each move and store resulting positions
        for i, move in enumerate(moves):
            board = self._apply_move(board, move)
            next_move = moves[i+1] if i+1 < len(moves) else None
            
            positions.append({
                'fen': self._board_to_fen(board),
                'move_index': i+1,
                'next_move': next_move
            })
            
        return positions
        
    def _create_initial_board(self):
        """Create a standard chess starting position"""
        return [
            ["R", "N", "B", "Q", "K", "B", "N", "R"],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " "],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            ["r", "n", "b", "q", "k", "b", "n", "r"]
        ]
        
    def _board_to_fen(self, board):
        """Convert board to FEN string (position part only)"""
        fen = ""
        for row in board:
            empty = 0
            for piece in row:
                if piece == " ":
                    empty += 1
                else:
                    if empty > 0:
                        fen += str(empty)
                        empty = 0
                    fen += piece
            if empty > 0:
                fen += str(empty)
            fen += "/"
        
        # Remove trailing slash
        return fen[:-1]
        
    def _apply_move(self, board, move_san):
        """Apply a move in Standard Algebraic Notation to the board"""
        board = [row[:] for row in board]  # Create a copy of the board
        
        # Check for castling
        if move_san == "O-O":  # Kingside castling
            if self._is_white_to_move(board):
                # White kingside castle
                board[7][4], board[7][6] = " ", "k"
                board[7][7], board[7][5] = " ", "r"
            else:
                # Black kingside castle
                board[0][4], board[0][6] = " ", "K"
                board[0][7], board[0][5] = " ", "R"
            return board
        elif move_san == "O-O-O":  # Queenside castling
            if self._is_white_to_move(board):
                # White queenside castle
                board[7][4], board[7][2] = " ", "k"
                board[7][0], board[7][3] = " ", "r"
            else:
                # Black queenside castle
                board[0][4], board[0][2] = " ", "K"
                board[0][0], board[0][3] = " ", "R"
            return board
        
        # Parse the move
        is_capture = "x" in move_san
        is_check = "+" in move_san
        is_checkmate = "#" in move_san
        is_promotion = "=" in move_san
        
        # Clean the move
        clean_move = move_san.replace("+", "").replace("#", "")
        
        # Handle pawn promotion
        promotion_piece = None
        if is_promotion:
            parts = clean_move.split("=")
            clean_move = parts[0]
            promotion_piece = parts[1]
        
        # Parse the destination square
        if is_capture:
            if "x" == clean_move[-3]:  # Pawn capture like exd5
                dest_file = clean_move[-2]
                dest_rank = int(clean_move[-1])
                piece_type = "p"
                src_file = clean_move[0]
            else:  # Piece capture like Nxd5
                dest_file = clean_move[-2]
                dest_rank = int(clean_move[-1])
                piece_type = clean_move[0].lower()
                if len(clean_move) > 3:  # Disambiguating like Nbd5
                    src_hint = clean_move[1]
                else:
                    src_hint = None
        else:  # Non-capture
            dest_file = clean_move[-2]
            dest_rank = int(clean_move[-1])
            if len(clean_move) == 2:  # Pawn move like e4
                piece_type = "p"
            else:  # Piece move like Nd5
                piece_type = clean_move[0].lower()
                if len(clean_move) > 3:  # Disambiguating like Nbd5
                    src_hint = clean_move[1]
                else:
                    src_hint = None
        
        # Convert file-rank to board coordinates
        dest_col = ord(dest_file) - ord('a')
        dest_row = 8 - dest_rank
        
        # Find the piece making the move
        is_white = self._is_white_to_move(board)
        piece = piece_type.upper() if not is_white else piece_type.lower()
        
        # Find all matching pieces
        candidates = []
        for row in range(8):
            for col in range(8):
                if board[row][col].lower() == piece_type:
                    # Check if it's the right color
                    if (is_white and board[row][col].islower()) or (not is_white and board[row][col].isupper()):
                        # Check if the piece can reach the destination
                        if self._can_piece_move(board, row, col, dest_row, dest_col):
                            # Check for disambiguation if provided
                            if 'src_hint' in locals() and src_hint:
                                if src_hint.isdigit():  # Rank disambiguation
                                    if row != 8 - int(src_hint):
                                        continue
                                else:  # File disambiguation
                                    if col != ord(src_hint) - ord('a'):
                                        continue
                            candidates.append((row, col))
        
        if not candidates:
            print(f"No valid piece found for move {move_san}")
            return board
        
        # For simplicity, we'll just take the first candidate
        src_row, src_col = candidates[0]
        
        # Make the move
        board[dest_row][dest_col] = board[src_row][src_col]
        board[src_row][src_col] = " "
        
        # Handle promotion
        if is_promotion and promotion_piece:
            board[dest_row][dest_col] = promotion_piece.lower() if is_white else promotion_piece.upper()
        
        return board
        
    def _is_white_to_move(self, board):
        """Determine if it's white's turn to move (simplified)"""
        # Count pieces to estimate whose turn it is
        white_pieces = 0
        black_pieces = 0
        
        for row in board:
            for piece in row:
                if piece.isupper():
                    black_pieces += 1
                elif piece.islower():
                    white_pieces += 1
        
        # If white has more pieces missing than black, it's likely black's turn
        return white_pieces <= 16 - black_pieces
        
    def _can_piece_move(self, board, src_row, src_col, dest_row, dest_col):
        """Simplified check if a piece can move to the destination (approximate)"""
        piece = board[src_row][src_col].lower()
        
        # Simplified movement patterns
        if piece == 'p':  # Pawn
            if src_col == dest_col:  # Forward move
                if src_row > dest_row:  # White pawn
                    return src_row - dest_row <= 2 and src_row == 6 or src_row - dest_row == 1
                else:  # Black pawn
                    return dest_row - src_row <= 2 and src_row == 1 or dest_row - src_row == 1
            else:  # Diagonal capture
                return abs(src_col - dest_col) == 1 and abs(src_row - dest_row) == 1
        elif piece == 'r':  # Rook
            return src_row == dest_row or src_col == dest_col
        elif piece == 'n':  # Knight
            return (abs(src_row - dest_row) == 2 and abs(src_col - dest_col) == 1) or \
                   (abs(src_row - dest_row) == 1 and abs(src_col - dest_col) == 2)
        elif piece == 'b':  # Bishop
            return abs(src_row - dest_row) == abs(src_col - dest_col)
        elif piece == 'q':  # Queen
            return src_row == dest_row or src_col == dest_col or \
                   abs(src_row - dest_row) == abs(src_col - dest_col)
        elif piece == 'k':  # King
            return abs(src_row - dest_row) <= 1 and abs(src_col - dest_col) <= 1
        
        return False 