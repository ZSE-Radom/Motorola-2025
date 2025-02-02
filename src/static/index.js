let popUpCount = 0;
let username = '';
let setupOptions = {};
let currentlyPlaying = false;

function fetchProfile() {
    fetch('/profile', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            createPopUp('error', 'Błąd z połączeniem', data.error);
        } else {
            username = data.username;
            document.getElementById('profileName').innerHTML = data.name;
            document.getElementById('profileRank').innerHTML = "RANK  " + data.elo;
            document.getElementById('profilePfpSrc').src = '/static/profiles/' + data.pfp;
        }
    }); 
}

function gameStart(type) {
    /** 
    if (type === 'Offline') {
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
                const button = document.getElementById(`start${type}`);
                button.classList.add('active')
                modeList.innerHTML = '';
                data.modes.forEach(mode => {
                    const modeButton = document.createElement('button');
                    modeButton.textContent = mode;
                    modeButton.className = 'modeBtn';
                    modeButton.addEventListener('click', () => startGame('Offline', mode));
                    modeList.appendChild(modeButton);
                });
            }
        });
    }*/
}

function startGame(type, mode) {
    animateMainMenu('close');
    setTimeout(() => {
        document.getElementById('modeList').style.display = 'none';
        document.getElementById('mainmenu').style.display = 'none';
        document.getElementById(`start${type}`).classList.remove('active');
        if (type === 'Offline') {
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
                    document.getElementById('modeList').style.display = 'none';
                    document.getElementById('chessGame').style.display = 'flex';
                    initStats(data.game_mode, data.game_type, data.first_player_name, data.second_player_name);
                    renderChessBoard(data.board, data.timer);
                    setInterval(refreshTimer, 500);
                    setInterval(checkForEvents, 500);
                }
            });
        }
    }, 1500);
}

function unsetIntervals() {
    clearInterval(refreshTimer);
    clearInterval(checkForEvents);
}

function renderSetup(game_type) {
    let boardData;
    if (game_type === 'human') {
        document.getElementById('chessStats').style.display = 'none';
        document.getElementById('chessSocial').style.display = 'none';
        document.getElementById('chessSetupHuman').style.display = 'none';
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
                renderChessBoard(boardData, 0);
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
                
                toggle.addEventListener("click", () => {
                    currentIndex = (currentIndex + 1) % options.length;
                    updateSlider();
                    if (currentIndex === 0) {
                        setupOptions['game_type'] = 'offline';
                    } else if (currentIndex === 1) {
                        createPopUp('info', 'Informacja', 'Gra online jest w trakcie tworzenia!');
                        setupOptions['game_type'] = 'online';
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
                                    document.getElementById('chessGame').style.display = 'flex';
                                    document.getElementById('chessSocial').style.display = 'block';
                                    document.getElementById('chessStats').style.display = 'block';
                                    initStats(data.game_mode, data.game_type, data.first_player_name, data.second_player_name);
                                    renderChessBoard(data.board, data.timer);
                                    setInterval(refreshTimer, 500);
                                    setInterval(checkForEvents, 500);
                                }, 1000);
                            }
                        });
                    }
                }
            }
        });
    } else if (game_type === 'bot') {
        createPopUp('info', 'Informacja', 'Gra z botem jest w trakcie tworzenia!');   
    }
}

function renderChessBoard(boardData, time) {
    document.getElementById('chessGame').style.display = 'flex';
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
    animateChessBoard('game');
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
                return 'OK';
            }
            document.getElementById('chessTurn').textContent = 'Tura: ' + data.current_turn;
        }
    });
}

function createPopUp(type, title, content) {
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

function checkForEvents() {
    fetch('/events')
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            createPopUp('error', 'Błąd z połączeniem', data.error);
        } else {
            for (const event of data.events) {
                if (event === 'resign') {
                    animateChessBoard('close');
                    setTimeout(() => {
                        document.getElementById('chessGame').style.display = 'none';
                        animateMainMenu('open');
                        document.getElementById('mainmenu').style.display = 'block';
                        createPopUp('info', 'Koniec gry', 'Gracz ' + data.winner + ' wygrał, jego przeciwnik się poddał!');
                        setTimeout(() => {
                            unsetIntervals();
                        }, 5000);
                    }, 1500);
                } else if (event === 'draw') {
                    animateChessBoard('close');
                    setTimeout(() => {
                        document.getElementById('chessGame').style.display = 'none';
                        animateMainMenu('open');
                        document.getElementById('mainmenu').style.display = 'block';
                        createPopUp('info', 'Koniec gry', 'Remis!');
                        setTimeout(() => {
                            unsetIntervals();
                        }, 5000);
                    }, 1500);
                } else if (event === 'time_over') {
                    animateChessBoard('close');
                    setTimeout(() => {
                        document.getElementById('chessGame').style.display = 'none';
                        animateMainMenu('open');
                        document.getElementById('mainmenu').style.display = 'block';
                        createPopUp('info', 'Koniec gry', 'Gracz ' + data.winner + ' wygrał, czas drugiego gracza minął!');
                        setTimeout(() => {
                            unsetIntervals();
                        }, 5000);
                    }, 1500);
                } else if (event === 'end') {
                    animateChessBoard('close');
                    setTimeout(() => {
                        document.getElementById('chessGame').style.display = 'none';
                        animateMainMenu('open');
                        document.getElementById('mainmenu').style.display = 'block';
                        createPopUp('info', 'Koniec gry', 'Gra została zakończona!');
                        setTimeout(() => {
                            unsetIntervals();
                        }, 5000);
                    }, 1500);
                } else {
                    createPopUp('info', 'Zdarzenie', event);
                }
            }
        }
    });
}

const slider = document.querySelector('#feed');
let mouseDown = false;
let startX, scrollLeft;
let startDragging = function (e) {
    mouseDown = true;
    startX = e.pageX - slider.offsetLeft;
    scrollLeft = slider.scrollLeft;
};

let stopDragging = function (event) {
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

fetchProfile();

window.onload = function(){
    document.getElementById('loading').style.opacity = '0';
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
    } else if (type === 'setup') {
        document.getElementById('chessSetupHuman').style.animation = "slideup-center 3s cubic-bezier(0.075, 0.82, 0.165, 1)";
        document.getElementById('chessBoard').style.animation = "slideup-center 2s cubic-bezier(0.075, 0.82, 0.165, 1)";
    } else if (type === 'close') {
        document.getElementById('chessSocial').style.animation = "slidedown-center 3s cubic-bezier(0.075, 0.82, 0.165, 1)";
        document.getElementById('chessBoard').style.animation = "slidedown-center 2s cubic-bezier(0.075, 0.82, 0.165, 1)";
        document.getElementById('chessStats').style.animation = "slidedown-center 3s cubic-bezier(0.075, 0.82, 0.165, 1)";
    }
}

function playSoundtrack() {
    const songs = ['Ballada o Stańczyku', 'Electric Heart', 'F-Cloud Song', 'ITwist', 'Jawor', 'Serwer Patyny', 'Srochaj Anime Opening', 'ZSE Theme Song'];
    let currentSongIndex = Math.floor(Math.random() * songs.length);
    const audio = new Audio(`/static/soundtrack/${songs[currentSongIndex]}.mp3`);
    audio.loop = false;
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

function nowPlaying(name) {
    createPopUp('info', '🎶Odtwarzanie', 'Teraz gra: ' + name + '<br>Utworzone przez: Patyna');
}

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