import os.path

session_events = {}

def load_from_file(path):
    return os.path.join(os.path.dirname(__file__), path)


def add_event(session_id, event):
    if session_id not in session_events:
        session_events[session_id] = []
    session_events[session_id].append(event)


def get_events(session_id):
    if session_id not in session_events:
        return []
    events = session_events[session_id]
    session_events[session_id] = []
    return events


def san_to_coordinates(board, move_san):
    """Convert Standard Algebraic Notation move to board coordinates"""
    # Handle castling
    if move_san == "O-O":  # Kingside castling
        if is_white_to_move(board):
            return (7, 4), (7, 6)  # White kingside castle
        else:
            return (0, 4), (0, 6)  # Black kingside castle
    elif move_san == "O-O-O":  # Queenside castling
        if is_white_to_move(board):
            return (7, 4), (7, 2)  # White queenside castle
        else:
            return (0, 4), (0, 2)  # Black queenside castle

    # Parse the move
    is_capture = "x" in move_san
    move_san = move_san.replace("+", "").replace("#", "")  # Remove check/checkmate indicators

    # Handle pawn promotion
    promotion_piece = None
    if "=" in move_san:
        parts = move_san.split("=")
        move_san = parts[0]
        promotion_piece = parts[1]

    # Get destination square
    dest_file = move_san[-2]
    dest_rank = int(move_san[-1])
    dest_col = ord(dest_file) - ord('a')
    dest_row = 8 - dest_rank

    # Determine piece type
    if len(move_san) == 2:  # Pawn move like e4
        piece_type = "p"
    elif is_capture and len(move_san) == 4 and move_san[0].islower():  # Pawn capture like exd5
        piece_type = "p"
        src_file = move_san[0]
        src_col = ord(src_file) - ord('a')
    else:  # Piece move
        piece_type = move_san[0].lower()

    # Find the piece
    is_white = is_white_to_move(board)
    piece = piece_type.lower() if is_white else piece_type.upper()

    candidates = []
    for row in range(8):
        for col in range(8):
            if board[row][col].lower() == piece_type:
                # Check if it's the right color
                if (is_white and board[row][col].islower()) or (not is_white and board[row][col].isupper()):
                    # For pawn captures with specified file
                    if piece_type == "p" and is_capture and 'src_file' in locals():
                        if col == src_col:
                            candidates.append((row, col))
                    # For other moves, check if the piece can reach the destination
                    elif can_piece_move(board, row, col, dest_row, dest_col):
                        # Check disambiguating move like Nbd5
                        if len(move_san) > 3 and piece_type != "p":
                            disambiguation = move_san[1]
                            if disambiguation.isalpha():  # File disambiguation
                                if col != ord(disambiguation) - ord('a'):
                                    continue
                            elif disambiguation.isdigit():  # Rank disambiguation
                                if row != 8 - int(disambiguation):
                                    continue
                        candidates.append((row, col))

    # Choose the best candidate
    if candidates:
        return candidates[0], (dest_row, dest_col)

    # If no candidates found, return None
    return None, None


def is_white_to_move(board):
    """Determine if it's white's turn to move"""
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


def can_piece_move(board, src_row, src_col, dest_row, dest_col):
    """Check if a piece can move to the destination (approximate)"""
    piece = board[src_row][src_col].lower()

    # Check if destination has a piece of the same color
    dest_piece = board[dest_row][dest_col]
    if dest_piece != " ":
        if (piece.islower() and dest_piece.islower()) or (piece.isupper() and dest_piece.isupper()):
            return False

    # Simplified movement patterns
    if piece == 'p':  # Pawn
        direction = -1 if piece.islower() else 1  # White pawns move up (-1), black down (+1)

        if src_col == dest_col:  # Forward move
            # Check if path is clear
            if dest_piece != " ":
                return False

            # Single square forward
            if src_row + direction == dest_row:
                return True

            # Double square forward from starting position
            if (src_row == 6 and piece.islower() and dest_row == 4) or \
               (src_row == 1 and piece.isupper() and dest_row == 3):
                middle_row = src_row + direction
                if board[middle_row][src_col] == " ":
                    return True
            return False
        elif abs(src_col - dest_col) == 1 and src_row + direction == dest_row:  # Diagonal capture
            # Must capture a piece (ignoring en passant for simplicity)
            return dest_piece != " "
        return False
    elif piece == 'r':  # Rook
        if src_row != dest_row and src_col != dest_col:
            return False

        # Check if path is clear
        if src_row == dest_row:  # Horizontal move
            step = 1 if src_col < dest_col else -1
            for col in range(src_col + step, dest_col, step):
                if board[src_row][col] != " ":
                    return False
        else:  # Vertical move
            step = 1 if src_row < dest_row else -1
            for row in range(src_row + step, dest_row, step):
                if board[row][src_col] != " ":
                    return False
        return True
    elif piece == 'n':  # Knight
        # Knight can jump over pieces
        return (abs(src_row - dest_row) == 2 and abs(src_col - dest_col) == 1) or \
               (abs(src_row - dest_row) == 1 and abs(src_col - dest_col) == 2)
    elif piece == 'b':  # Bishop
        if abs(src_row - dest_row) != abs(src_col - dest_col):
            return False

        # Check if path is clear
        row_step = 1 if src_row < dest_row else -1
        col_step = 1 if src_col < dest_col else -1

        row, col = src_row + row_step, src_col + col_step
        while row != dest_row and col != dest_col:
            if board[row][col] != " ":
                return False
            row += row_step
            col += col_step
        return True
    elif piece == 'q':  # Queen
        # Combination of rook and bishop
        if src_row == dest_row or src_col == dest_col:  # Rook-like move
            if src_row == dest_row:  # Horizontal
                step = 1 if src_col < dest_col else -1
                for col in range(src_col + step, dest_col, step):
                    if board[src_row][col] != " ":
                        return False
            else:  # Vertical
                step = 1 if src_row < dest_row else -1
                for row in range(src_row + step, dest_row, step):
                    if board[row][src_col] != " ":
                        return False
            return True
        elif abs(src_row - dest_row) == abs(src_col - dest_col):  # Bishop-like move
            row_step = 1 if src_row < dest_row else -1
            col_step = 1 if src_col < dest_col else -1

            row, col = src_row + row_step, src_col + col_step
            while row != dest_row and col != dest_col:
                if board[row][col] != " ":
                    return False
                row += row_step
                col += col_step
            return True
        return False
    elif piece == 'k':  # King
        # Basic king move (not considering check)
        return abs(src_row - dest_row) <= 1 and abs(src_col - dest_col) <= 1

    return False
