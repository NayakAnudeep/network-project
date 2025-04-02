// ┌───────┐
// │ Login │
// └───────┘
const LOGIN_MODAL = document.getElementById("modal-login");
const LOGIN_FORM = LOGIN_MODAL.querySelector('form');
const LOGIN_URL = LOGIN_FORM.action;
const LOGIN_FLASH_ERROR_P = LOGIN_MODAL.querySelector('.flash-err');
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
LOGIN_FORM.addEventListener('submit', async event => {
    event.preventDefault();
    const email = LOGIN_FORM.querySelector('input[type="email"]').value;
    const password = LOGIN_FORM.querySelector('input[type="password"]').value;
    try {
        const response = await fetch(LOGIN_URL, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        if (response.ok) {
            if (data.success) { // redirect
                window.location.href = window.origin + '/';
            } else {
                LOGIN_FLASH_ERROR_P.classList.remove('hidden');
            }
        } else {
            LOGIN_FLASH_ERROR_P.textContent = "There has been an error. Please try again later.";
            LOGIN_FLASH_ERROR_P.classList.remove('hidden');
        }
    } catch (error) {
        console.error(error.message);
        LOGIN_FLASH_ERROR_P.textContent = "There has been an error. Please try again later.";
        LOGIN_FLASH_ERROR_P.classList.remove('hidden');
    }
});

// ┌─────────┐
// │ Sign up │
// └─────────┘
const SIGNUP_MODAL = document.getElementById("modal-signup");
const SIGNUP_FORM = SIGNUP_MODAL.querySelector('form');
const SIGNUP_URL = SIGNUP_FORM.action;
const SIGNUP_FLASH_ERROR_P = SIGNUP_MODAL.querySelector('.flash-err');
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
SIGNUP_FORM.addEventListener('submit', async event => {
    event.preventDefault();
    const email = SIGNUP_FORM.querySelector('input[type="email"]').value;
    const password = SIGNUP_FORM.querySelector('input[type="password"]').value;
    const name = SIGNUP_FORM.querySelector('input[type="text"]').value;
    const role = SIGNUP_FORM.querySelector('select').value;   
    try {
        const response = await fetch(SIGNUP_URL, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ name, email, password, role })
        });
        const data = await response.json();
        if (response.ok) {
            if (data.success) { // redirect
                window.location.href = window.location.href;
            } else {
                SIGNUP_FLASH_ERROR_P.textContent = data.error;
                SIGNUP_FLASH_ERROR_P.classList.remove('hidden');
            }
        } else {
            SIGNUP_FLASH_ERROR_P.classList.remove('hidden');
        }
    } catch (error) {
        console.error(error.message);
        SIGNUP_FLASH_ERROR_P.classList.remove('hidden');        
    }
});
