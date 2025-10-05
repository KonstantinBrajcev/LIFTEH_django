// static/js/charts.js

function initializeCharts() {
  // Проверяем, что данные загружены
  if (!window.chartData) {
    console.error('chartData is not defined');
    return;
  }

  console.log('Initializing charts with data:', window.chartData);

  // Проверяем наличие необходимых элементов
  const monthChartEl = document.getElementById('monthChart');
  const customerChartEl = document.getElementById('customerChart');
  const avgChartEl = document.getElementById('avgChart');

  if (!monthChartEl || !customerChartEl || !avgChartEl) {
    console.error('One or more chart elements not found');
    return;
  }

  // График №1 по месяцам
  try {
    const monthCtx = monthChartEl.getContext('2d');
    new Chart(monthCtx, {
      type: 'bar',
      data: {
        labels: window.chartData.monthNames,
        datasets: [{
          label: 'Сумма за месяц',
          data: window.chartData.monthSums,
          backgroundColor: 'rgba(54, 162, 235, 0.7)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }]
      },
      options: {
        animation: false,
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Сумма (руб)'
            }
          }
        },
        plugins: {
          annotation: {
            annotations: {
              avgLine: {
                type: 'line',
                yMin: window.chartData.monthAvg,
                yMax: window.chartData.monthAvg,
                borderColor: 'rgb(255, 99, 71)',
                borderWidth: 2,
                borderDash: [6, 6],
                label: {
                  content: 'Среднее: ' + window.chartData.monthAvg.toLocaleString('ru-RU'),
                  enabled: true,
                  position: 'right',
                  backgroundColor: 'rgba(132, 132, 132, 0.8)',
                  font: {
                    weight: 'bold'
                  }
                }
              }
            }
          }
        }
      }
    });
    console.log('Month chart initialized');
  } catch (error) {
    console.error('Error initializing month chart:', error);
  }

  // График №2 по заказчикам
  try {
    const customerCtx = customerChartEl.getContext('2d');
    new Chart(customerCtx, {
      type: 'bar',
      data: {
        labels: window.chartData.customers,
        datasets: [{
          label: 'Сумма за год',
          data: window.chartData.customerTotals,
          backgroundColor: 'rgba(255, 99, 132, 0.7)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1
        }]
      },
      options: {
        animation: false,
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            ticks: {
              autoSkip: false,
              maxRotation: 90
            }
          },
          y: {
            beginAtZero: true
          }
        }
      }
    });
    console.log('Customer chart initialized');
  } catch (error) {
    console.error('Error initializing customer chart:', error);
  }

  // График №3: Среднее значение по заказчикам
  try {
    const avgCtx = avgChartEl.getContext('2d');
    const avgData = {
      labels: window.chartData.customersAvg.map(item => item.customer),
      datasets: [{
        label: 'Среднее за ТО',
        data: window.chartData.customersAvg.map(item => item.avg_value),
        backgroundColor: 'rgba(153, 102, 255, 0.7)',
        borderColor: 'rgba(153, 102, 255, 1)',
        borderWidth: 1
      }]
    };

    const avgConfig = {
      type: 'bar',
      data: avgData,
      options: {
        animation: false,
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Среднее за ТО'
            }
          },
          x: {
            ticks: {
              autoSkip: false,
              maxRotation: 90,
              minRotation: 45
            }
          }
        },
        plugins: {
          annotation: {
            annotations: {
              avgLine: {
                type: 'line',
                yMin: window.chartData.globalAvg,
                yMax: window.chartData.globalAvg,
                borderColor: 'red',
                borderWidth: 2,
                borderDash: [6, 6],
                label: {
                  content: 'Среднее: ' + window.chartData.globalAvg.toLocaleString('ru-RU'),
                  enabled: true,
                  position: 'right',
                  backgroundColor: 'rgba(132, 132, 132, 0.8)',
                  font: {
                    weight: 'bold'
                  }
                }
              }
            }
          }
        }
      }
    };

    new Chart(avgCtx, avgConfig);
    console.log('Average chart initialized');
  } catch (error) {
    console.error('Error initializing average chart:', error);
  }
}

// Инициализация при загрузке документа
document.addEventListener('DOMContentLoaded', function () {
  console.log('DOM loaded, initializing charts...');
  initializeCharts();
});