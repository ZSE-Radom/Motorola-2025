let setupOptions = {};
let currentTurn = "Biały"; 
const modes = ['classic', 'blitz', '960'];
let boardData;


function updateTimers(time) {
  document.getElementById('chessTimer1').textContent = time['Biały'];
  document.getElementById('chessTimer2').textContent = time['Czarny'];
}

function highlightValidMoves(moves, posx, posy) {
  const validMoves = document.getElementsByClassName('validMove');
  while (validMoves.length) {
    validMoves[0].classList.remove('validMove');
  }
  console.log(moves);
  moves.forEach(([newPosx, newPosy]) => {
    const targetSquare = document.getElementById(newPosx * 8 + newPosy);
    targetSquare.classList.add('validMove');
    targetSquare.addEventListener('click', () => executeMove(posx, posy, newPosx, newPosy), { once: true });
  });
}

// Called when the user clicks “Start Game”
function startGame(type, mode) {
  animateMainMenu("close");
  setTimeout(() => {
    // Hide main menu elements.
    document.getElementById("modeList").style.display = "none";
    document.getElementById("mainmenu").style.display = "none";
    document.getElementById(`start${type}`).classList.remove("active");
    if (type === "Offline") {
      // Send a message to create an offline game.
      chessSocket.send(JSON.stringify({
        type: "create_game",
        session_id: sessionId,
        gamemode: mode,      // e.g. "classic", "blitz", "960"
        party_type: "offline" // For now we assume offline; adjust as needed.
      }));
    }
    // (You can add additional logic for other game types.)
  }, 1500);
}


// Called to render the game setup screen (for human vs. human games)
function renderSetup(game_type) {
  if (game_type === "human") {
    // Hide certain UI elements.
    document.getElementById("chessStats").style.display = "none";
    document.getElementById("chessSocial").style.display = "none";
    document.getElementById("chessSetupHuman").style.display = "none";
    document.getElementById("chessBoard").style.display = "none";
    animateMainMenu("close");

    // (Optionally) If you need to fetch an initial board look, you could send:
    // socket.send(JSON.stringify({ type: "getBoardLook" }));
    // For this example, we assume the server sends the board as part of setup.

    // Set up the toggle for selecting offline/online play.
    const options = [
      "Na tym komputerze (gra offline)",
      "Na innym komputerze (gra online)"
    ];
    const colors = ["#FC6471", "#7D5BA6"];
    const toggle = document.getElementById("toggle");
    const slider = toggle.querySelector(".slider");
    const labelsContainer = toggle.querySelector(".labels");
    setupOptions["game_type"] = "offline";
    toggle.style.setProperty("--options", options.length);
    labelsContainer.innerHTML = "";
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
        setupOptions["game_type"] = "offline";
      } else if (currentIndex === 1) {
        createPopUp("info", "Informacja", "Gra online jest w trakcie tworzenia!");
        setupOptions["game_type"] = "online";
      }
    });
    updateSlider();

    // (Optional) Request a list of available modes.
    // socket.send(JSON.stringify({ type: "list_modes" }));
    
    setTimeout(() => {
      document.getElementById("mainmenu").style.display = "none";
      document.getElementById("chessGame").style.display = "flex";
      document.getElementById("chessSetupHuman").style.display = "block";
      document.getElementById("chessBoard").style.display = "flex";
      animateChessBoard("setup");
    }, 1500);

    // When the user clicks the game start button:
    document.getElementById("chessGameStartButton").onclick = function () {
      if (setupOptions["game_mode"] === undefined) {
        createPopUp("error", "Błąd", "Wybierz tryb gry!");
      } else {
        chessSocket.send(JSON.stringify({
          type: "create_game",
          session_id: sessionId,
          gamemode: setupOptions["game_mode"],
          party_type: setupOptions["game_type"]
        }));
      }
    };
  } else if (game_type === "bot") {
    // For bot games, send data to start the game against a bot.
    const startData = {
      gamemode: "classic", // Adjust as needed.
      one_player: true,
      human_color: "Biały"
    };
    chessSocket.send(JSON.stringify({
      type: "create_game",
      session_id: sessionId,
      gamemode: startData.gamemode,
      party_type: "offline" // For a bot, you might treat this as offline.
    }));
  }
}


function renderChessBoard(localBoardData, time=(0, 0)) {
    document.getElementById('chessGame').style.display = 'flex';
    boardData = localBoardData;
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


function isEmpty(square) {
  return !square || square.trim() === ''; 
}

function isEnemyPiece(currentPiece, targetPiece) {
  if (!targetPiece || targetPiece.trim() === '') return false; 
  const isCurrentWhite = currentPiece === currentPiece.toUpperCase();
  const isTargetWhite = targetPiece === targetPiece.toUpperCase();
  return isCurrentWhite !== isTargetWhite;
}


function createSquare(row, col, piece, letters) {
  const square = document.createElement('div');
  const isLightSquare = (row + col) % 2 === 0;

  square.className = 'square';
  square.id = row * 8 + col;
  square.style.backgroundColor = isLightSquare ? '#FCF7FF' : '#56876D';

  const pieceContainer = document.createElement('div');
  pieceContainer.className = 'pieceContainer';

  if (piece && piece.trim() !== '') {
    const pieceImage = document.createElement('img');
    // White pieces use uppercase letter images (with an "x" variant)
    pieceImage.src = piece === piece.toUpperCase() ?
      `/static/figures/${piece}x.svg` : `/static/figures/${piece}.svg`;
    pieceContainer.appendChild(pieceImage);
  }
  square.appendChild(pieceContainer);

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
function handleSquareClick(posx, posy) {
  const piece = boardData[posx][posy];
  if (!piece || piece.trim() === '') return;

  const isWhitePiece = (piece === piece.toUpperCase());
  if ((currentTurn === "Biały" && !isWhitePiece) || (currentTurn === "Czarny" && isWhitePiece)) {
    console.log("Not your turn. Current turn:", currentTurn);
    return;
  }

  const validMoves = getValidMoves(piece, posx, posy);
  console.log("Valid moves:", validMoves);
  highlightValidMoves(validMoves, posx, posy);
}

function getValidMoves(piece, row, col) {
  const validMoves = [];
  const pieceType = piece.toUpperCase();
  console.log("Piece type:", pieceType);
  switch (pieceType) {
    case 'P': // Pawn
      validMoves.push(...getPawnValidMoves(row, col, boardData));
      break;
    case 'R': // Rook
      validMoves.push(...getRookValidMoves(row, col, boardData));
      break;
    case 'N': // Knight
      validMoves.push(...getKnightValidMoves(row, col, boardData));
      break;
    case 'B': // Bishop
      validMoves.push(...getBishopValidMoves(row, col, boardData));
      break;
    case 'Q': // Queen
      validMoves.push(...getQueenValidMoves(row, col, boardData));
      break;
    case 'K': // King
      validMoves.push(...getKingValidMoves(row, col, boardData));
      break;
    default:
      break;
  }
  return validMoves;
}

// Pawn movement logic
function getPawnValidMoves(row, col, boardData) {
  const validMoves = [];
  const piece = boardData[row][col];
  if (!piece || piece.trim() === '') return validMoves;

  // Determine color: white if uppercase, black if lowercase.
  const isWhite = (piece === piece.toUpperCase());
  // White moves up (row decreases), black moves down (row increases)
  const direction = isWhite ? -1 : 1;

  // One-square move forward (only if the target square is empty)
  if (boardData[row + direction] && isEmpty(boardData[row + direction][col])) {
    validMoves.push([row + direction, col]);

    // Two-square move on the pawn's first move.
    // For white, the starting row is 6; for black, it’s 1.
    if ((isWhite && row === 6) || (!isWhite && row === 1)) {
      if (boardData[row + 2 * direction] && isEmpty(boardData[row + 2 * direction][col])) {
        validMoves.push([row + 2 * direction, col]);
      }
    }
  }

  // Diagonal captures:
  if (boardData[row + direction]) {
    // Left diagonal
    if (col > 0) {
      const leftDiag = boardData[row + direction][col - 1];
      if (!isEmpty(leftDiag) && isEnemyPiece(piece, leftDiag)) {
        validMoves.push([row + direction, col - 1]);
      }
    }
    // Right diagonal
    if (col < 7) {
      const rightDiag = boardData[row + direction][col + 1];
      if (!isEmpty(rightDiag) && isEnemyPiece(piece, rightDiag)) {
        validMoves.push([row + direction, col + 1]);
      }
    }
  }

  return validMoves;
}


function getRookValidMoves(row, col, boardData) {
  const validMoves = [];
  const currentPiece = boardData[row][col];

  const directions = [
    [-1, 0], [1, 0], [0, -1], [0, 1] 
  ];

  directions.forEach(([dx, dy]) => {
    let x = row + dx;
    let y = col + dy;

    while (x >= 0 && x < 8 && y >= 0 && y < 8) {
      if (isEmpty(boardData[x][y])) {
        validMoves.push([x, y]);
      } else {
        if (isEnemyPiece(currentPiece, boardData[x][y])) {
          validMoves.push([x, y]);
        }
        break;
      }
      x += dx;
      y += dy;
    }
  });

  return validMoves;
}


// Knight movement logic
function getKnightValidMoves(row, col, boardData) {
  const validMoves = [];
  const currentPiece = boardData[row][col];
  const knightMoves = [
    [-2, -1], [-1, -2], [1, -2], [2, -1],
    [2, 1], [1, 2], [-1, 2], [-2, 1]
  ];

  knightMoves.forEach(([dx, dy]) => {
    const x = row + dx;
    const y = col + dy;
    
    if (x >= 0 && x < 8 && y >= 0 && y < 8) {
      if (isEmpty(boardData[x][y]) || isEnemyPiece(currentPiece, boardData[x][y])) {
        validMoves.push([x, y]);
      }
    }
  });

  return validMoves;
}

function getBishopValidMoves(row, col, boardData) {
  const validMoves = [];
  const currentPiece = boardData[row][col];

  const directions = [
    [-1, -1], [-1, 1], [1, -1], [1, 1] 
  ];

  directions.forEach(([dx, dy]) => {
    let x = row + dx;
    let y = col + dy;

    while (x >= 0 && x < 8 && y >= 0 && y < 8) {
      if (isEmpty(boardData[x][y])) {
        validMoves.push([x, y]);
      } else {
        if (isEnemyPiece(currentPiece, boardData[x][y])) {
          validMoves.push([x, y]); 
        }
        break;
      }
      x += dx;
      y += dy;
    }
  });

  return validMoves;
}

function getQueenValidMoves(row, col, boardData) {
  return [
    ...getRookValidMoves(row, col, boardData),
    ...getBishopValidMoves(row, col, boardData)
  ];
}

function getKingValidMoves(row, col, boardData) {
  const validMoves = [];
  const currentPiece = boardData[row][col];

  const kingMoves = [
    [-1, -1], [-1, 0], [-1, 1],
    [0, -1],           [0, 1],
    [1, -1],  [1, 0],  [1, 1]
  ];

  kingMoves.forEach(([dx, dy]) => {
    const x = row + dx;
    const y = col + dy;

    if (x >= 0 && x < 8 && y >= 0 && y < 8) {
      if (isEmpty(boardData[x][y]) || isEnemyPiece(currentPiece, boardData[x][y])) {
        validMoves.push([x, y]);
      }
    }
  });

  return validMoves;
}


function executeMove(posx, posy, newPosx, newPosy) {
  chessSocket.send(JSON.stringify({
    type: "move",
    session_id: sessionId,
    game_id: currentGameId,
    old_pos: `${posx},${posy}`,
    new_pos: `${newPosx},${newPosy}`
  }));

  updateBoardAfterMove([posx, posy], [newPosx, newPosy]);

  currentTurn = (currentTurn === "Biały") ? "Czarny" : "Biały";
  console.log("Turn switched. New turn:", currentTurn);
}
function updateTimers(time) {
  document.getElementById("chessTimer1").textContent = time["Biały"];
  document.getElementById("chessTimer2").textContent = time["Czarny"];
}


function closeModes() {
  document.getElementById("modeList").style.display = "none";
  const collection = document.getElementsByClassName("active");
  for (const c of collection) {
    c.classList.remove("active");
  }
}

// Update the list of available parties (for a lobby UI).
function updatePartiesList(parties) {
  const listContainer = document.getElementById("partiesList");
  listContainer.innerHTML = "";
  for (const [gameId, info] of Object.entries(parties)) {
    const div = document.createElement("div");
    div.textContent = `Game ${gameId}: ${info.gamemode} (${info.players} gracz(e))`;
    // Optionally, add a button to join the game.
    const joinBtn = document.createElement("button");
    joinBtn.textContent = "Dołącz";
    joinBtn.onclick = () => joinGame(gameId);
    div.appendChild(joinBtn);
    listContainer.appendChild(div);
  }
}


function joinGame(gameId) {
    chessSocket.send(JSON.stringify({
      type: "join_game",
      session_id: sessionId,
      game_id: gameId
    }));
  }


  function updateBoardAfterMove(oldPos, newPos) {
    const [oldx, oldy] = oldPos.map(Number);
    const [newx, newy] = newPos.map(Number);
    
    // Update the board data:
    boardData[newx][newy] = boardData[oldx][oldy];
    boardData[oldx][oldy] = '';
  
    // Get the corresponding DOM squares.
    const oldSquare = document.getElementById(oldx * 8 + oldy);
    const newSquare = document.getElementById(newx * 8 + newy);
  
    // Assume each square has a container for its piece image.
    const oldContainer = oldSquare.querySelector('.pieceContainer');
    const newContainer = newSquare.querySelector('.pieceContainer');
  
    // Clear both containers to ensure no leftover images.
    oldContainer.innerHTML = '';
    newContainer.innerHTML = '';
  
    // Rebuild the destination square’s piece image (if any)
    const piece = boardData[newx][newy];
    if (piece && piece.trim() !== '') {
      const pieceImage = document.createElement('img');
      // If the piece is uppercase, assume it’s white and use the "x" variant.
      pieceImage.src = piece === piece.toUpperCase() ?
        `/static/figures/${piece}x.svg` : `/static/figures/${piece}.svg`;
      newContainer.appendChild(pieceImage);
    }
  }
  
function initStats(game_mode, game_type, first_player_name, second_player_name, first_player_time, second_player_time) {
    document.getElementById('chessGameType').innerHTML = `Gra ${game_mode}, typ: ${game_type}`;
    document.getElementById('chessName1').textContent = first_player_name;
    document.getElementById('chessName2').textContent = second_player_name;
    document.getElementById('chessTimer1').textContent = first_player_time;
    document.getElementById('chessTimer2').textContent = second_player_time;
}

function startGame(type, mode) {
    animateMainMenu("close");
    setTimeout(() => {
        // Hide main menu elements.
        document.getElementById("modeList").style.display = "none";
        document.getElementById("mainmenu").style.display = "none";
        document.getElementsByClassName('active')[0].classList.remove("active");
        if (type === "Offline") {
            chessSocket.send(JSON.stringify({
                type: "create_game",
                session_id: sessionId,
                gamemode: mode,      // e.g. "classic", "blitz", "960"
                party_type: "offline" // For now we assume offline; adjust as needed.
            }));
        }
    }, 1500);
}

function renderSetup(game_type) {
if (game_type === "human") {
    // Hide certain UI elements.
    document.getElementById("chessStats").style.display = "none";
    document.getElementById("chessSocial").style.display = "none";
    document.getElementById("chessSetupHuman").style.display = "none";
    document.getElementById("chessSetupBot").style.display = "none";
    document.getElementById("chessBoard").style.display = "none";
    animateMainMenu("close");

    // (Optionally) If you need to fetch an initial board look, you could send:
    // socket.send(JSON.stringify({ type: "getBoardLook" }));
    // For this example, we assume the server sends the board as part of setup.

    // Set up the toggle for selecting offline/online play.
    const options = [
    "Na tym komputerze (gra offline)",
    "Na innym komputerze (gra online)"
    ];
    const colors = ["#FC6471", "#7D5BA6"];
    const toggle = document.getElementById("toggle");
    const slider = toggle.querySelector(".slider");
    const labelsContainer = toggle.querySelector(".labels");
    setupOptions["game_type"] = "offline";
    toggle.style.setProperty("--options", options.length);
    labelsContainer.innerHTML = "";
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
        setupOptions["game_type"] = "offline";
    } else if (currentIndex === 1) {
        createPopUp("info", "Informacja", "Gra online jest w trakcie tworzenia!");
        setupOptions["game_type"] = "online";
    }
    });
    updateSlider();

    modes.forEach((mode) => {
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
    });

    setTimeout(() => {
    document.getElementById("mainmenu").style.display = "none";
    document.getElementById("chessGame").style.display = "flex";
    document.getElementById("chessSetupHuman").style.display = "block";
    document.getElementById("chessBoard").style.display = "flex";
    animateChessBoard("setup");
    }, 1500);

    // When the user clicks the game start button:
    document.getElementById("chessGameStartButton").onclick = function () {
    if (setupOptions["game_mode"] === undefined) {
        createPopUp("error", "Błąd", "Wybierz tryb gry!");
    } else {
        chessSocket.send(JSON.stringify({
            type: "create_game",
            session_id: sessionId,
            gamemode: setupOptions["game_mode"],
            party_type: setupOptions["game_type"]
        }));
    }
    };
} else if (game_type === "bot") {
    // For bot games, send data to start the game against a bot.
    const startData = {
        gamemode: "classic", // Adjust as needed.
        one_player: true,
        human_color: "Biały"
    };
    chessSocket.send(JSON.stringify({
        type: "create_game",
        session_id: sessionId,
        gamemode: startData.gamemode,
        party_type: "offline" // For a bot, you might treat this as offline.
    }));
    setTimeout(() => {
        document.getElementById("mainmenu").style.display = "none";
        document.getElementById("chessGame").style.display = "flex";
        document.getElementById("chessSetupHuman").style.display = "none";
        document.getElementById("chessSetupBot").style.display = "none";
        document.getElementById("chessBoard").style.display = "flex";
        animateChessBoard("setup");
        }, 1500);
}
}

function resign() {

}

function exit() {
    resign();
}

function draw() {

}
