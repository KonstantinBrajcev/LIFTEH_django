// object.js - только для работы с сортировкой
function toggleSortMenu() {
  const sortMenu = document.getElementById('sortMenuContainer');
  const mainContent = document.getElementById('mainContent');
  const toggle = document.getElementById('sortToggle');

  if (toggle.checked) {
    sortMenu.classList.add('show');
    if (mainContent) {
      mainContent.classList.add('with-sort-menu');
    }
  } else {
    sortMenu.classList.remove('show');
    if (mainContent) {
      mainContent.classList.remove('with-sort-menu');
    }
  }
}

// Функция для сохранения состояния переключателя
function saveToggleState() {
  const toggle = document.getElementById('sortToggle');
  if (toggle) {
    localStorage.setItem('sortMenuVisible', toggle.checked);
  }
}

function loadToggleState() {
  const savedState = localStorage.getItem('sortMenuVisible');
  const toggle = document.getElementById('sortToggle');
  const sortMenu = document.getElementById('sortMenuContainer');
  const mainContent = document.getElementById('mainContent');

  if (savedState === 'true' && toggle && sortMenu) {
    toggle.checked = true;
    setTimeout(() => {
      sortMenu.classList.add('show');
      if (mainContent) {
        mainContent.classList.add('with-sort-menu');
      }
    }, 10);
  }
}

// Загружаем состояние при загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
  // Загружаем состояние сортировки
  loadToggleState();

  // Сохраняем состояние при изменении
  const toggle = document.getElementById('sortToggle');
  if (toggle) {
    toggle.addEventListener('change', saveToggleState);
  }
});