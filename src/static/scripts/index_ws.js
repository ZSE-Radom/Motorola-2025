let username = '';

function fetchProfile() {
    username = 'Patyna';
    document.getElementById('profileName').innerHTML = username;
    document.getElementById('profileRank').innerHTML = "RANK  " + 2137;
    document.getElementById('profilePfpSrc').src = '/static/profiles/' + '8715642fbbded8333534042f40a2a3e4.png';
    // TODO?
}

function handleSocketMessage(message) {
    switch (message.type) {
      case "init":
        sessionId = message.session_id;
        createPopUp("info", "Websocket", ` Połączono z serwerem websocket. ID sesji: ${sessionId}`);
        // You may now enable game creation/join UI.
        break;
  
      case "create_game":
        currentGameId = message.game_id;
        createPopUp("info", "Gra utworzona", `ID gry: ${currentGameId}`);
        // Display the initial board that the backend sends.

        // (Optionally) if party_type is "offline", the backend will immediately start the game.
        break;
  
      case "play":
        createPopUp("info", "Gra rozpoczęta", "Powodzenia!");
        fromSetupToGame(message);
        console.log(message)
        initStats(
            "??", "??", "??", "??", message.time_player_1, message.time_player_2
                );
        // You can also set up periodic UI updates if needed (or let the server push updates).
        break;
  
      case "move":
        createPopUp("info", "Ruch", "Przeciwnik wykonał ruch.");
        // Update the board locally based on the move.
        updateBoardAfterMove(message.old_pos, message.new_pos);
        break;
  
      case "list":
        // The server sends an updated list of available parties.
        updatePartiesList(message.parties);
        break;
  
      case "error":
        createPopUp("error", "Error", message.message);
        break;
  
      default:
        createPopUp("error", "Error", "Nieznany typ wiadomości.");
    }
  }
  

window.addEventListener("DOMContentLoaded", () => {
    window['websocket'] = new WebSocket('ws://localhost:8001');
    createPopUp('info', 'Websocket', 'Connecting to websocket server...');
    fetchProfile();

    chessSocket = window['websocket'];

    chessSocket.onopen = () => {
        chessSocket.send(JSON.stringify({ type: "init" }));
        document.getElementById('loading').style.opacity = '0';
        animateMainMenu('open');
        setTimeout(() => {
            playSoundtrack();
            document.getElementById('loading').style.display = 'none';
        }, 2000);
    };
    
    chessSocket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleSocketMessage(message);
    };
    
    chessSocket.onclose = () => {
        createPopUp('error', 'Websocket', 'Utracono połączenie z backendem...');
        // TODO? ponowne łączenie?
    };
    
    chessSocket.onerror = (error) => {
        createPopUp('error', 'Websocket', `Błąd połączenia z backendem ${error}`);
        console.error(error);
    };

});
