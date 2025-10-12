// ---- ФУНКЦИЯ ДЛЯ ЗАГРУЗКИ ФОРМЫ РЕДАКТИРОВАНИЯ AVR ----
function loadAvrEditForm(pk) {
  const modal = new bootstrap.Modal(document.getElementById('objectModal'));
  const url = `/avr/edit/${pk}/`;

  fetch(url, {
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
    .then(response => response.text())
    .then(html => {
      document.getElementById('modalTitle').textContent = 'Редактирование АВР';
      document.getElementById('modalFormContent').innerHTML = html;
      // Устанавливаем action формы
      const form = document.querySelector('#objectModal form');
      if (form) {
        form.action = url;
      }
      modal.show();
    })
    .catch(error => console.error('Error:', error));
}


// ---- ФУНКЦИЯ ОТКРЫТИЯ МОДАЛЬНОГО ОКНА ----
function loadModalForm(url, title, element) {
  const modal = new bootstrap.Modal(document.getElementById('objectModal'));
  document.getElementById('modalTitle').textContent = title;

  // Получаем цвет из data-атрибута
  const lastColor = element ? element.getAttribute('data-last-color') : null;

  fetch(url, {
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
    .then(response => response.text())
    .then(html => {
      document.getElementById('modalFormContent').innerHTML = html;

      // Устанавливаем начальный цвет
      if (lastColor) {
        document.querySelector('.modal-content').style.backgroundColor = lastColor;
      }
      // Добавляем обработчик после загрузки содержимого
      const addBtn = document.getElementById('addWorkButton');
      if (addBtn) {
        addBtn.addEventListener('click', addWorkRow);
      }
      setupFormSubmit();
      // Добавляем обработчик для изменения цвета radio-кнопок
      setupResultRadioButtons();
      modal.show();
    })
    .catch(error => console.error('Error:', error));
}


// ---- ФУНКЦИЯ ДЛЯ НАСТРОЙКИ И ОТПРАВКИ ФОРМЫ ----
function setupFormSubmit() {
  const form = document.querySelector('#objectModal form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const submitBtn = form.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Сохранение...';
      submitBtn.disabled = true;

      fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: {
          'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
        .then(response => {
          if (response.ok) { window.location.reload(); }
          else {
            return response.text().then(html => {
              document.getElementById('modalFormContent').innerHTML = html;
              setupFormSubmit();
            });
          }
        })
        .finally(() => {
          submitBtn.innerHTML = originalText;
          submitBtn.disabled = false;
        });
    });
  }
}


// ---- ФУНКЦИЯ ДЛЯ ПОДТВЕРЖДЕНИЯ УДАЛЕНИЯ ----
function confirmDelete(url, objectId) {
  const modal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
  document.getElementById('deleteConfirmText').textContent =
    `Вы уверены, что хотите удалить запись #${objectId}?`;
  const form = document.getElementById('deleteForm');
  form.action = url;
  modal.show();
}


function showTab(tabName) {
  // Скрыть все вкладки
  const tabs = document.querySelectorAll('.tab');
  tabs.forEach(tab => { tab.style.display = 'none'; });

  // Удалить класс active у всех кнопок
  const buttons = document.querySelectorAll('.tab-button');
  buttons.forEach(button => {
    button.classList.remove('active');
  });

  // Показать выбранную вкладку
  document.getElementById(tabName).style.display = 'block';
  document.querySelector(`.tab-button[onclick="showTab('${tabName}')"]`).classList.add('active');
  window.history.pushState(null, null, `#${tabName}`);

  // Если переключаемся на вкладку с графиками
  if (tabName === 'charts') {
    // Даем время на отображение вкладки
    setTimeout(() => {
      if (window.initChartsOnTabShow) {
        window.initChartsOnTabShow();
      } else {
        console.warn('Charts initialization function not found');
        // Резервная инициализация
        if (window.chartData && typeof initializeCharts === 'function') {
          setTimeout(initializeCharts, 300);
        }
      }
    }, 200);
  }
}

// Функция для инициализации графиков (резервная)
function initializeChartsFallback() {
  console.log('Using fallback charts initialization');
  const monthChartEl = document.getElementById('monthChart');
  const customerChartEl = document.getElementById('customerChart');
  const avgChartEl = document.getElementById('avgChart');

  if ((monthChartEl || customerChartEl || avgChartEl) && window.chartData) {
    console.log('Charts elements found, initializing...');
    // Если функция initializeCharts существует в глобальной области
    if (typeof initializeCharts === 'function') {
      initializeCharts();
    }
  }
}

// Показать первую вкладку по умолчанию
const hash = window.location.hash.substring(1);
if (hash) {
  showTab(hash);
} else {
  showTab('service');
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function () {
  // Проверяем, активна ли вкладка с графиками при загрузке
  const activeTab = document.querySelector('.tab-button.active');
  if (activeTab && activeTab.getAttribute('onclick').includes('charts')) {
    setTimeout(() => {
      if (window.initChartsOnTabShow) {
        window.initChartsOnTabShow();
      } else {
        initializeChartsFallback();
      }
    }, 1000);
  }
});


// ---- ФУНКЦИЯ ДОБАВЛЕНИЯ РАБОТ В АВР ----
let rowCounter = 1; // Счетчик для генерации уникальных ID
function addWorkRow() {
  rowCounter++; // Добавьте эту строку
  const container = document.getElementById('work-rows');
  if (!container) {
    console.error("Элемент work-rows не найден");
    return;
  }
  const newRow = document.createElement('div');
  newRow.className = 'work-row';
  newRow.style.display = 'flex';
  newRow.style.gap = '10px';
  newRow.style.alignItems = 'center';
  newRow.style.marginBottom = '10px';
  // Генерируем уникальные ID с использованием счетчика
  const workId = `workname-field-${rowCounter}`;
  const unitId = `unit-field-${rowCounter}`;
  const quantityId = `quantity-field-${rowCounter}`;

  newRow.innerHTML = `
            <div class="form-floating" style="flex: 1; min-width: 200px;">
                <input class="form-control" type="text" id="${workId}" name="workname" maxlength="100" required>
                <label class="form-label" for="${workId}">Наименование работ:</label>
            </div>
            
            <div class="form-floating" style="width: 100px;">
              <select class="form-select" id="${unitId}" name="unit" required>
                <option value="шт.">шт.</option>
                <option value="комп.">комп.</option>
                <option value="л.">л.</option>
                <option value="кг.">кг.</option>
                <option value="м.">м.</option>
              </select>
              <label class="form-label" for="${unitId}">Ед. изм.:</label>
            </div>

            <div class="form-floating" style="width: 100px;">
                <input class="form-control" type="number" id="${quantityId}" name="quantity" min="1" value="1" required>
                <label class="form-label" for="${quantityId}">Кол-во:</label>
            </div>
        <button type="button" class="btn btn-danger remove-work"
          style="align-self: stretch; display: flex; align-items: center; justify-content: center;">
          <strong>X</strong>
        </button>
    `;
  container.appendChild(newRow);
  // Добавляем обработчик удаления строки
  newRow.querySelector('.remove-work').addEventListener('click', function () {
    container.removeChild(newRow);
  });
}


// ---- ОБЪЕДИНЕННАЯ ФУНКЦИЯ ДЛЯ RADIO-КНОПОК ----
function setupResultRadioButtons() {
  const modalContent = document.querySelector('.modal-content');
  const fotoGroup = document.getElementById('foto-group');
  const commentsContainer = document.getElementById('comments-container');
  const commentsField = document.getElementById('comments');

  if (!modalContent || !fotoGroup || !commentsContainer) return;


  // Функция для определения цвета последней записи
  function getLastServiceClass() {
    // Ищем таблицу обслуживания в загруженной форме модального окна
    const modalContent = document.getElementById('modalFormContent');
    if (!modalContent) return null;
    const serviceRows = modalContent.querySelectorAll('tr.table-success, tr.table-warning, tr.table-danger');
    if (serviceRows.length === 0) return null;
    const lastRow = serviceRows[0];
    if (lastRow.classList.contains('table-success')) return '#d4edda'; // Зеленый
    if (lastRow.classList.contains('table-warning')) return '#fff3cd'; // Желтый
    if (lastRow.classList.contains('table-danger')) return '#f8d7da';  // Красный
    return null;
  }

  // Устанавливаем начальный цвет модального окна
  const lastColor = getLastServiceClass();
  if (lastColor) {
    modalContent.style.backgroundColor = lastColor;
  }

  function updateUI() {
    const selectedValue = document.querySelector('input[name="result"]:checked')?.value;
    if (!selectedValue) return;

    // 1. Обновляем фон модального окна
    const newColor = {
      '0': '#d4edda', // Зеленый
      '1': '#fff3cd', // Желтый
      '2': '#f8d7da'  // Красный
    }[selectedValue];

    if (newColor) {
      modalContent.style.backgroundColor = newColor;
      modalContent.style.transition = 'background-color 0.3s ease';
    }

    // 2. Управляем видимостью полей
    if (selectedValue === '0') {
      // Для "В исправном состоянии"
      commentsContainer.style.display = 'none';
      fotoGroup.classList.add('d-none');
      commentsField.value = 'В исправном состоянии';
    } else {
      // Для остальных вариантов
      commentsContainer.style.display = 'block';
      fotoGroup.classList.remove('d-none');

      if (selectedValue === '1') {
        commentsField.value = 'Требуется устранить ...';
      } else if (selectedValue === '2') {
        commentsField.value = 'Не работает';
      }
    }

    // 2. Управляем видимостью поля для фото
    const shouldShowFoto = ['1', '2'].includes(selectedValue);
    fotoGroup.classList.toggle('d-none', !shouldShowFoto);
    document.getElementById('foto').required = false;

  }

  // Назначаем обработчики для всех radio-кнопок
  document.querySelectorAll('input[name="result"]').forEach(radio => {
    radio.addEventListener('change', updateUI);
  });
}



// ---- ФУНКЦИЯ ЗАГРУЗКИ ПРОБЛЕМ В МОДАЛЬНОЕ ОКНО ----
function loadProblemModalForm(url, title) {
  const modal = new bootstrap.Modal(document.getElementById('objectModal'));
  document.getElementById('modalTitle').textContent = title;

  // Очищаем предыдущее содержимое
  document.getElementById('modalFormContent').innerHTML =
    '<div class="text-center py-4"><div class="spinner-border" role="status"><span class="visually-hidden">Загрузка...</span></div></div>';

  fetch(url, {
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.text();
    })
    .then(html => {
      document.getElementById('modalFormContent').innerHTML = html;
      modal.show();
    })
    .catch(error => {
      console.error('Error:', error);
      document.getElementById('modalFormContent').innerHTML =
        '<div class="alert alert-danger">Ошибка загрузки формы</div>';
    });
}