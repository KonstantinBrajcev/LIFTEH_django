function toggleSortMenu() {
  const sortMenu = document.getElementById('sortMenuContainer');
  const toggle = document.getElementById('sortToggle');

  if (toggle.checked) {
    sortMenu.classList.add('show');
  } else {
    sortMenu.classList.remove('show');
  }
}


// Опционально: функция для сохранения состояния переключателя
function saveToggleState() {
  const toggle = document.getElementById('sortToggle');
  localStorage.setItem('sortMenuVisible', toggle.checked);
}

function loadToggleState() {
  const savedState = localStorage.getItem('sortMenuVisible');
  const toggle = document.getElementById('sortToggle');
  const sortMenu = document.getElementById('sortMenuContainer');

  if (savedState === 'true') {
    toggle.checked = true;
    // Небольшая задержка для корректной анимации при загрузке
    setTimeout(() => {
      sortMenu.classList.add('show');
    }, 10);
  }
}

// Загружаем состояние при загрузке страницы
document.addEventListener('DOMContentLoaded', loadToggleState);

// Сохраняем состояние при изменении
document.getElementById('sortToggle').addEventListener('change', saveToggleState);