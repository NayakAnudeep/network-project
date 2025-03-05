
/* ▗▖    ▗▄▖  ▗▄▄▖▗▄▄▄▖▗▖  ▗▖
   ▐▌   ▐▌ ▐▌▐▌     █  ▐▛▚▖▐▌
   ▐▌   ▐▌ ▐▌▐▌▝▜▌  █  ▐▌ ▝▜▌
   ▐▙▄▄▖▝▚▄▞▘▝▚▄▞▘▗▄█▄▖▐▌  ▐▌ */

const LOGIN_MODAL = document.getElementById("modal-login");
const LOGIN_LINK = document.querySelector('#login-btn');
const LOGIN_CLOSE_BTNS = [document.querySelector('#modal-login .close-btn'),
                          document.querySelector('#modal-login .cancel')];

LOGIN_LINK.addEventListener('click', event => {
    event.preventDefault();
    SIGNUP_MODAL.style.display = "none";
    LOGIN_MODAL.style.display = "block";
});
for (let i = 0; i < LOGIN_CLOSE_BTNS.length; i++) {
    LOGIN_CLOSE_BTNS[i].addEventListener('click', event => {
        LOGIN_MODAL.style.display = "none";
    });
}

/*  ▗▄▄▖▗▄▄▄▖ ▗▄▄▖▗▖  ▗▖▗▖ ▗▖▗▄▄▖
   ▐▌     █  ▐▌   ▐▛▚▖▐▌▐▌ ▐▌▐▌ ▐▌
    ▝▀▚▖  █  ▐▌▝▜▌▐▌ ▝▜▌▐▌ ▐▌▐▛▀▘
   ▗▄▄▞▘▗▄█▄▖▝▚▄▞▘▐▌  ▐▌▝▚▄▞▘▐▌ */

const SIGNUP_MODAL = document.getElementById("modal-signup");
const SIGNUP_LINKS = [document.querySelector('#signup-btn'),
                      document.querySelector('#signup-now-btn')];
const SIGNUP_CLOSE_BTNS = [document.querySelector('#modal-signup .close-btn'),
                           document.querySelector('#modal-signup .cancel')];

for (let i = 0; i < SIGNUP_LINKS.length; i++) {
    SIGNUP_LINKS[i].addEventListener('click', event => {
        event.preventDefault();
        LOGIN_MODAL.style.display = "none";
        SIGNUP_MODAL.style.display = "block";
    });
}

for (let i = 0; i < SIGNUP_CLOSE_BTNS.length; i++) {
    SIGNUP_CLOSE_BTNS[i].addEventListener('click', event => {
        SIGNUP_MODAL.style.display = "none";
    });
}
