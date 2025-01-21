from flask import Flask, render_template, jsonify, request, session
from modes import ClassicMode, BlitzMode, X960Mode
import os

app = Flask(__name__)
app.secret_key = os.urandom(12).hex()

modes_store = {}

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/startOffline', methods=['POST'])
def start_offline():
    mode = request.json['mode']
    if mode == 'classic':
        mode_instance = ClassicMode(None)
    elif mode == 'blitz':
        mode_instance = BlitzMode(None)
    elif mode == '960':
        mode_instance = X960Mode(None)
    else:
        return jsonify({'error': 'Invalid mode'}), 400
    
    session_id = session.get('session_id')
    if not session_id:
        session_id = os.urandom(12).hex()
        session['session_id'] = session_id

    modes_store[session_id] = mode_instance
    mode_instance.web = True

    return jsonify(mode_instance.board, mode_instance.timer, mode_instance.current_turn, mode_instance.running, mode_instance.winner)


@app.route('/stats', methods=['GET'])
def stats():
    session_id = session.get('session_id')
    if not session_id or session_id not in modes_store:
        return jsonify({'error': 'Game session not found'}), 400

    mode_instance = modes_store[session_id]
    return jsonify(mode_instance.board, mode_instance.timer, mode_instance.current_turn, mode_instance.running, mode_instance.winner)


@app.route('/move', methods=['POST'])
def move():
    posx = request.json['move'][0]
    posy = request.json['move'][1]
    new_posx = request.json['move'][2]
    new_posy = request.json['move'][3]

    session_id = session.get('session_id')
    if not session_id or session_id not in modes_store:
        return jsonify({'error': 'Game session not found'}), 400

    mode_instance = modes_store[session_id]
    mode_instance.move_piece([posx, posy], [new_posx, new_posy])

    print(mode_instance.board)

    return jsonify(mode_instance.board, mode_instance.timer, mode_instance.current_turn, mode_instance.running, mode_instance.winner)


@app.route('/goodMoves', methods=['POST'])
def good_moves():
    posx = request.json['posx']
    posy = request.json['posy']

    session_id = session.get('session_id')
    if not session_id or session_id not in modes_store:
        return jsonify({'error': 'Game session not found'}), 400

    mode_instance = modes_store[session_id]
    valid_moves = mode_instance.highlight_moves(posx, posy, None)

    return jsonify({'valid_moves': valid_moves})


@app.route('/endSession', methods=['POST'])
def end_session():
    session_id = session.get('session_id')
    if session_id and session_id in modes_store:
        del modes_store[session_id]
        session.pop('session_id', None)
    return jsonify({'status': 'session ended'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
