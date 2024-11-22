// Hent elementene
const themeStyle = document.getElementById('theme-style');
const logo = document.getElementById('logo');
const themeToggleButtons = document.querySelectorAll('.theme-toggle');

// Funksjon for å sette tema
function setTheme(theme) {
    if (theme === 'light-mode') {
        themeStyle.setAttribute('href', '/static/css/light-mode.css');
        if (logo) logo.src = '/static/images/easyhome_logo_dark.png'; // Oppdater logo hvis tilgjengelig
        themeToggleButtons.forEach(button => button.textContent = 'Dark mode'); // Oppdater tekst på alle knapper
    } else {
        themeStyle.setAttribute('href', '/static/css/dark-mode.css');
        if (logo) logo.src = '/static/images/easyhome_logo_light.png'; // Oppdater logo hvis tilgjengelig
        themeToggleButtons.forEach(button => button.textContent = 'Light mode'); // Oppdater tekst på alle knapper
    }
    localStorage.setItem('theme', theme);
}

// Hent lagret tema fra localStorage
const savedTheme = localStorage.getItem('theme') || 'dark-mode';
setTheme(savedTheme);

// Bytt tema ved klikk
themeToggleButtons.forEach(button => {
    button.addEventListener('click', () => {
        const currentTheme = themeStyle.getAttribute('href').includes('dark-mode.css') ? 'light-mode' : 'dark-mode';
        setTheme(currentTheme);
    });
});
