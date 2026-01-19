// Показать первую вкладку по умолчанию
const hash = window.location.hash.substring(1);
if (hash) {
  showTab(hash);
} else {
  showTab('service');
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

// Автоматическая адаптация при изменении размера окна
window.addEventListener('resize', function () {
  // adjustContentHeight();
});

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function () {
  // adjustContentHeight();
});