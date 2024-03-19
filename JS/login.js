const btnPopup = document.querySelector('.btnLogin-popup');
const welcomeText = document.getElementById('welcome-text');
const wrapper = document.querySelector('.wrapper');
const loginLink = document.querySelector('.login-link');
const registerLink = document.querySelector('.register-link');
const iconClose = document.querySelector('.icon-close');
const content = document.querySelector('.content'); 

btnPopup.addEventListener('click', () => {
    welcomeText.style.display = 'none';
    wrapper.classList.add('active-popup'); 
});

loginLink.addEventListener('click', () => { 
    wrapper.classList.remove('active'); 
    content.style.display = 'none'; 
});

registerLink.addEventListener('click', () => { 
    wrapper.classList.add('active'); 
    content.style.display = 'none'; 
});

iconClose.addEventListener('click', () => { 
    wrapper.classList.remove('active-popup');
    content.style.display = 'block'; 
    welcomeText.style.display = 'block'; 
});
