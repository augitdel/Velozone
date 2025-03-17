const wrapper = document.querySelector('.wrapper');
const loginLink = document.querySelector('.login-link');
const registerLink = document.querySelector('.register-link');
const btnPopup = document.querySelector('.btnLogin-popup');
const iconClose = document.querySelector('.icon-close');

registerLink.addEventListener('click', () => {
    wrapper.classList.add('active')
});

loginLink.addEventListener('click', () => {
    wrapper.classList.remove('active');
});

btnPopup.addEventListener('click', () => {
    wrapper.classList.add('active-popup');
});

iconClose.addEventListener('click', () => {
    wrapper.classList.remove('active-popup');
});


function setActionForm(action) {
    let form;
    if (action === 'login') {
        form = document.getElementById("login"); // Haal het login formulier op
        form.action = "{{url_for('login')}}";
        form.method = "post";
    } else if (action === 'register') {
        form = document.getElementById("register"); // Haal het registratie formulier op
        form.action = "{{url_for('register')}}";
        form.method = "post";
    }
    let errorMessage = document.querySelector('.error-message');
    if (!errorMessage) {
        wrapper.classList.remove('active-popup');
    }
}

// Voeg eventlistener toe om te controleren op foutmeldingen bij het laden van de pagina
document.addEventListener("DOMContentLoaded", function() {
    const errorMessage = document.querySelector('.error-message');
    if (errorMessage) {
        wrapper.classList.add('active-popup');  // Open de popup opnieuw als er een fout is
    }
});
