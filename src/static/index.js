function gameStart(type) {
    document.getElementById('mainmenu').style.display = 'none';
    if (type === 'offline') {
        //let mode = prompt('podaj tryb (classic, blitz, 960)');
        let mode = 'classic'
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
                let letters = ['H', 'G', 'F', 'E', 'D', 'C', 'B', 'A'];
                x.innerHTML = '';

                for (let i = 0; i < 8; i++) {
                    let row = document.createElement('div');
                    row.className = 'row';
            
                    for (let j = 0; j < 8; j++) {
                        let square = document.createElement('div');
                        if (j==0){
                            if (i % 2 == 0){
                                square.innerHTML += `<div style="color: #FCF7FF" class="boardNumbers">${i+1}</div>`;
                            } else {
                                square.innerHTML += `<div style="color: #56876D" class="boardNumbers">${i+1}</div>`;
                            }
                        }
                        if (i==7){
                            if (j % 2 == 0){
                                square.innerHTML += `<div style="color: #56876D" class="boardLetters">${letters[j]}</div>`;
                            } else {
                                square.innerHTML += `<div style="color: #FCF7FF" class="boardLetters">${letters[j]}</div>`;
                            }
                        }
                        if (i % 2 == 0) {
                            if (j % 2 == 0) {
                                square.style.backgroundColor = '#56876D';
                            }
                        } else {
                            if (j % 2 != 0) {
                                square.style.backgroundColor = '#56876D';
                            }
                        }
                        square.className = 'square';
                        square.id = i * 8 + j;
                        square.innerHTML += data[0][i][j];
                        square.addEventListener("click", function(e) {
                            alert(square.id);
                        }, false);
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

gameStart('offline')