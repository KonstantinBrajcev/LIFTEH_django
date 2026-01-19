// charts.js - упрощенная и надежная версия

class ChartsManager {
  constructor() {
    this.charts = {};
    this.isInitialized = false;
    console.log('ChartsManager constructor called');
  }

  initialize() {
    if (this.isInitialized) {
      console.log('Charts already initialized');
      return true;
    }

    try {
      console.log('Starting charts initialization...');

      // Проверяем наличие всех необходимых данных
      const requiredData = [
        'month_names', 'month_sums', 'customers', 'customer_totals',
        'customers_avg', 'total_sum_all', 'month_avg', 'global_avg', 'total_elevators'
      ];

      for (const dataId of requiredData) {
        if (!document.getElementById(dataId)) {
          throw new Error(`Missing data element: ${dataId}`);
        }
      }

      // Загружаем данные
      const monthNames = JSON.parse(document.getElementById('month_names').textContent);
      const monthSums = JSON.parse(document.getElementById('month_sums').textContent);
      const customers = JSON.parse(document.getElementById('customers').textContent);
      const customerTotals = JSON.parse(document.getElementById('customer_totals').textContent);
      const customersAvg = JSON.parse(document.getElementById('customers_avg').textContent);
      const totalSumAll = JSON.parse(document.getElementById('total_sum_all').textContent);
      const monthAvg = JSON.parse(document.getElementById('month_avg').textContent);
      const globalAvg = JSON.parse(document.getElementById('global_avg').textContent);
      const totalElevators = JSON.parse(document.getElementById('total_elevators').textContent);

      console.log('Data loaded:', {
        months: monthNames.length,
        customers: customers.length,
        totalSumAll: totalSumAll
      });

      // Создаем графики
      this.createMonthChart(monthNames, monthSums, monthAvg);
      this.createCustomerChart(customers, customerTotals, globalAvg);
      this.createAvgChart(customersAvg);

      // Обновляем итоги
      this.updateTotalDisplay(totalSumAll, monthAvg, globalAvg, customers.length, totalElevators);

      this.isInitialized = true;
      console.log('All charts created successfully');
      return true;

    } catch (error) {
      console.error('Error in charts initialization:', error);
      this.showError('Ошибка создания графиков: ' + error.message);
      return false;
    }
  }

  createMonthChart(monthNames, monthSums, monthAvg) {
    const ctx = document.getElementById('monthChart');

    this.charts.monthChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: monthNames,
        datasets: [{
          label: 'Сумма за месяц',
          data: monthSums,
          backgroundColor: 'rgba(54, 162, 235, 0.7)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }]
      },
      options: {
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
        }
      }
    });
  }

  createCustomerChart(customers, customerTotals, globalAvg) {
    const ctx = document.getElementById('customerChart');
    const topCustomers = customers.slice(0, 20);
    const topTotals = customerTotals.slice(0, 20);

    this.charts.customerChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: topCustomers,
        datasets: [{
          label: 'Сумма за год',
          data: topTotals,
          backgroundColor: 'rgba(255, 99, 132, 0.7)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            ticks: {
              maxRotation: 45,
              minRotation: 45
            }
          },
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Сумма (руб)'
            }
          }
        }
      }
    });
  }

  createAvgChart(customersAvg) {
    const ctx = document.getElementById('avgChart');
    const topAvg = customersAvg.slice(0, 20);
    const avgLabels = topAvg.map(item => item.customer);
    const avgData = topAvg.map(item => item.avg_value);

    this.charts.avgChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: avgLabels,
        datasets: [{
          label: 'Среднее за ТО',
          data: avgData,
          backgroundColor: 'rgba(153, 102, 255, 0.7)',
          borderColor: 'rgba(153, 102, 255, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            ticks: {
              maxRotation: 45,
              minRotation: 45
            }
          },
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Средняя сумма (руб)'
            }
          }
        }
      }
    });
  }

  updateTotalDisplay(totalSum, monthAvg, globalAvg, customersCount, elevatorsCount) {
    const formatNumber = (num) => new Intl.NumberFormat('ru-RU').format(num);

    document.getElementById('total-sum-display').textContent = `${formatNumber(totalSum)} руб.`;
    document.getElementById('month-avg-display').textContent = `${formatNumber(monthAvg)} руб.`;
    document.getElementById('global-avg-display').textContent = `${formatNumber(globalAvg)} руб.`;
    document.getElementById('customers-count-display').textContent = customersCount;
    document.getElementById('total-elevators-display').textContent = elevatorsCount;
  }

  showError(message) {
    const tabContent = document.getElementById('tab-content');
    if (tabContent) {
      const errorDiv = document.createElement('div');
      errorDiv.className = 'alert alert-danger';
      errorDiv.innerHTML = `<strong>Ошибка графиков:</strong> ${message}`;
      tabContent.prepend(errorDiv);
    }
  }

  destroy() {
    Object.values(this.charts).forEach(chart => {
      if (chart && typeof chart.destroy === 'function') {
        chart.destroy();
      }
    });
    this.charts = {};
    this.isInitialized = false;
  }
}

// Глобальные функции
window.chartsManager = new ChartsManager();
window.initializeCharts = function () {
  return window.chartsManager.initialize();
};

window.destroyCharts = function () {
  if (window.chartsManager) {
    window.chartsManager.destroy();
  }
};

console.log('charts.js loaded successfully');