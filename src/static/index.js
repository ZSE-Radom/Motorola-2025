function gameStart(type) {
    document.getElementById('mainmenu').style.display = 'none';
    if (type === 'offline') {
        let mode = 'classic';
        fetch('/startOffline', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode })
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                document.getElementById('chessGame').style.display = 'flex';
                renderChessBoard(data[0], data[1]);
                setInterval(refreshTimer, 500);
            }
        });
    }
}

function renderChessBoard(boardData, time) {
    const chessBoard = document.getElementById('chessBoard');
    const letters = ['H', 'G', 'F', 'E', 'D', 'C', 'B', 'A'];

    chessBoard.innerHTML = ''; // Clear the board

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
    //if letter of piece is small
    if (piece[0] === piece[0].toLowerCase()) {
        pieceImage.src = `/static/figures/${piece}.svg`;
    } else {
        pieceImage.src = `/static/figures/${piece}x.svg`;
    }
    

    square.className = 'square';
    square.id = row * 8 + col;
    square.style.backgroundColor = isLightSquare ? '#FCF7FF' : '#56876D';
    if (piece !== ' ') square.appendChild(pieceImage);

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
            alert(data.error);
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
            alert(data.error);
        } else {
            renderChessBoard(data[0], data[1]);
        }
    });
}

function refreshTimer() {
    fetch('/stats')
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            if (data[3] == 'true') {
                updateTimers(data[1]);
            } else if (data[3] == 'false') {
                console.log('dddddddddd')
                document.getElementById('chessGame').style.display = 'none';
                document.getElementById('mainmenu').style.display = 'flex';
                alert('Koniec gry! Wygrał gracz ' + data[4]);
            }
            document.getElementById('chessTurn').textContent = 'Tura: ' + data[2];
        }
    });
}

function displayErrorPopUp() {
    const errorPopUp = document.getElementById('errorPopUp');
    errorPopUp.style.display = 'block';
    setTimeout(() => errorPopUp.style.display = 'none', 5000);
}

gameStart('offline');
