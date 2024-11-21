// Hent elementene
const themeStyle = document.getElementById('theme-style');
const logo = document.getElementById('logo');
const themeToggleButton = document.getElementById('theme-toggle');

// Funksjon for å sette tema
function setTheme(theme) {
    if (theme === 'light-mode') {
        themeStyle.setAttribute('href', '/static/css/light-mode.css');
        logo.src = '/static/images/easyhome_logo_dark.png';
        themeToggleButton.textContent = 'Dark mode';
    } else {
        themeStyle.setAttribute('href', '/static/css/dark-mode.css');
        logo.src = '/static/images/easyhome_logo_light.png';
        themeToggleButton.textContent = 'Light mode';
    }
    localStorage.setItem('theme', theme);
}

// Hent lagret tema fra localStorage
const savedTheme = localStorage.getItem('theme') || 'dark-mode';
setTheme(savedTheme);

// Bytt tema ved klikk
themeToggleButton.addEventListener('click', () => {
    const currentTheme = themeStyle.getAttribute('href').includes('dark-mode.css') ? 'light-mode' : 'dark-mode';
    setTheme(currentTheme);
});
