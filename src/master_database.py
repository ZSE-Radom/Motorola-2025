import requests
import os
import random
import json
from pgn_parser import PGNParser
from utils import san_to_coordinates

class MasterDatabase:
    def __init__(self):
        self.games = []
        self.positions = {}  # Dictionary mapping FEN positions to list of next moves
        self.archmasters = []
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        self.pgn_parser = PGNParser()
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # Default archmasters (12 of them as specified)
        self.default_archmasters = [
            "Magnus Carlsen", "Garry Kasparov", "Anatoly Karpov", "Bobby Fischer",
            "Viswanathan Anand", "Vladimir Kramnik", "Mikhail Botvinnik", "José Raúl Capablanca",
            "Emanuel Lasker", "Wilhelm Steinitz", "Alexander Alekhine", "Tigran Petrosian"
        ]

    def download_pgn(self, archmaster_name):
        """Download PGN files for a specific archmaster from chess.com"""
        print(f"Downloading games for {archmaster_name}...")
        
        # Format the name for the API URL
        formatted_name = archmaster_name.lower().replace(" ", "-")
        url = f"https://api.chess.com/pub/player/{formatted_name}/games/archives"
        
        try:
            # Get the list of monthly archives
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Error: Could not find games for {archmaster_name}")
                return False
                
            archives = response.json().get('archives', [])
            
            # Download a subset of archives (limit to 2 to avoid too many requests)
            for archive_url in archives[:2]:
                response = requests.get(archive_url)
                if response.status_code == 200:
                    games = response.json().get('games', [])
                    
                    # Filter for standard games and save them
                    pgn_content = ""
                    for game in games:
                        if game.get('rules') == 'chess':
                            pgn_content += game.get('pgn', '') + "\n\n"
                    
                    # Save to file
                    filename = os.path.join(self.data_dir, f"{formatted_name}_games.pgn")
                    with open(filename, 'a', encoding='utf-8') as f:
                        f.write(pgn_content)
                        
            return True
        except Exception as e:
            print(f"Error downloading games for {archmaster_name}: {str(e)}")
            return False

    def load_default_archmasters(self):
        """Load games from default archmasters"""
        for archmaster in self.default_archmasters:
            success = self.download_pgn(archmaster)
            if success:
                self.archmasters.append(archmaster)
        
        # Load all downloaded PGN files
        self.load_pgn_directory(self.data_dir)

    def load_pgn_file(self, file_path):
        """Load a PGN file and extract positions and moves"""
        try:
            num_games = self.pgn_parser.parse_file(file_path)
            
            # Process all games parsed by the parser
            for game in self.pgn_parser.games:
                self.games.append(game)
                
                # Add to positions dictionary
                for position in game['positions']:
                    fen = position['fen']
                    next_move = position['next_move']
                    
                    if not next_move:
                        continue
                        
                    if fen not in self.positions:
                        self.positions[fen] = []
                    
                    # Get player information
                    white = game['headers'].get('White', 'Unknown')
                    black = game['headers'].get('Black', 'Unknown')
                    
                    # Add move data
                    self.positions[fen].append({
                        'move': next_move,
                        'white': white,
                        'black': black
                    })
            
            return True
        except Exception as e:
            print(f"Error loading PGN file {file_path}: {str(e)}")
            return False

    def load_pgn_directory(self, directory):
        """Load all PGN files from a directory"""
        loaded_files = 0
        for filename in os.listdir(directory):
            if filename.endswith('.pgn'):
                file_path = os.path.join(directory, filename)
                if self.load_pgn_file(file_path):
                    loaded_files += 1
        
        print(f"Loaded {loaded_files} PGN files with a total of {len(self.games)} games")
        print(f"Database contains {len(self.positions)} unique positions")

    def convert_san_to_coordinates(self, board, move_san):
        """Convert a move in SAN to board coordinates"""
        return san_to_coordinates(board, move_san)

    def get_move_suggestion(self, board):
        """Get a move suggestion from the master database for the current position"""
        # Convert board to FEN
        fen = self.board_to_fen(board)
        
        # Check if this position exists in the database
        if fen in self.positions:
            moves = self.positions[fen]
            if moves:
                # Choose a random move from the database
                move_data = random.choice(moves)
                move_san = move_data['move']
                
                # Convert SAN move to coordinates
                from_pos, to_pos = self.convert_san_to_coordinates(board, move_san)
                
                return {
                    'from': from_pos,
                    'to': to_pos,
                    'archmaster': move_data['white'] if self.is_white_to_move(board) else move_data['black']
                }
        
        # If no move found in database
        return None

    def get_move_statistics(self, board):
        """Get statistics about moves from the master database for the current position"""
        fen = self.board_to_fen(board)
        
        if fen not in self.positions:
            return []
            
        moves = self.positions[fen]
        
        # Count frequency of each move
        move_counts = {}
        for move_data in moves:
            move_san = move_data['move']
            
            if move_san not in move_counts:
                # Convert SAN move to coordinates
                from_pos, to_pos = self.convert_san_to_coordinates(board, move_san)
                
                move_counts[move_san] = {
                    'count': 0,
                    'from': from_pos,
                    'to': to_pos,
                    'archmasters': set()
                }
            move_counts[move_san]['count'] += 1
            
            # Add archmaster who played this move
            if self.is_white_to_move(board):
                move_counts[move_san]['archmasters'].add(move_data['white'])
            else:
                move_counts[move_san]['archmasters'].add(move_data['black'])
                
        # Convert to list and calculate percentages
        total_moves = len(moves)
        statistics = []
        for move_san, data in move_counts.items():
            statistics.append({
                'from': data['from'],
                'to': data['to'],
                'frequency': data['count'],
                'percentage': (data['count'] / total_moves) * 100,
                'archmasters': list(data['archmasters'])
            })
            
        # Sort by frequency
        statistics.sort(key=lambda x: x['frequency'], reverse=True)
        
        return statistics

    def board_to_fen(self, board):
        """Convert the game board to FEN string format (position part only)"""
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
        
        # Remove trailing slash and return
        return fen[:-1]

    def is_white_to_move(self, board):
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

    def import_pgn(self, file_path):
        """Import a PGN file into the database"""
        return self.load_pgn_file(file_path)

    def get_database_stats(self):
        """Get database statistics"""
        return {
            "total_games": len(self.games),
            "total_positions": len(self.positions),
            "archmasters": self.archmasters
        }

    def reset(self):
        """Reset the database"""
        self.games = []
        self.positions = {}
        self.archmasters = []
        self.pgn_parser = PGNParser() 