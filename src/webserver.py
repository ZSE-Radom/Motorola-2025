from flask import Flask, render_template, jsonify, request, session
from modes import ClassicMode, BlitzMode, X960Mode, GMMode
from flask_cors import CORS
import os
from utils import get_events
import logging

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests
app.secret_key = os.urandom(12).hex()

log = logging.getLogger("werkzeug")
log.disabled = True
# Store game modes and sessions
modes_store = {}
available_modes = {
    'classic': ClassicMode,
    'blitz': BlitzMode,
    '960': X960Mode,
    'gm': GMMode
}

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/profile', methods=['GET'])
def profile():
    return jsonify({
        'name': 'Patyna',
        'elo': 1200,
        'wins': 0,
        'losses': 0,
        'draws': 0,
        'pfp': '8715642fbbded8333534042f40a2a3e4.png'
    })


@app.route('/listModes', methods=['GET'])
def list_modes():
    temp_modes = available_modes.copy()
    temp_modes.pop('gm', None)
    return jsonify({'modes': list(temp_modes.keys())})


@app.route('/startOffline', methods=['POST'])
def start_offline():
    try:
        data = request.json
        mode_name = data.get('game_mode')
        one_player = data.get('one_player', False)
        human_color = data.get('human_color', "Biały")
        custom_board = data.get('custom_board', None)
        allow_for_revert = data.get('allow_for_revert', True)
        bot_mode = data.get('bot_mode', 'easy')
        gm_name = data.get('gm_name', False)

        if mode_name not in available_modes:
            return jsonify({'error': 'Invalid mode'}), 400

        if mode_name == 'gm':
            mode_instance = available_modes[mode_name](name=gm_name, one_player=one_player, human_color=human_color)
        else:
            mode_instance = available_modes[mode_name](one_player=one_player, human_color=human_color)
        session_id = session.get('session_id') or os.urandom(12).hex()
        session['session_id'] = session_id
        mode_instance.session_id = session_id

        modes_store[session_id] = mode_instance
        mode_instance.game_mode = mode_name

        if allow_for_revert:
            mode_instance.allow_for_revert = allow_for_revert

        if custom_board:
            try:
                # Normalize the board data before setting it
                for i in range(len(custom_board)):
                    for j in range(len(custom_board[i])):
                        # Convert empty strings to spaces
                        if custom_board[i][j] == '':
                            custom_board[i][j] = ' '
                mode_instance.set_board(custom_board)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
        else:
            mode_instance.board = mode_instance.initialize_board()

        if gm_name:
            mode_instance.gm_name = gm_name

        if bot_mode:
            mode_instance.bot_mode = bot_mode

        return jsonify({
            'board': mode_instance.board,
            'timer': mode_instance.timer,
            'current_turn': mode_instance.current_turn,
            'running': mode_instance.running,
            'winner': mode_instance.winner,
            'game_type': mode_instance.game_type,
            'game_mode': mode_instance.game_mode,
            'first_player_name': mode_instance.first_player_name,
            'second_player_name': mode_instance.second_player_name,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/startOnline', methods=['POST'])
def start_online():
    try:
        mode_name = request.json.get('mode')
        if mode_name not in available_modes:
            return jsonify({'error': 'Invalid mode'}), 400

        mode_instance = available_modes[mode_name](None)
        session_id = os.urandom(12).hex()
        session['session_id'] = session_id

        modes_store[session_id] = mode_instance

        return jsonify({'session_id': session_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/joinOnline', methods=['POST'])
def join_online():
    try:
        session_id = request.json.get('session_id')
        if session_id not in modes_store:
            return jsonify({'error': 'Invalid session ID'}), 400

        session['session_id'] = session_id
        return jsonify({'status': 'joined', 'session_id': session_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/stats', methods=['GET'])
def stats():
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in modes_store:
            return jsonify({'error': 'Game session not found'}), 400

        mode_instance = modes_store[session_id]
        return jsonify({
            'board': mode_instance.board,
            'timer': mode_instance.timer,
            'current_turn': mode_instance.current_turn,
            'running': mode_instance.running,
            'winner': mode_instance.winner,
            'history': mode_instance.move_history,
            'events': get_events(session_id)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/move', methods=['POST'])
def move():
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in modes_store:
            return jsonify({'error': 'Game session not found'}), 400

        move_data = request.json.get('move')
        if not move_data or len(move_data) != 4:
            return jsonify({'error': 'Invalid move data'}), 400

        posx, posy, new_posx, new_posy = move_data
        mode_instance = modes_store[session_id]

        # Add turn validation
        piece = mode_instance.board[posx][posy]
        current_color = "Biały" if piece.isupper() else "Czarny"
        if current_color != mode_instance.current_turn:
            return jsonify({'error': 'Not your turn'}), 400

        mode_instance.move_piece([posx, posy], [new_posx, new_posy])
        return jsonify({
            'board': mode_instance.board,
            'timer': mode_instance.timer,
            'current_turn': mode_instance.current_turn,
            'running': mode_instance.running,
            'winner': mode_instance.winner
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/goodMoves', methods=['POST'])
def good_moves():
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in modes_store:
            return jsonify({'error': 'Game session not found'}), 400

        posx = request.json.get('posx')
        posy = request.json.get('posy')
        if posx is None or posy is None:
            return jsonify({'error': 'Invalid position data'}), 400

        mode_instance = modes_store[session_id]
        valid_moves = mode_instance.highlight_moves(posx, posy, 0, None)

        return jsonify({'valid_moves': valid_moves})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/endSession', methods=['POST'])
def end_session():
    try:
        session_id = session.get('session_id')
        if session_id and session_id in modes_store:
            del modes_store[session_id]
            session.pop('session_id', None)
        return jsonify({'status': 'session ended'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/resign', methods=['POST'])
def resign():
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in modes_store:
            return jsonify({'error': 'Game session not found'}), 400

        mode_instance = modes_store[session_id]
        mode_instance.resign()
        return jsonify({
            'board': mode_instance.board,
            'timer': mode_instance.timer,
            'current_turn': mode_instance.current_turn,
            'running': mode_instance.running,
            'winner': mode_instance.winner
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/revert', methods=['POST'])
def revert():
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in modes_store:
            return jsonify({'error': 'Game session not found'}), 400

        mode_instance = modes_store[session_id]
        mode_instance.revert()
        return jsonify({
            'board': mode_instance.board,
            'timer': mode_instance.timer,
            'current_turn': mode_instance.current_turn,
            'running': mode_instance.running,
            'winner': mode_instance.winner
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/draw', methods=['POST'])
def draw():
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in modes_store:
            return jsonify({'error': 'Game session not found'}), 400

        mode_instance = modes_store[session_id]
        mode_instance.draw()
        return jsonify({
            'board': mode_instance.board,
            'timer': mode_instance.timer,
            'current_turn': mode_instance.current_turn,
            'running': mode_instance.running,
            'winner': mode_instance.winner
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/events', methods=['GET'])
def events():
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in modes_store:
            return jsonify({'error': 'Game session not found'}), 400

        events = get_events(session_id)
        return jsonify({'events': events})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/getBoardLook', methods=['GET'])
def get_board_look():
    try:
        mode_name = request.args.get('mode')
        if mode_name not in available_modes:
            mode_name = 'classic'

        mode_instance = available_modes[mode_name](None)
        return jsonify({'board': mode_instance.board})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/customBoardLayout', methods=['POST'])
def custom_board_layout():
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in modes_store:
            return jsonify({'error': 'Game session not found'}), 400

        board_layout = request.json.get('board')
        if not board_layout or len(board_layout) != 8:
            return jsonify({'error': 'Invalid board layout'}), 400
        print('dupa')
        mode_instance = modes_store[session_id]
        mode_instance.board = board_layout
        return jsonify({'board': board_layout})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/listPGNs', methods=['GET'])
def list_pgns():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        folder = os.path.join(base_dir, 'game_data', 'pgn_games')
        pgn_files = [f for f in os.listdir(folder) if f.endswith('.pgn')]
        pgn_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)
        return jsonify({'pgns': pgn_files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/promote', methods=['POST'])
def handle_promotion():
    session_id = session.get('session_id')
    piece = request.json.get('piece')

    mode = modes_store[session_id]
    res = mode.promotion(piece)
    if res is None:
        return jsonify({'error': 'Invalid promotion'}), 400

    return jsonify({'status': 'ok'})

online_games = {}

@app.route('/createOnlineGame', methods=['POST'])
def create_online_game():
    try:
        data = request.json
        mode_name = data.get('game_mode', 'classic')

        if mode_name not in available_modes:
            return jsonify({'error': 'Invalid mode'}), 400

        session_id = session.get('session_id') or os.urandom(12).hex()
        session['session_id'] = session_id

        # Check for existing games with empty slots
        for game_id, game in list(online_games.items()):
            if game.get('player2') is None and game.get('player1') != session_id and game.get('mode_name') == mode_name:
                # Join as player 2
                game['player2'] = session_id

                # Create game instance if not already created
                if 'mode_instance' not in game:
                    mode_instance = available_modes[mode_name](one_player=False, human_color="Biały")
                    mode_instance.session_id = game_id
                    mode_instance.game_mode = mode_name
                    mode_instance.board = mode_instance.initialize_board()
                    modes_store[game_id] = mode_instance
                    game['mode_instance'] = mode_instance

                return jsonify({
                    'session_id': game_id,
                    'role': 'player2',
                    'board': modes_store[game_id].board,
                    'current_turn': modes_store[game_id].current_turn
                })

        # If no game with empty slot was found, create a new one
        mode_instance = available_modes[mode_name](one_player=False, human_color="Biały")
        mode_instance.session_id = session_id
        mode_instance.game_mode = mode_name
        mode_instance.board = mode_instance.initialize_board()
        modes_store[session_id] = mode_instance

        online_games[session_id] = {
            'player1': session_id,
            'player2': None,
            'mode_name': mode_name,
            'mode_instance': mode_instance
        }

        return jsonify({
            'session_id': session_id,
            'role': 'player1',
            'board': mode_instance.board,
            'current_turn': mode_instance.current_turn
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/canGameStart', methods=['GET'])
def can_game_start():
    try:
        session_id = request.args.get('game_id') or session.get('session_id')
        if not session_id or session_id not in online_games:
            return jsonify({'status': 'waiting', 'message': 'Game not found'})

        game = online_games.get(session_id)
        if game.get('player1') is None or game.get('player2') is None:
            return jsonify({'status': 'waiting', 'message': 'Waiting for opponent'})

        # Game is ready to start
        mode_instance = modes_store.get(session_id)
        return jsonify({
            'status': 'ready',
            'board': mode_instance.board,
            'current_turn': mode_instance.current_turn,
            'game_mode': mode_instance.game_mode
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/checkOnlineTurn', methods=['GET'])
def check_online_turn():
    try:
        session_id = request.args.get('game_id') or session.get('session_id')
        if not session_id or session_id not in online_games:
            return jsonify({'error': 'Game not found'}), 400

        game = online_games.get(session_id)
        mode_instance = modes_store.get(session_id)

        # Determine player color based on session id
        is_white = game.get('player1') == session.get('session_id')
        player_turn = "Biały" if is_white else "Czarny"

        return jsonify({
            'is_your_turn': player_turn == mode_instance.current_turn,
            'current_turn': mode_instance.current_turn,
            'board': mode_instance.board,
            'winner': mode_instance.winner,
            'running': mode_instance.running
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
