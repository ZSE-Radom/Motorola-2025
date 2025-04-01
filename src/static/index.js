let popUpCount = 0;
let setupOptions = {};
let currentlyPlaying = false;
let boardInitialized = false;
let mutePopups = false;
let performing_move = false;
let boardAltered = false;
let editMode = false;
let pfpsrclist = ['/static/profiles/1.png', '/static/profiles/2.png', '/static/profiles/3.png', '/static/profiles/4.png', '/static/profiles/5.png', '/static/profiles/6.png', '/static/profiles/7.png', '/static/profiles/8.png', '/static/profiles/9.png', '/static/profiles/10.png', '/static/profiles/11.png', '/static/profiles/12.png', '/static/profiles/a_8f428c9540cd76b2a6d8a727db98cee7.png', '/static/profiles/8715642fbbded8333534042f40a2a3e4.png']
let rInterval = null;
let currentPlayer = null;

function getCustomBoardData() {
    const boardData = [];
    const chessBoard = document.getElementById('chessBoardContainer');
    const rows = chessBoard.querySelectorAll('.row');

    rows.forEach(row => {
        const rowData = [];
        const squares = row.querySelectorAll('.square');
        squares.forEach(square => {
            const pieceImg = square.querySelector('img.piece');
            if (pieceImg) {
                let piece = pieceImg.src.split('/').pop().replace('.svg', '');
                if (piece.endsWith('x')) {
                    piece = piece.slice(0, -1).toUpperCase();
                }
                rowData.push(piece);
            } else {
                rowData.push('');
            }
        });
        boardData.push(rowData);
    });

    return boardData;
}

function unsetIntervals() {
    clearInterval(rInterval);
    //clearInterval(checkForEvents);
}

function renderSetup(game_type) {
    let boardData;
    editMode = true;
    loadProfiles();
    document.getElementById('chessBoardEditor').style.display = 'block';
    if (game_type === 'human') {
        document.getElementById('chessStats').style.display = 'none';
        document.getElementById('chessSocial').style.display = 'none';
        document.getElementById('chessSetupHuman').style.display = 'none';
        document.getElementById('chessSetupBot').style.display = 'none';
        document.getElementById('chessSetupGM').style.display = 'none';
        document.getElementById('chessBoard').style.display = 'none';
        animateMainMenu('close');
        fetch('/getBoardLook', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        }).then(res => res.json())
        .then(data => {
            if (data.error) {
                createPopUp('error', 'Błąd z połączeniem', data.error);
            } else {
                boardData = data.board;
                initChessBoard(boardData, 0);
                const options = ["Na tym komputerze (gra offline)", "Na innym komputerze (gra online)"];
                const colors = ["#FC6471", "#7D5BA6"];
                const toggle = document.getElementById("toggle");
                const slider = toggle.querySelector(".slider");
                const labelsContainer = toggle.querySelector(".labels");
                setupOptions['game_type'] = 'offline';

                toggle.style.setProperty("--options", options.length);

                labelsContainer.innerHTML = '';

                options.forEach((option, index) => {
                    const label = document.createElement("span");
                    label.textContent = option;
                    label.dataset.index = index;
                    labelsContainer.appendChild(label);
                });

                let currentIndex = 0;
                function updateSlider() {
                    slider.style.left = `${(100 / options.length) * currentIndex}%`;
                    slider.style.background = colors[currentIndex];
                }

                let canOnlineStart = false;

                toggle.addEventListener("click", () => {
                    currentIndex = (currentIndex + 1) % options.length;
                    updateSlider();
                    if (currentIndex === 0) {
                        setupOptions['game_type'] = 'offline';
                    } else if (currentIndex === 1) {
                        setupOptions['game_type'] = 'online';

                        fetch('/createOnlineGame', {
                            method: 'POST',
                            body: JSON.stringify({ setupOptions }),
                            headers: { 'Content-Type': 'application/json' },
                        }).then(res => res.json())
                        .then(data => {
                            if (data.error) {
                                createPopUp('error', 'Błąd z połączeniem', data.error);
                            } else {
                                createPopUp('info', 'Gra online', 'Gra online została utworzona! Oczekiwanie na drugiego gracza...');
                                fetch('/canGameStart', {
                                    method: 'GET',
                                    headers: { 'Content-Type': 'application/json' },
                                }).then(res => res.json())
                                .then(data => {
                                    if (data.error) {
                                        createPopUp('error', 'Błąd z połączeniem', data.error);
                                    } else {
                                        if (data.ready) {
                                            createPopUp('info', 'Gra online', 'Drugi gracz dołączył! Rozpocznij grę!');
                                            canOnlineStart = true;
                                        } else {
                                            createPopUp('info', 'Gra online', 'Oczekiwanie na drugiego gracza...');
                                        }
                                    }
                                });
                            }
                        });
                    }
                });

                fetch('/listModes', {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' },
                }).then(res => res.json())
                .then(data => {
                    console.log(data);
                    if (data.error) {
                        createPopUp('error', 'Błąd z połączeniem', data.error);
                    } else {
                        document.getElementById('chessSetupField2Content').innerHTML = '';
                        for (const mode of data.modes) {
                            const modeButton = document.createElement('button');
                            modeButton.textContent = mode;
                            modeButton.className = 'modeBtn';
                            document.getElementById('chessSetupField2Content').appendChild(modeButton);
                            modeButton.onclick = function() {
                                setupOptions['game_mode'] = mode;
                                modeButton.classList.add('active');
                                for (const child of modeButton.parentNode.children) {
                                    if (child !== modeButton) {
                                        child.classList.remove('active');
                                    }
                                }
                            }
                        }
                    }
                });

                updateSlider();
                setTimeout(() => {
                    document.getElementById('mainmenu').style.display = 'none';
                    document.getElementById('chessGame').style.display = 'flex';
                    document.getElementById('chessSetupHuman').style.display = 'block';
                    document.getElementById('chessBoard').style.display = 'flex';
                    animateChessBoard('setup');
                }, 1500);

                document.getElementById('chessGameStartButton').onclick = function() {
                    if (setupOptions['game_mode'] != 'online') {
                        if (boardAltered) {
                            setupOptions['custom_board'] = getCustomBoardData();
                        } else {
                            setupOptions['custom_board'] = null;
                        }
                        setupOptions['allow_for_revert'] = document.getElementById('allowUndo').checked;
                        if (setupOptions['game_mode'] === undefined) {
                            createPopUp('error', 'Błąd', 'Wybierz tryb gry!');
                        } else {
                            fetch('/startOffline', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify(setupOptions)
                            })
                            .then(res => res.json())
                            .then(data => {
                                editMode = false;
                                document.getElementById('chessBoardEditor').style.display = 'none';
                                if (data.error) {
                                    createPopUp('error', 'Błąd z połączeniem', data.error);
                                } else {

                                    document.getElementById('chessSetupHuman').animate([
                                        { transform: 'translateY(0)' },
                                        { transform: 'translateY(-100%)' }
                                    ], {
                                        duration: 1000,
                                        easing: 'ease-in-out'
                                    });
                                    document.getElementById('chessBoard').animate([
                                        { transform: 'translateX(0)' },
                                        { transform: 'translateX(-25%)' }
                                    ], {
                                        duration: 1000,
                                        easing: 'ease-in-out'
                                    });
                                    setTimeout(() => {
                                        document.getElementById('chessSetupHuman').style.display = 'none';
                                        document.getElementById('chessSetupGM').style.display = 'none';
                                        document.getElementById('chessSetupBot').style.display = 'none';
                                        document.getElementById('chessGame').style.display = 'flex';
                                        document.getElementById('chessSocial').style.display = 'block';
                                        document.getElementById('chessStats').style.display = 'block';
                                        initStats(data.game_mode, data.game_type, data.first_player_name, data.second_player_name);
                                        initChessBoard(data.board, data.timer);
                                        rInterval = setInterval(refreshTimer, 500);
                                        //setInterval(checkForEvents, 500);
                                    }, 1000);
                                }
                            });
                        }
                    } else if (setupOptions['game_type'] === 'online') {
                        if (canOnlineStart) {
                        if (boardAltered) {
                            setupOptions['custom_board'] = getCustomBoardData();
                        } else {
                            setupOptions['custom_board'] = null;
                        }
                        setupOptions['allow_for_revert'] = document.getElementById('allowUndo').checked;
                            if (setupOptions['game_mode'] === undefined) {
                                createPopUp('error', 'Błąd', 'Wybierz tryb gry!');
                            } else {
                                fetch('/startOnline', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify(setupOptions)
                                })
                                .then(res => res.json())
                                .then(data => {
                                    if (data.error) {
                                        createPopUp('error', 'Błąd z połączeniem', data.error);
                                    } else {
                                        editMode = false;
                                        document.getElementById('chessBoardEditor').style.display = 'none';
                                        document.getElementById('chessGame').style.display = 'flex';
                                        document.getElementById('chessSocial').style.display = 'block';
                                        document.getElementById('chessStats').style.display = 'block';
                                        initStats(data.game_mode, data.game_type, data.first_player_name, data.second_player_name);
                                        initChessBoard(data.board, data.timer);
                                        rInterval = setInterval(refreshTimer, 500);
                                        //setInterval(checkForEvents, 500);
                                    }
                                });
                            }
                        }
                    }
                }
            }
        });
    } else if (game_type === 'bot') {
        document.getElementById('chessStats').style.display = 'none';
        document.getElementById('chessSocial').style.display = 'none';
        document.getElementById('chessSetupHuman').style.display = 'none';
        document.getElementById('chessSetupBot').style.display = 'none';
        document.getElementById('chessSetupGM').style.display = 'none';
        document.getElementById('chessBoard').style.display = 'none';
        animateMainMenu('close');
        fetch('/getBoardLook', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        }).then(res => res.json())
        .then(data => {
            if (data.error) {
                createPopUp('error', 'Błąd z połączeniem', data.error);
            } else {
                boardData = data.board;
                initChessBoard(boardData, 0);
                const botDifficulties = ["Łatwy (SochAI)", "Średni (mAItiuu)", "Trudny (MuchAI)"];
                const colors = ["#FC6471", "#FFD700", "#7D5BA6"];
                const toggle = document.getElementById("toggleBot");
                const slider = toggle.querySelector(".slider");
                const labelsContainer = toggle.querySelector(".labels");
                setupOptions['bot_mode'] = 'easy';

                toggle.style.setProperty("--options", botDifficulties.length);

                labelsContainer.innerHTML = '';

                botDifficulties.forEach((difficulty, index) => {
                    const label = document.createElement("span");
                    label.textContent = difficulty;
                    label.dataset.index = index;
                    labelsContainer.appendChild(label);
                });

                let currentIndex = 0;
                function updateSlider() {
                    slider.style.left = `${(100 / botDifficulties.length) * currentIndex}%`;
                    slider.style.background = colors[currentIndex];
                }

                toggle.addEventListener("click", () => {
                    currentIndex = (currentIndex + 1) % botDifficulties.length;
                    updateSlider();
                    if (currentIndex === 0) {
                        setupOptions['bot_mode'] = 'easy';
                        document.getElementById('chessName2').src = 'SochAI (Łatwy)';
                        document.getElementById('chessPfp2').src = pfpsrclist[Math.floor(Math.random() * pfpsrclist.length)];
                    } else if (currentIndex === 1) {
                        setupOptions['bot_mode'] = 'medium';
                        document.getElementById('chessName2').src = 'mAItiuu (Średni)';
                        document.getElementById('chessPfp2').src = pfpsrclist[Math.floor(Math.random() * pfpsrclist.length)];
                    } else if (currentIndex === 2) {
                        setupOptions['bot_mode'] = 'hard';
                        document.getElementById('chessName2').src = 'MuchAI (Trudny)';
                        document.getElementById('chessPfp2').src = pfpsrclist[Math.floor(Math.random() * pfpsrclist.length)];
                    }
                    // TODO bot może być tylko czarny :(
                });

                updateSlider();
                setTimeout(() => {
                    document.getElementById('mainmenu').style.display = 'none';
                    document.getElementById('chessGame').style.display = 'flex';
                    document.getElementById('chessSetupBot').style.display = 'block';
                    document.getElementById('chessBoard').style.display = 'flex';
                    animateChessBoard('setupBot');
                }, 1500);

                document.getElementById('chessGameStartButtonBot').onclick = function() {
                    if (boardAltered) {
                        setupOptions['custom_board'] = getCustomBoardData();
                    } else {
                        setupOptions['custom_board'] = null;
                    }
                    setupOptions['game_mode'] = 'classic'; // Default mode for bot
                    setupOptions['one_player'] = true; // TODO
                    fetch('/startOffline', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(setupOptions)
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.error) {
                            createPopUp('error', 'Błąd z połączeniem', data.error);
                        } else {
                            editMode = false;
                            document.getElementById('chessBoardEditor').style.display = 'none';
                            if (setupOptions['bot_mode'] === 'easy') {
                                document.getElementById('chessName2').textContent = 'SochAI (Łatwy)';
                                document.getElementById('chessPfp2').src = pfpsrclist[Math.floor(Math.random() * pfpsrclist.length)];
                            } else if (setupOptions['bot_mode'] === 'medium') {
                                console.log('medium');
                                document.getElementById('chessName2').textContent = 'mAItiuu (Średni)';
                                document.getElementById('chessPfp2').src = pfpsrclist[Math.floor(Math.random() * pfpsrclist.length)];
                            } else if (setupOptions['bot_mode'] === 'hard') {
                                document.getElementById('chessName2').textContent = 'MuchAI (Trudny)';
                                document.getElementById('chessPfp2').src = pfpsrclist[Math.floor(Math.random() * pfpsrclist.length)];
                            }
                            document.getElementById('chessSetupBot').animate([
                                { transform: 'translateY(0)' },
                                { transform: 'translateY(-100%)' }
                            ], {
                                duration: 1000,
                                easing: 'ease-in-out'
                            });
                            document.getElementById('chessBoard').animate([
                                { transform: 'translateX(0)' },
                                { transform: 'translateX(-25%)' }
                            ], {
                                duration: 1000,
                                easing: 'ease-in-out'
                            });
                            setTimeout(() => {

                                document.getElementById('chessSetupBot').style.display = 'none';
                                document.getElementById('chessGame').style.display = 'flex';
                                document.getElementById('chessSocial').style.display = 'block';
                                document.getElementById('chessStats').style.display = 'block';
                                initStats(data.game_mode, data.game_type, data.first_player_name, data.second_player_name);
                                initChessBoard(data.board, data.timer);
                                rInterval = setInterval(refreshTimer, 500);
                                //setInterval(checkForEvents, 500);
                            }, 1000);
                        }
                    });
                }
            }
        });
    } else if (game_type === 'gm') {
        editMode = false;
        document.getElementById('chessBoardEditor').style.display = 'none';
        document.getElementById('chessStats').style.display = 'none';
        document.getElementById('chessSocial').style.display = 'none';
        document.getElementById('chessSetupHuman').style.display = 'none';
        document.getElementById('chessSetupBot').style.display = 'none';
        document.getElementById('chessSetupGM').style.display = 'none';
        document.getElementById('chessBoard').style.display = 'none';

        animateMainMenu('close');
        fetch('/getBoardLook', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        }).then(res => res.json())
        .then(data => {
            if (data.error) {
                createPopUp('error', 'Błąd z połączeniem', data.error);
            } else {
                boardData = data.board;
                initChessBoard(boardData, 0);

                pgns_list = document.getElementById('chessSetupField10Content');

                fetch('/listPGNs', {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' },
                }).then(res => res.json())
                .then(data => {
                    if (data.error) {
                        createPopUp('error', 'Błąd z połączeniem', data.error);
                    } else {
                        pgns_list.innerHTML = '';
                        for (const pgn of data.pgns) {
                            const pgnButton = document.createElement('button');
                            pgnButton.textContent = pgn;
                            pgnButton.className = 'modeBtn';
                            pgnButton.classList.add('pgnBtn');
                            pgns_list.appendChild(pgnButton);
                            pgnButton.onclick = function() {
                                setupOptions['pgn'] = pgn;
                                pgnButton.classList.add('active');
                                for (const child of pgnButton.parentNode.children) {
                                    if (child !== pgnButton) {
                                        child.classList.remove('active');
                                    }
                                }
                            }
                        }
                    }
                });

                setTimeout(() => {
                    document.getElementById('mainmenu').style.display = 'none';
                    document.getElementById('chessGame').style.display = 'flex';
                    document.getElementById('chessSetupGM').style.display = 'block';
                    document.getElementById('chessBoard').style.display = 'flex';
                    animateChessBoard('setupGM');
                }, 1500);

                document.getElementById('chessGameStartButtonGM').onclick = function() {

                setupOptions['gm_name'] = document.querySelector('.pgnBtn.active')?.textContent || null;
                setupOptions['game_mode'] = 'gm';
                setupOptions['one_player'] = true; // TODO
                    fetch('/startOffline', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(setupOptions)
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.error) {
                            createPopUp('error', 'Błąd z połączeniem', data.error);
                        } else {
                            editMode = false;
                            document.getElementById('chessBoardEditor').style.display = 'none';
                            document.getElementById('chessSetupGM').animate([
                                { transform: 'translateY(0)' },
                                { transform: 'translateY(-100%)' }
                            ], {
                                duration: 1000,
                                easing: 'ease-in-out'
                            });
                            document.getElementById('chessBoard').animate([
                                { transform: 'translateX(0)' },
                                { transform: 'translateX(-25%)' }
                            ], {
                                duration: 1000,
                                easing: 'ease-in-out'
                            });
                            setTimeout(() => {
                                console.log('ddd')
                                document.getElementById('chessSetupGM').style.display = 'none';
                                document.getElementById('chessGame').style.display = 'flex';
                                document.getElementById('chessSocial').style.display = 'block';
                                document.getElementById('chessStats').style.display = 'block';
                                initStats(data.game_mode, data.game_type, data.first_player_name, data.second_player_name);
                                initChessBoard(data.board, data.timer);
                                rInterval = setInterval(refreshTimer, 500);
                                //setInterval(checkForEvents, 500);
                            }, 1000);
                        }
                    });
                }
            }
        });
    }
}

function updateChessBoard(boardData) {
    for (let i = 0; i < 8; i++) {
        for (let j = 0; j < 8; j++) {
            const squareId = i * 8 + j;
            const square = document.getElementById(squareId);
            const newPiece = boardData[i][j] ? boardData[i][j].trim() : '';
            const currentPiece = square.dataset.piece || '';

            if (currentPiece !== newPiece) {
                square.dataset.piece = newPiece;

                const pieceImg = square.querySelector('img.piece');

                if (newPiece === '') {
                    if (pieceImg) {
                        pieceImg.remove();
                    }
                } else {
                    let src;
                    if (newPiece === newPiece.toUpperCase()) {
                        src = `/static/figures/${newPiece}x.svg`;
                    } else {
                        src = `/static/figures/${newPiece}.svg`;
                    }

                    if (pieceImg) {
                        pieceImg.src = src;
                    } else {
                        const newImg = document.createElement('img');
                        newImg.className = 'piece';
                        newImg.src = src;
                        square.insertBefore(newImg, square.firstChild);
                    }
                }
            }
        }
    }
}

  function initChessBoard(boardData) {
    document.getElementById('chessGame').style.display = 'flex';
    const chessBoard = document.getElementById('chessBoardContainer');
    const letters = ['H', 'G', 'F', 'E', 'D', 'C', 'B', 'A'];

    chessBoard.innerHTML = '';

    for (let i = 0; i < 8; i++) {
      const row = document.createElement('div');
      row.className = 'row';

      for (let j = 0; j < 8; j++) {
        const square = document.createElement('div');
        square.className = 'square';
        square.id = i * 8 + j;
        square.dataset.piece = boardData[i][j] ? boardData[i][j].trim() : '';

        const isLightSquare = (i + j) % 2 === 0;
        square.style.backgroundColor = isLightSquare ? '#FCF7FF' : '#56876D';

        if (square.dataset.piece !== '') {
          const pieceImage = document.createElement('img');
          pieceImage.className = 'piece';
          const piece = square.dataset.piece;
          if (piece === piece.toUpperCase()) {
            pieceImage.src = `/static/figures/${piece}x.svg`;
          } else {
            pieceImage.src = `/static/figures/${piece}.svg`;
          }
          square.appendChild(pieceImage);
        }

        if (j === 0) {
          const boardNumber = document.createElement('div');
          boardNumber.className = 'boardNumbers';
          boardNumber.style.color = isLightSquare ? '#56876D' : '#FCF7FF';
          boardNumber.textContent = i + 1;
          square.appendChild(boardNumber);
        }

        if (i === 7) {
          const boardLetter = document.createElement('div');
          boardLetter.className = 'boardLetters';
          boardLetter.style.color = isLightSquare ? '#56876D' : '#FCF7FF';
          boardLetter.textContent = letters[j];
          square.appendChild(boardLetter);
        }

        square.addEventListener('click', () => handleSquareClick(i, j));
        row.appendChild(square);
      }

      chessBoard.appendChild(row);
    }

    const squares = document.querySelectorAll('.square');

    squares.forEach(square => {
        square.addEventListener('dragover', handleDragOver);
        square.addEventListener('drop', handleDrop);
        square.addEventListener('dragstart', handleDragStart);
    });
    document.querySelectorAll('#piecePalette img').forEach(piece => {
        piece.addEventListener('dragstart', handlePaletteDragStart);
    });

    document.addEventListener('dragend', handleDragEnd);

    boardInitialized = true;
    boardAltered = false;
}
let movedPiece = null;
let fromPalette = false;
let originalSquare = null;

function handleDragOver(event) {
    if (!editMode) return; // Check if in edit mode
    let warningSetup = document.getElementsByClassName('warningSetup');
    for (const el of warningSetup) {
        el.style.display = 'block';
    }
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
}

function handleDrop(event) {
    if (!editMode) return; // Check if in edit mode
    event.preventDefault();
    const piece = event.dataTransfer.getData('text/plain');
    const targetSquare = event.target.closest('.square');

    if (targetSquare) {
        const existingPiece = targetSquare.querySelector('img.piece');
        if (existingPiece) {
            existingPiece.remove();
        }

        const newPieceImg = document.createElement('img');
        newPieceImg.className = 'piece';
        let pieceName = piece.split('/').pop().replace('.svg', '').replace('x', '');
        if (piece.endsWith('x.svg')) {
            pieceName = pieceName.toUpperCase()
        }
        newPieceImg.src = pieceName === pieceName.toUpperCase()
            ? `/static/figures/${pieceName}x.svg`
            : `/static/figures/${pieceName}.svg`;
        newPieceImg.dataset.piece = piece;

        targetSquare.appendChild(newPieceImg);

        boardAltered = true;

        // Remove the piece from the original square if it exists
        if (originalSquare && originalSquare !== targetSquare) {
            const originalPiece = originalSquare.querySelector('img.piece');
            if (originalPiece) {
                originalPiece.remove();
            }
        }
    } else if (movedPiece && !fromPalette) {
        // If dropped outside the board and not from the palette, remove the piece
        movedPiece.remove();
    }

    // If moving from chessBoard or square instance, remove old instance
    if (originalSquare && originalSquare !== targetSquare) {
        const oldPiece = originalSquare.querySelector('img.piece');
        if (oldPiece) {
            oldPiece.remove();
        }
        originalSquare = null; // Reset original square only after removing the old piece
    }
}

function handleDragStart(event) {
    if (!editMode) return; // Check if in edit mode
    const piece = event.target.src;
    if (piece) {
        event.dataTransfer.setData('text/plain', piece);
        event.dataTransfer.effectAllowed = 'move';
        movedPiece = event.target;
        fromPalette = false; // Reset flag
        originalSquare = event.target.closest('.square'); // Track the original square
    }
}

function handlePaletteDragStart(event) {
    if (!editMode) return; // Check if in edit mode
    const piece = event.target.src;
    if (piece) {
        event.dataTransfer.setData('text/plain', piece);
        event.dataTransfer.effectAllowed = 'move';
        event.dataTransfer.setDragImage(event.target, 0, 0);
        fromPalette = true; // Mark as from palette
        originalSquare = null; // Reset original square
    }
}

function handleDragEnd(event) {
    if (!editMode) return; // Check if in edit mode
    const targetElement = document.elementFromPoint(event.clientX, event.clientY);
    const targetSquare = targetElement?.closest('.square');

    if (!targetSquare && movedPiece) {
        if (fromPalette) {
            // If from palette, do nothing (allow adding multiple pieces)
        } else {
            // If not from palette, remove the piece
            movedPiece.remove();
        }
        movedPiece = null;
    }
}

function updateTimers(time) {
    document.getElementById('chessTimer1').textContent = time['Biały'];
    document.getElementById('chessTimer2').textContent = time['Czarny'];
}

function handleSquareClick(posx, posy) {
    if (editMode) return;
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
        validMoves[0].onclick = null;
    }

    if (!moves?.length) return;

    moves.forEach(([newPosx, newPosy]) => {
        const targetSquare = document.getElementById(newPosx * 8 + newPosy);
        targetSquare.classList.add('validMove');
        targetSquare.onclick = function () {executeMove(posx, posy, newPosx, newPosy)}
    });
}

function executeMove(posx, posy, newPosx, newPosy) {
    if (performing_move) {
        console.log('blocked double move');
        return
    }
    const chessBoard = document.getElementById('chessBoardContainer');
    chessBoard.style.pointerEvents = 'none'; // Disable input
    performing_move = true;
    fetch('/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ move: [posx, posy, newPosx, newPosy] })
    })
    .then(res => res.json())
    .then(() => {
        //updateChessBoard(data.board);
        chessBoard.style.pointerEvents = 'auto'; // Re-enable
        performing_move = false;
    })
    .catch(error => {
        chessBoard.style.pointerEvents = 'auto';
        createPopUp('error', 'Błąd', error.message);
        performing_move = false;
    }).finally(() => {
        performing_move = false;
    })
}

function refreshTimer() {
    fetch('/stats')
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          createPopUp('error', 'Błąd z połączeniem', data.error);
            document.getElementById('chessGame').style.display = 'none';
            document.getElementById('mainmenu').style.display = 'block';
            animateMainMenu('open');
            unsetIntervals();
        } else {
          if (data.running === true) {
            if (!boardInitialized) {
              initChessBoard(data.board);
            } else {
              updateChessBoard(data.board);
            }
            updateTimers(data.timer);
            animateChessBoard('game');
          }

            currentPlayer = data.current_turn;

          if (!data.events) {
            return;
            }

        let events = Array.isArray(data.events) ? data.events : [data.events];

        for (const event of events) {
            const played = localStorage.getItem('played')
            switch(event) {
                case 'resign':
                    handleGameEnd('Koniec gry', 'Gracz się poddał!');
                    if (played) {
                        const playedCount = parseInt(played) + 1;
                        localStorage.setItem('played', playedCount.toString());
                    }
                    break;
                case 'draw':
                    handleGameEnd('Koniec gry', 'Remis!');
                    if (played) {
                        const playedCount = parseInt(played) + 1;
                        localStorage.setItem('played', playedCount.toString());
                    }
                    break;
                case 'time_over':
                    handleGameEnd('Koniec gry', 'Czas się skończył!');
                    if (played) {
                        const playedCount = parseInt(played) + 1;
                        localStorage.setItem('played', playedCount.toString());
                    }
                    break;
                case 'end':
                    handleGameEnd('Koniec gry', 'Gra została zakończona!');
                    if (played) {
                        const playedCount = parseInt(played) + 1;
                        localStorage.setItem('played', playedCount.toString());
                    }
                    break;
                case 'check':
                    createPopUp('info', 'Szach!', 'Twój król jest atakowany!');
                    break;
                case 'promotion':
                    handlePromotion();
                    break;
                case 'bot_move_begin':
                    document.body.style.cursor = 'wait';
                    break;
                case 'bot_move_finish':
                    document.body.style.cursor = 'default';
                    break;
                default:
                    createPopUp('info', 'Zdarzenie', event);
            }
        }
          document.getElementById('chessLog').innerHTML = data.history;
          document.getElementById('chessTurn').textContent = 'Tura: ' + data.current_turn;
        }
      });
  }

function createPopUp(type, title, content) {
    if (mutePopups) return;
    document.getElementById('notifySound').play();
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
            popUp.style.animation = 'slideleft-popup 1s cubic-bezier(0.075, 0.82, 0.165, 1)';
            setTimeout(() => {
                popUp.remove();
                popUpCount--;
            }, 900);
        }
    }, 5000);
}

function closePopUp(button) {
    const popUp = button.parentNode;
    if (popUp.parentNode) {
        popUp.style.animation = 'slideleft-popup 1s cubic-bezier(0.075, 0.82, 0.165, 1)';
        setTimeout(() => {
            popUp.remove();
            popUpCount--;
        }, 900);
    }
}

function initStats(game_mode, game_type) {
    document.getElementById('chessGameType').innerHTML = `Gra ${game_mode}, typ: ${game_type}`;
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
            boardInitialized = false;
            return 'OK';
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
            boardInitialized = false;
            return 'OK';
        }
    });
}

function closeModes() {
    document.getElementById('modeList').style.display = 'none';
    const collection = document.getElementsByClassName("active");
    for (const c of collection) {
        c.classList.remove('active');
    }
}

function handleGameEnd(title, message) {
    animateChessBoard('close');
    setTimeout(() => {
        document.getElementById('chessGame').style.display = 'none';
        animateMainMenu('open');
        document.getElementById('mainmenu').style.display = 'block';
        createPopUp('info', title, message);
        unsetIntervals();
    }, 1500);
}

function handlePromotion() {
    document.getElementById('chessPromotionQueen').children.item(0).src = `/static/figures/q${currentPlayer === "Biały" ? 'x' : ''}.svg`;
    document.getElementById('chessPromotionRook').children.item(0).src = `/static/figures/r${currentPlayer === "Biały" ? 'x' : ''}.svg`;
    document.getElementById('chessPromotionBishop').children.item(0).src = `/static/figures/b${currentPlayer === "Biały" ? 'x' : ''}.svg`;
    document.getElementById('chessPromotionKnight').children.item(0).src = `/static/figures/n${currentPlayer === "Biały" ? 'x' : ''}.svg`;

    document.getElementById("chessPromotion").style.display = "flex";
}

function promotion(piece) {
    document.getElementById("chessPromotion").style.display = "none";
    fetch('/promote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            piece: piece,
        })
    }).then(data => {
        if (data.status !== 200) {
            createPopUp('error', 'Wystąpił błąd podczas promocji', data.error);
            return;
        }
        createPopUp('info', 'Promocja', 'Pionek został promowany!');
    })
}

const slider = document.querySelector('#feed');
let mouseDown = false;
let startX, scrollLeft;
let startDragging = function (e) {
    mouseDown = true;
    startX = e.pageX - slider.offsetLeft;
    scrollLeft = slider.scrollLeft;
};

let stopDragging = function () {
    mouseDown = false;
};

slider.addEventListener('mousemove', (e) => {
    e.preventDefault();  if(!mouseDown) {
        return;
    }
    const x = e.pageX - slider.offsetLeft;
    const scroll = x - startX;
    slider.scrollLeft = scrollLeft - scroll;
});

slider.addEventListener('mousedown', startDragging, false);
slider.addEventListener('mouseup', stopDragging, false);
slider.addEventListener('mouseleave', stopDragging, false);


window.onload = function(){
    document.getElementById('loading').style.opacity = '0';
    loadProfiles();
    animateMainMenu('open');
    setTimeout(() => {
        playSoundtrack();
        document.getElementById('loading').style.display = 'none';
    }, 2000);
};

function animateMainMenu(type) {
    if (type === 'open') {
        document.getElementById('header').style.animation = "slideup-center 1.6s cubic-bezier(0.075, 0.82, 0.165, 1)";
        document.getElementById('gameModes').style.animation = "slideup-center 2.4s cubic-bezier(0.075, 0.82, 0.165, 1)";
        document.getElementById('feed').style.animation = "slideup-center 3.2s cubic-bezier(0.075, 0.82, 0.165, 1)";
        document.getElementById('bottomButtons').style.animation = "slideup-center 4s cubic-bezier(0.075, 0.82, 0.165, 1)";
        document.getElementById('modeList').style.animation = "slideup-translate-center 1.5s cubic-bezier(0.075, 0.82, 0.165, 1)";
    } else if (type === 'close') {
        document.getElementById('header').style.animation = "slidedown-center 1.6s cubic-bezier(0.075, 0.82, 0.165, 1)";
        document.getElementById('gameModes').style.animation = "slidedown-center 2.4s cubic-bezier(0.075, 0.82, 0.165, 1)";
        document.getElementById('feed').style.animation = "slidedown-center 3.2s cubic-bezier(0.075, 0.82, 0.165, 1)";
        document.getElementById('bottomButtons').style.animation = "slidedown-center 4s cubic-bezier(0.075, 0.82, 0.165, 1)";
        document.getElementById('modeList').style.animation = "slidedown-translate-center 1.5s cubic-bezier(0.075, 0.82, 0.165, 1)";
    }
}

function animateChessBoard(type) {
    if (type === 'game') {
        document.getElementById('chessSocial').style.animation = "slideup-center 3s cubic-bezier(0.075, 0.82, 0.165, 1)";
        document.getElementById('chessStats').style.animation = "slideup-center 3s cubic-bezier(0.075, 0.82, 0.165, 1)";
        document.getElementById('chessSocial').style.display = 'block';
        document.getElementById('chessStats').style.display = 'block';
    } else if (type === 'setup') {
        document.getElementById('chessSetupHuman').style.animation = "slideup-center 3s cubic-bezier(0.075, 0.82, 0.165, 1)";
        document.getElementById('chessBoard').style.animation = "slideup-center 2s cubic-bezier(0.075, 0.82, 0.165, 1)";
    } else if (type === 'setupBot') {
        document.getElementById('chessSetupBot').style.animation = "slideup-center 3s cubic-bezier(0.075, 0.82, 0.165, 1)";
        document.getElementById('chessBoard').style.animation = "slideup-center 2s cubic-bezier(0.075, 0.82, 0.165, 1)";
    } else if (type === 'setupGM') {
        document.getElementById('chessSetupGM').style.animation = "slideup-center 3s cubic-bezier(0.075, 0.82, 0.165, 1)";
        document.getElementById('chessBoard').style.animation = "slideup-center 2s cubic-bezier(0.075, 0.82, 0.165, 1)";
    } else if (type === 'close') {
        document.getElementById('chessSocial').style.animation = "slidedown-center 3s cubic-bezier(0.075, 0.82, 0.165, 1)";
        document.getElementById('chessBoard').style.animation = "slidedown-center 2s cubic-bezier(0.075, 0.82, 0.165, 1)";
        document.getElementById('chessStats').style.animation = "slidedown-center 3s cubic-bezier(0.075, 0.82, 0.165, 1)";
    }
}

function back() {
    // revert move on server
    fetch('/revert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            createPopUp('error', 'Błąd z połączeniem', data.error);
        } else {
            return 'OK';
        }
    }
    );
}


const songs = ['Ballada o Stańczyku', 'Electric Heart', 'F-Cloud Song', 'ITwist', 'Jawor', 'Serwer Patyny', 'Srochaj Anime Opening', 'ZSE Theme Song'];
let currentSongIndex = Math.floor(Math.random() * songs.length);
const audio = new Audio(`/static/soundtrack/${songs[currentSongIndex]}.mp3`);
audio.loop = false;

function playSoundtrack() {
    audio.play();
    nowPlaying(songs[currentSongIndex]);

    audio.addEventListener('ended', () => {
        let newSongIndex;
        do {
            newSongIndex = Math.floor(Math.random() * songs.length);
        } while (newSongIndex === currentSongIndex);
        currentSongIndex = newSongIndex;
        audio.src = `/static/soundtrack/${songs[currentSongIndex]}.mp3`;
        audio.play();
        nowPlaying(songs[currentSongIndex]);
    });
}

function nowPlaying(name, popup=true) {
    if (popup) createPopUp('info', '🎶Odtwarzanie', 'Teraz gra: ' + name + '<br>Utworzone przez: Patyna');
    document.getElementById('musicplayerTitle').textContent = name;
}

function pauseMusic() {
    if (audio.paused) {
        audio.play();
    } else {
        audio.pause();
    }
}

function playMusic() {
    audio.play();
}

function nextMusic() {
    let newSongIndex;
    do {
        newSongIndex = Math.floor(Math.random() * songs.length);
    } while (newSongIndex === currentSongIndex);
    currentSongIndex = newSongIndex;
    audio.src = `/static/soundtrack/${songs[currentSongIndex]}.mp3`;
    audio.play();
    nowPlaying(songs[currentSongIndex], false);
}

function prevMusic() {
    let newSongIndex;
    do {
        newSongIndex = Math.floor(Math.random() * songs.length);
    } while (newSongIndex === currentSongIndex);
    currentSongIndex = newSongIndex;
    audio.src = `/static/soundtrack/${songs[currentSongIndex]}.mp3`;
    audio.play();
    nowPlaying(songs[currentSongIndex], false);
}

document.addEventListener('keydown', () => {
    document.getElementById('loading').style.backgroundImage = 'url("/static/feed/1.png")';
});
document.addEventListener('keyup', () => {
    document.getElementById('loading').style.backgroundImage = '';
});

fetch('/static/changelog_bar')
    .then(response => response.text())
    .then(data => {
        document.getElementById('latest_news').innerHTML = data;
    })
    .catch(error => {
        console.error('Error fetching changelog:', error);
    });

if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.getElementById('darkmode').checked = true;
    document.body.classList.add('dark');
}

function exit() {
    document.getElementById('exitscreen').style.display = 'block';
    document.getElementById('exitscreen').animate([
        { transform: 'translateY(-100%)' },
        { transform: 'translateY(0)' }
    ], {
        duration: 1000,
        easing: 'ease-in-out'
    });
}

let current_player = 1;

function prevPfp(elem) {
    elem.parentNode.querySelector('.prpr').src = pfpsrclist[current_player - 1];
}

function nextPfp(elem) {
    elem.parentNode.querySelector('.prpr').src = pfpsrclist[current_player];
    current_player++;
    if (current_player >= pfpsrclist.length) {
        current_player = 0;
    }
}

function saveProfiles() {
    const player1Pfp = document.getElementById('myPfp1').src;
    const player2Pfp = document.getElementById('myPfp2').src;
    const player1Name = document.getElementById('profileEditNameInput1').value || 'Patyna';
    const player2Name = document.getElementById('profileEditNameInput2').value || 'MinerPL';

    // Save to localStorage
    localStorage.setItem('player1Pfp', player1Pfp);
    localStorage.setItem('player2Pfp', player2Pfp);
    localStorage.setItem('player1Name', player1Name);
    localStorage.setItem('player2Name', player2Name);

    // Show confirmation
    createPopUp('info', 'Zapisano', 'Profile zostały zapisane!');
    loadProfiles();
    document.getElementById('init').style.display = 'none';
}

function loadProfiles() {
    // Get profile data from localStorage
    const player1Pfp = localStorage.getItem('player1Pfp');
    const player2Pfp = localStorage.getItem('player2Pfp');
    const player1Name = localStorage.getItem('player1Name');
    const player2Name = localStorage.getItem('player2Name');
    const played = localStorage.getItem('played') || 0;

    if (!player1Pfp) localStorage.setItem('player1Pfp', pfpsrclist[0]);
    if (!player2Pfp) localStorage.setItem('player2Pfp', pfpsrclist[1]);

    if (played === null) {
        localStorage.setItem('played', 0);
    }

    // Set profile pictures if they exist
    if (player1Pfp) document.getElementById('myPfp1').src = player1Pfp;
    else document.getElementById('myPfp1').src = pfpsrclist[0];

    if (player2Pfp) document.getElementById('myPfp2').src = player2Pfp;
    else document.getElementById('myPfp2').src = pfpsrclist[1];

    // Set names if they exist
    if (player1Name) document.getElementById('profileEditNameInput1').value = player1Name;
    if (player2Name) document.getElementById('profileEditNameInput2').value = player2Name;

    document.getElementById('chessName1').textContent = player1Name;
    document.getElementById('chessName2').textContent = player2Name;
    document.getElementById('chessPfp1').firstChild.src = player1Pfp;
    document.getElementById('chessPfp2').firstChild.src = player2Pfp;
    document.getElementById('profileName').textContent = player1Name;
    document.getElementById('profilePfp').firstChild.src = player1Pfp;
    document.getElementById('profileRank').textContent = 'Zagranych partii: ' + played || 0;

}

document.getElementById('musicvol').addEventListener('input', (e) => {
    const volume = e.target.value / 100;
    audio.volume = volume;
    localStorage.setItem('musicVolume', volume);
});

document.getElementById('sfxvol').addEventListener('input', (e) => {
    const volume = e.target.value / 100;
    Array.from(document.getElementsByClassName('sfx')).forEach(sfx => {
        sfx.volume = volume;
    });
    localStorage.setItem('sfxVolume', volume);
});

document.getElementById('darkmode').addEventListener('change', (e) => {
    if (e.target.checked) {
        document.body.classList.add('dark');
        localStorage.setItem('darkMode', 'true');
    } else {
        document.body.classList.remove('dark');
        localStorage.setItem('darkMode', 'false');
    }
});

window.addEventListener('load', () => {
    const Name1 = localStorage.getItem('player1Name');
    if (Name1 === null || Name1.length < 1) {
        document.getElementById('init').style.display = 'block';
    }
    const musicVolume = localStorage.getItem('musicVolume');
    if (musicVolume !== null) {
        audio.volume = parseFloat(musicVolume);
        document.getElementById('musicvol').value = musicVolume * 100;
    } else {
        audio.volume = 0.75;
        document.getElementById('musicvol').value = 75;
    }

    const sfxVolume = localStorage.getItem('sfxVolume');
    if (sfxVolume !== null) {
        Array.from(document.getElementsByClassName('sfx')).forEach(sfx => {
            sfx.volume = parseFloat(sfxVolume);
        });
        document.getElementById('sfxvol').value = sfxVolume * 100;
    }

    const darkMode = localStorage.getItem('darkMode');
    if (darkMode === 'true' || (darkMode === null && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.body.classList.add('dark');
        document.getElementById('darkmode').checked = true;
    } else {
        document.body.classList.remove('dark');
        document.getElementById('darkmode').checked = false;
    }
});

document.addEventListener('click', (e) => {
    // if is button
    if (e.target.tagName === 'BUTTON') {
        document.getElementById('btnClickSound').play();
    }
    currentlyPlaying = true;
    document.getElementById('clickSound').play();
    setTimeout(() => {
        currentlyPlaying = false;
    }, 100);
});
