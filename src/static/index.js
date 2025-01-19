function gameStart(type) {
    document.getElementById('mainmenu').style.display = 'none';
    if (type === 'offline') {
        let mode = prompt('podaj tryb (classic, blitz, 960)');
        fetch('/startOffline', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ mode })
        }).then(res => res.json()).then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                document.getElementById('chessGame').style.display = 'flex';
                console.log(data[0]);
                let x = document.getElementById('chessBoard');
                let time = data[1];
                x.innerHTML = '';
                
                for (let i = 0; i < 8; i++) {
                    let row = document.createElement('div');
                    row.className = 'row';
                    for (let j = 0; j < 8; j++) {
                        let square = document.createElement('div');
                        square.className = 'square';
                        square.id = i * 8 + j;
                        square.innerHTML = data[0][i][j];
                        row.appendChild(square);
                    }
                    x.appendChild(row);
                }

                document.getElementById('chessTimer1').innerHTML = time['Biały'];
                document.getElementById('chessTimer2').innerHTML = time['Czarny'];
                
            }
        });
    }
}