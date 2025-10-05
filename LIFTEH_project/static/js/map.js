let map;
let clusterer;
// Состояния кнопки
const filterStates = {
  all: {
    text: "ВСЕ ОБЪЕКТЫ",
    filter: "all",
    next: "without_marks",
    className: "active-all"
  },
  without_marks: {
    text: "БЕЗ ОТМЕТОК",
    filter: "without_marks",
    next: "all",
    className: "active-without-marks"
  }
};

let currentFilterState = filterStates.all;

function initMap(filterType = 'all') {
  if (map) {
    map.destroy();
  }

  map = new ymaps.Map('map', {
    center: [53.9, 27.5],
    zoom: 7
  });

  // Удаляем все стандартные элементы управления
  map.controls.remove('zoomControl');
  map.controls.remove('geolocationControl');
  map.controls.remove('searchControl');
  map.controls.remove('typeSelector');
  map.controls.remove('fullscreenControl');
  map.controls.remove('rulerControl');
  map.controls.remove('trafficControl');
  map.controls.remove('routeButtonControl');

  clusterer = new ymaps.Clusterer({
    preset: 'islands#invertedOrangeClusterIcons',
    clusterDisableClickZoom: true,
    clusterOpenBalloonOnClick: true,
    gridSize: 64
  });

  loadObjects(filterType);
}

function loadObjects(filterType) {
  // Показываем индикатор загрузки
  clusterer.removeAll();

  fetch(`/get-objects/?filter=${filterType}`)
    .then(response => response.json())
    .then(objectsData => {
      const placemarks = [];
      const uniqueAddresses = new Set();

      // SVG иконка в формате data URL
      const customIconSvg = 'data:image/svg+xml;charset=utf-8,' +
        encodeURIComponent(
          '<svg xmlns="http://www.w3.org/2000/svg" width="35" height="35" fill="currentColor" class="bi bi-geo-alt-fill" viewBox="0 0 16 16">' +
          '<path fill="#de4c15" d="M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10m0-7a3 3 0 1 1 0-6 3 3 0 0 1 0 6"/>' +
          '</svg>'
        );

      objectsData.forEach(function (obj) {
        if (obj.latitude && obj.longitude && !uniqueAddresses.has(obj.address)) {
          uniqueAddresses.add(obj.address);

          const placemark = new ymaps.Placemark(
            [obj.latitude, obj.longitude],
            {
              balloonContent: '<div style="border-radius: 5px;">' +
                '<div style="background-color: #de4c15; color: white; padding: 8px; padding: 5px; font-weight: bold;">' +
                obj.customer + '</div>' +

                '<a href="https://yandex.ru/maps/?text=' + obj.address + '" target="_blank" style="text-decoration: none; color: inherit; margin-right: 5px;">' +
                '<img src="/static/ico/geo-alt.svg" alt="address" style="width: 16px; height: 16px; vertical-align: middle; margin: 5px;">' +
                obj.address + '</a><br>' +

                (function () {
                  if (obj.manual_url) {
                    return '<a href="' + obj.manual_url + '" target="_blank" style="text-decoration: none; color: inherit; cursor: pointer;" onclick="event.stopPropagation();">' +
                      '<img src="/static/ico/gear.svg" alt="model" style="width: 16px; height: 16px; vertical-align: middle; margin: 5px;">' +
                      obj.model + '</a><br>';
                  } else {
                    return '<span style="color: #666;">' +
                      '<img src="/static/ico/gear.svg" alt="model" style="width: 16px; height: 16px; vertical-align: middle; margin: 5px; opacity: 0.5;">' +
                      obj.model + ' (нет руководства)</span><br>';
                  }
                })() +

                '<a href="tel:' + obj.phone + '" style="text-decoration: none; color: inherit;">' +
                '<img src="/static/ico/telephone.svg" alt="phone" style="width: 16px; height: 16px; vertical-align: middle; margin: 5px;">' +
                obj.phone + '</a><br>' +

                // Блок последнего осмотра
                (function () {
                  let serviceHtml = '<div style="margin-top: 5px; padding-top: 0px; border-top: 1px solid #eee;">';
                  serviceHtml += '<div style="font-weight: bold; color: #de4c15; margin-left: 5px; text-align: left;">Последнее ТО</div>';

                  if (obj.last_service_date) {
                    serviceHtml += '<div style="display: flex; align-items: center; margin-bottom: 4px;">';
                    serviceHtml += '<img src="/static/ico/calendar.svg" alt="date" style="width: 16px; height: 16px; vertical-align: middle; margin: 5px;">';
                    serviceHtml += '<span style="font-size: 14px;">' + obj.last_service_date + '</span>';
                    serviceHtml += '</div>';

                    if (obj.last_service_comments) {
                      serviceHtml += '<div style="display: flex; align-items: flex-start; margin: 4px;">';
                      serviceHtml += '<img src="/static/ico/chat-left-text.svg" alt="comments" style="width: 16px; height: 16px; vertical-align: top; margin: 5px; margin-top: 2px;">';
                      serviceHtml += '<span style="font-size: 14px; color: #666;">' + obj.last_service_comments + '</span>';
                      serviceHtml += '</div>';
                    }
                  } else {
                    serviceHtml += '<div style="color: #999; font-size: 14px; margin: 4px;">Нет данных об осмотрах</div>';
                  }

                  serviceHtml += '</div>';
                  return serviceHtml;
                })() +

                '</div>',
              clusterCaption: obj.customer
            },
            {
              iconLayout: 'default#image',
              iconImageHref: customIconSvg,
              iconImageSize: [30, 30],
              iconImageOffset: [-15, -35],
              iconImageClipRect: [[0, 0], [35, 35]],
              balloonCloseButton: false
            }
          );

          placemarks.push(placemark);
        }
      });

      if (placemarks.length > 0) {
        clusterer.add(placemarks);
        map.geoObjects.add(clusterer);
        map.setBounds(clusterer.getBounds(), { checkZoomRange: true });
      } else {
        // Если нет объектов, центрируем карту по умолчанию
        map.setCenter([53.9, 27.5], 7);
      }
    })
    .catch(error => {
      console.error('Ошибка загрузки объектов:', error);
    });
}

// Функция переключения состояния кнопки
function toggleFilter() {
  // Переключаем на следующее состояние
  currentFilterState = filterStates[currentFilterState.next];

  // Обновляем кнопку
  const button = document.getElementById('filterToggle');
  button.textContent = currentFilterState.text;
  button.className = 'filter-toggle-btn ' + currentFilterState.className;

  // Загружаем объекты с новым фильтром
  loadObjects(currentFilterState.filter);
}

ymaps.ready(function () {
  initMap();

  // Обработчик для кнопки фильтра
  document.getElementById('filterToggle').addEventListener('click', toggleFilter);

  // Обработчик события клика на карте
  map.events.add('click', function () {
    map.balloon.close();
    if (clusterer.balloon) {
      clusterer.balloon.close();
    }
  });
});