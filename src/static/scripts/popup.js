let popUpCount = 0;

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