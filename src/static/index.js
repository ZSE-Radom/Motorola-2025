let popUpCount = 0;

function gameStart(type) {
    if (type === 'offline') {
        fetch('/listModes', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                createPopUp('error', 'Błąd z połączeniem', data.error);
            } else {
                document.getElementById('modeList').style.display = 'block';
                const modeList = document.getElementById('modeBtns');
                modeList.innerHTML = '';
                data.modes.forEach(mode => {
                    const modeButton = document.createElement('button');
                    modeButton.textContent = mode;
                    modeButton.className = 'modeBtn';
                    modeButton.addEventListener('click', () => startOfflineGame(mode));
                    modeList.appendChild(modeButton);
                });
            }
        });
    }
}

function startOfflineGame(mode) {
    document.getElementById('mainmenu').style.display = 'none';
    fetch('/startOffline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            createPopUp('error', 'Błąd z połączeniem', data.error);
        } else {
            document.getElementById('chessGame').style.display = 'flex';
            initStats(data.game_mode, data.game_type, data.first_player_name, data.second_player_name);
            renderChessBoard(data.board, data.timer);
            setInterval(refreshTimer, 500);
        }
    });
}

function renderChessBoard(boardData, time) {
    const chessBoard = document.getElementById('chessBoard');
    const letters = ['H', 'G', 'F', 'E', 'D', 'C', 'B', 'A'];

    chessBoard.innerHTML = '';

    for (let i = 0; i < 8; i++) {
        const row = document.createElement('div');
        row.className = 'row';

        for (let j = 0; j < 8; j++) {
            const square = createSquare(i, j, boardData[i][j], letters);
            row.appendChild(square);
        }

        chessBoard.appendChild(row);
    }

    updateTimers(time);
}

function createSquare(row, col, piece, letters) {
    const square = document.createElement('div');
    const isLightSquare = (row + col) % 2 === 0;

    const pieceImage = document.createElement('img');

    if (piece != '' || piece != ' ' || piece != null || piece != undefined)  {
        if (piece === piece.toUpperCase()) pieceImage.src = `/static/figures/${piece}x.svg`;
        else pieceImage.src = `/static/figures/${piece}.svg`;
    }

    square.className = 'square';
    square.id = row * 8 + col;
    square.style.backgroundColor = isLightSquare ? '#FCF7FF' : '#56876D';
    if (piece != ' ') square.appendChild(pieceImage);

    if (col === 0) {
        const boardNumber = document.createElement('div');
        boardNumber.className = 'boardNumbers';
        boardNumber.style.color = isLightSquare ? '#56876D' : '#FCF7FF';
        boardNumber.textContent = row + 1;
        square.appendChild(boardNumber);
    }

    if (row === 7) {
        const boardLetter = document.createElement('div');
        boardLetter.className = 'boardLetters';
        boardLetter.style.color = isLightSquare ? '#56876D' : '#FCF7FF';
        boardLetter.textContent = letters[col];
        square.appendChild(boardLetter);
    }

    square.addEventListener('click', () => handleSquareClick(row, col));
    return square;
}

function updateTimers(time) {
    document.getElementById('chessTimer1').textContent = time['Biały'];
    document.getElementById('chessTimer2').textContent = time['Czarny'];
}

function handleSquareClick(posx, posy) {
    fetch('/goodMoves', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ posx, posy })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            createPopUp('error', 'Błąd z połączeniem', data.error);
        } else {
            highlightValidMoves(data.valid_moves, posx, posy);
        }
    });
}

function highlightValidMoves(moves, posx, posy) {
    const validMoves = document.getElementsByClassName('validMove');
    while (validMoves.length) {
        validMoves[0].classList.remove('validMove');
    }

    moves.forEach(([newPosx, newPosy]) => {
        const targetSquare = document.getElementById(newPosx * 8 + newPosy);
        targetSquare.classList.add('validMove');
        targetSquare.addEventListener('click', () => executeMove(posx, posy, newPosx, newPosy), { once: true });
    });
}

function executeMove(posx, posy, newPosx, newPosy) {
    fetch('/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ move: [posx, posy, newPosx, newPosy] })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            createPopUp('error', 'Błąd z połączeniem', data.error);
        } else {
            renderChessBoard(data.board, data.timer);
        }
    });
}

function refreshTimer() {
    fetch('/stats')
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            displayErrorPopUp('Błąd z połączeniem', data.error);
        } else {
            if (data.running === true) {
                updateTimers(data.timer);
            } else {
                document.getElementById('chessGame').style.display = 'none';
                document.getElementById('mainmenu').style.display = 'flex';
                createPopUp('info', 'Koniec gry', 'Wygrał gracz ' + data.winner);
            }
            document.getElementById('chessTurn').textContent = 'Tura: ' + data.current_turn;
        }
    });
}

function createPopUp(type, title, content) {
    popUpCount++;

    const popUp = document.createElement('div');
    popUp.className = `popup ${type}`;
    popUp.style.marginTop = `${10 + popUpCount * 10}px`;
    popUp.style.marginRight = `${10}px`;
    popUp.innerHTML = `
        <h3>${title}</h3>
        <p>${content}</p>
        <button onclick="closePopUp(this)">OK</button>
    `;

    document.body.appendChild(popUp);
    popUp.style.display = 'block';

    setTimeout(() => {
        if (popUp.parentNode) {
            popUp.remove();
            popUpCount--;
        }
    }, 5000);
}

function closePopUp(button) {
    const popUp = button.parentNode;
    if (popUp.parentNode) {
        popUp.remove();
        popUpCount--;
    }
}

function initStats(game_mode, game_type, first_player_name, second_player_name) {
    document.getElementById('chessGameType').innerHTML = `Gra ${game_mode}, typ: ${game_type}`;
    document.getElementById('chessName1').textContent = first_player_name;
    document.getElementById('chessName2').textContent = second_player_name;
}

function resign() {
    fetch('/resign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            createPopUp('error', 'Błąd z połączeniem', data.error);
        } else {
            document.getElementById('chessGame').style.display = 'none';
            document.getElementById('mainmenu').style.display = 'flex';
            createPopUp('info', 'Koniec gry', 'Gracz ' + data.winner + ' wygrał, jego przeciwnik się poddał!');
        }
    });
}

function exit() {
    resign();
}

function draw() {
    fetch('/draw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            createPopUp('error', 'Błąd z połączeniem', data.error);
        } else {
            document.getElementById('chessGame').style.display = 'none';
            document.getElementById('mainmenu').style.display = 'flex';
            createPopUp('info', 'Koniec gry', 'Remis!');
        }
    });
}