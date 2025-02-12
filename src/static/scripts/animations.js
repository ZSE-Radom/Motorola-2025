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

function fromSetupToGame(data) {
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
        renderChessBoard(data.board, (data.time_player_1, data.time_player_2));
    }, 1000);
}