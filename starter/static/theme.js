const THEME_STORAGE_KEY = 'sudoku-theme';
const LIGHT_THEME = 'light';
const DARK_THEME = 'dark';

function getStoredTheme() {
  try {
    const storedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    if (storedTheme === LIGHT_THEME || storedTheme === DARK_THEME) {
      return storedTheme;
    }
  } catch (error) {
    console.warn('Unable to read theme from localStorage', error);
  }
  return null;
}

function getPreferredTheme() {
  const storedTheme = getStoredTheme();
  if (storedTheme) {
    return storedTheme;
  }

  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return DARK_THEME;
  }

  return LIGHT_THEME;
}

function applyTheme(theme) {
  document.body.dataset.theme = theme;

  const toggleButton = document.getElementById('theme-toggle');
  if (toggleButton) {
    toggleButton.setAttribute('aria-pressed', String(theme === DARK_THEME));
    toggleButton.innerText = theme === DARK_THEME ? '☀️ Light Mode' : '🌙 Dark Mode';
  }
}

function setTheme(theme) {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  } catch (error) {
    console.warn('Unable to save theme to localStorage', error);
  }
  applyTheme(theme);
}

function toggleTheme() {
  const nextTheme = document.body.dataset.theme === DARK_THEME ? LIGHT_THEME : DARK_THEME;
  setTheme(nextTheme);
}

document.addEventListener('DOMContentLoaded', () => {
  const initialTheme = getPreferredTheme();
  applyTheme(initialTheme);

  const toggleButton = document.getElementById('theme-toggle');
  if (toggleButton) {
    toggleButton.addEventListener('click', toggleTheme);
  }
});

window.sudokuTheme = {
  applyTheme,
  setTheme,
  toggleTheme,
  getStoredTheme,
};
