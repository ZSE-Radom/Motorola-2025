from flask import Flask, render_template, jsonify, request
from modes import ClassicMode, BlitzMode, X960Mode

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/startOffline', methods=['GET', 'POST'])
def start_offline():
    mode = request.json['mode']
    if mode == 'classic':
        mode = ClassicMode(None)
    elif mode == 'blitz':
        mode = BlitzMode(None)
    elif mode == '960':
        mode = X960Mode(None)
    else:
        return jsonify('error')
    return jsonify(mode.board, mode.timer)

@app.route('/goodMoves', methods=['GET', 'POST'])
def good_moves():
    posx = request.json['posx']
    posy = request.json['posy']
    
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)