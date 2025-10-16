// Обновленная функция создания балуна для зданий с кнопками
function createBuildingBalloonContent(obj) {
  return '<div style="border-radius: 5px; min-width: 250px;">' +
    '<div style="background-color: #de4c15; color: white; padding: 8px; font-weight: bold;">' +
    obj.customer + '</div>' +
    '<a href="https://yandex.ru/maps/?text=' + obj.address +
    '" target="_blank" style="text-decoration: none; color: inherit; margin-right: 5px; color: #666;">' +
    '<img src="/static/ico/geo-alt.svg" style="width: 16px; height: 16px; vertical-align: middle; margin: 5px;">' +
    obj.address + '</a><br>' +
    (obj.manual_url ?
      '<a href="' + obj.manual_url + '" target="_blank" style="text-decoration: none; color: inherit; cursor: pointer;" onclick="event.stopPropagation();">' +
      '<img src="/static/ico/gear.svg" style="width: 16px; height: 16px; vertical-align: middle; margin: 5px;">' +
      obj.model + '</a><br>' :
      '<span style="color: #666;">' +
      '<img src="/static/ico/gear.svg" style="width: 16px; height: 16px; vertical-align: middle; margin: 5px; opacity: 0.5;">' +
      obj.model + ' (*)</span><br>') +
    '<a href="tel:' + obj.phone + '" style="text-decoration: none; color: inherit; color: #666;">' +
    '<img src="/static/ico/telephone.svg" style="width: 16px; height: 16px; vertical-align: middle; margin: 5px;">' +
    obj.phone + '</a><br>' +
    createServiceInfo(obj) +

    // Добавляем кнопки в балун
    '<div class="balloon-buttons" style="display: flex; gap: 5px; justify-content: center;">' +
    '<button class="btn btn-primary btn-sm" onclick="openServiceModal(' + obj.id + '); event.stopPropagation();">' +
    'Добавить ТО</button>' +
    '<button class="btn btn-success btn-sm" onclick="openAvrModal(' + obj.id + '); event.stopPropagation();">' +
    'Добавить АВР</button>' +
    '</div>' +
    '</div>';
}

function createCarBalloonContent(tracker) {
  const lastUpdate = tracker.last_update || '';
  const [date, time] = lastUpdate.split(' ');
  return '<div style="border-radius: 5px; min-width: 200px;">' +
    '<div style="background-color: #007bff; color: white; padding: 8px; font-weight: bold;">' + tracker.car_id + '</div>' +
    '<div style="padding: 8px;">' +
    '<div style="margin-bottom: 4px;">' +
    '<img src="/static/ico/car-front-fill.svg" style="width: 16px; height: 16px; vertical-align: middle; margin-right: 5px;">' +
    '<strong>Автомобиль:</strong> ' + (tracker.tracker_id == 1801661 ? 'VW Crafter' : 'MB Sprinter') +
    '</div>' +
    '<div style="margin-bottom: 4px;">' +
    '<img src="/static/ico/nvme.svg" style="width: 16px; height: 16px; vertical-align: middle; margin-right: 5px;">' +
    '<strong>Гос номер:</strong> ' + (tracker.tracker_id == 1801661 ? 'AH 2456-3' : '1256 MB-3') +
    '</div>' +
    '<div style="margin-bottom: 4px;">' +
    '<img src="/static/ico/person.svg" style="width: 16px; height: 16px; vertical-align: middle; margin-right: 5px;">' +
    '<strong>Водитель:</strong> ' + tracker.driver_name +
    '</div>' +
    '<div style="margin-bottom: 4px;">' +
    '<img src="/static/ico/speedometer.svg" style="width: 16px; height: 16px; vertical-align: middle; margin-right: 5px;">' +
    '<strong>Скорость:</strong> ' + tracker.speed + ' км/ч' +
    '</div>' +
    '<div style="margin-bottom: 4px;">' +
    '<img src="/static/ico/radar.svg" style="width: 16px; height: 16px; vertical-align: middle; margin-right: 5px;">' +
    '<strong>Спутники:</strong> ' + tracker.satellites +
    '</div>' +
    '<div style="margin-bottom: 4px;">' +
    '<img src="/static/ico/123.svg" style="width: 16px; height: 16px; vertical-align: middle; margin-right: 5px;">' +
    '<strong>Пробег:</strong> ' + tracker.mileage + ' км' +
    '</div>' +
    '<div style="margin-bottom: 4px;">' +
    '<img src="/static/ico/recycle.svg" style="width: 16px; height: 16px; vertical-align: middle; margin-right: 5px;">' +
    '<strong>Дата обновления:</strong> ' + (date || '--.--.----') +
    '</div>' +
    '<div style="margin-bottom: 4px;">' +
    '<img src="/static/ico/recycle.svg" style="width: 16px; height: 16px; vertical-align: middle; margin-right: 5px;">' +
    '<strong>Время обновления:</strong> ' + (time || '--:--:--') +
    '</div>' +
    '</div></div>';
}

function createServiceInfo(obj) {
  let serviceHtml = '<div style="margin-top: 5px; padding-top: 0px; border-top: 1px solid #eee;">';
  serviceHtml += '<div style="font-weight: bold; color: #de4c15; margin-left: 5px; text-align: left;">Последнее ТО</div>';
  if (obj.last_service_date) {
    serviceHtml += '<div style="display: flex; align-items: center;">';
    serviceHtml += '<img src="/static/ico/calendar.svg" style="width: 16px; height: 16px; vertical-align: middle; margin: 5px;">';
    serviceHtml += '<span style="font-size: 14px; color: #666;">' + obj.last_service_date + '</span>';
    serviceHtml += '</div>';
    if (obj.last_service_comments) {
      serviceHtml += '<div style="display: flex; align-items: center;">';
      serviceHtml += '<img src="/static/ico/chat-left-text.svg" style="width: 16px; height: 16px; vertical-align: middle; margin: 5px;">';
      serviceHtml += '<span style="font-size: 14px; color: #666;">' + obj.last_service_comments + '</span>';
      serviceHtml += '</div>';
    }
  } else {
    serviceHtml += '<div style="color: #999; font-size: 14px; margin: 4px;">Нет данных об осмотрах</div>';
  }
  serviceHtml += '</div>';
  return serviceHtml;
}
