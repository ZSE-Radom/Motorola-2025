// from filenames: song name.mp3
let currentlyPlaying = false;
const songs = ['Ballada o Stańczyku', 'Electric Heart', 'F-Cloud Song', 'ITwist', 'Jawor', 'Serwer Patyny', 'Srochaj Anime Opening', 'ZSE Theme Song'];

function playSoundtrack() {
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
