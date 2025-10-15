let map;
let clusterer;
let carPlacemarks = [];
let buildingPlacemarks = [];
let updateInterval;

// Состояния кнопок
const objectsFilterStates = {
    all: "all",
    without_marks: "without_marks"
};

const transportFilterStates = {
    transport: "transport",
    no_transport: "no_transport"
};

let currentObjectsState = objectsFilterStates.without_marks;
let currentTransportState = transportFilterStates.transport;

// Переменные для прав доступа
let userHasLimitedAccess = false;

// Функция для проверки прав доступа
function checkUserAccess() {
    const hasAccessEntries = document.body.getAttribute('data-has-access-entries') === 'true';
    const isSuperuser = document.body.getAttribute('data-user-is-superuser') === 'true';
    
    // Если пользователь имеет ограниченные права (не суперпользователь И есть записи доступа)
    userHasLimitedAccess = (!isSuperuser && hasAccessEntries);
    
    if (userHasLimitedAccess) {
        const transportSwitch = document.getElementById('transportSwitch');
        const transportSwitchContainer = transportSwitch ? transportSwitch.closest('.filter-switch') : null;
        
        if (transportSwitchContainer) {
            transportSwitchContainer.style.display = 'none';
            console.log('Transport switch hidden for user with limited access');
        }
        
        // Автоматически выключаем транспорт
        currentTransportState = transportFilterStates.no_transport;
        if (transportSwitch) {
            transportSwitch.checked = false;
        }
    }
    
    console.log(`User access - Limited: ${userHasLimitedAccess}, Superuser: ${isSuperuser}`);
    return userHasLimitedAccess;
}

// // Вызов функции после загрузки DOM
// document.addEventListener('DOMContentLoaded', function() {
//     checkUserAccess();
// });

function toggleObjectsFilter() {
    const switchElement = document.getElementById('objectsSwitch');
    const isChecked = switchElement.checked;

    if (isChecked) {
        currentObjectsState = objectsFilterStates.all;
    } else {
        currentObjectsState = objectsFilterStates.without_marks;
    }

    loadObjects();
}

function toggleTransportFilter() {
    // Если пользователь с ограниченными правами, игнорируем переключение транспорта
    if (userHasLimitedAccess) {
        console.log('Transport toggle ignored for user with limited access');
        return;
    }

    const switchElement = document.getElementById('transportSwitch');
    const isChecked = switchElement.checked;

    // Останавливаем автообновление при выключении транспорта
    if (!isChecked && updateInterval) {
        clearInterval(updateInterval);
    }

    if (isChecked) {
        currentTransportState = transportFilterStates.transport;
    } else {
        currentTransportState = transportFilterStates.no_transport;
    }

    loadObjects();
}

// Функция для создания балуна метки с кнопками
function createPlacemarkBalloon(object) {
    const balloonContent = `
        <div class="balloon-content">
            <h4>${object.customer || 'Заказчик не указан'}</h4>
            <p><strong>Адрес:</strong> ${object.address || 'Не указан'}</p>
            <p><strong>Телефон:</strong> ${object.phone || 'Не указан'}</p>
            <div class="balloon-buttons">
                <button class="btn btn-primary btn-sm" onclick="openServiceModal(${object.id})">
                    Добавить ТО
                </button>
                <button class="btn btn-success btn-sm" onclick="openAvrModal(${object.id})">
                    Добавить АВР
                </button>
            </div>
        </div>
    `;
    return balloonContent;
}

// Функция для открытия модального окна ТО
function openServiceModal(objectId) {
    const url = `/service/add/${objectId}/`;
    const title = 'Добавление обслуживания';

    // Используем функцию из to.js
    if (typeof loadModalForm === 'function') {
        loadModalForm(url, title);
    } else {
        console.error('Функция loadModalForm не найдена');
    }
}

// Функция для открытия модального окна АВР
function openAvrModal(objectId) {
    const url = `/avr/add/${objectId}/`;
    const title = 'Добавление АВР';

    // Используем функцию из to.js
    if (typeof loadModalForm === 'function') {
        loadModalForm(url, title);
    } else {
        console.error('Функция loadModalForm не найдена');
    }
}

function initMap() {
    // ПЕРВОЕ: проверяем права доступа ДО инициализации карты
    const isLimitedAccess = checkUserAccess();
    
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

    map.geoObjects.add(clusterer);
    
    // ВТОРОЕ: загружаем объекты только после проверки прав
    loadObjects();
}

function loadObjects() {
    console.log(`Загрузка объектов: состояние объектов = ${currentObjectsState}, состояние транспорта = ${currentTransportState}`);
    console.log(`User has limited access: ${userHasLimitedAccess}`);
    console.log(`URL для объектов: /api/get_objects/?filter=${currentObjectsState}`);
    console.log(`URL для транспорта: /api/get_tracker_locations/`);
    
    clusterer.removeAll();
    clearCarPlacemarks();
    clearBuildingPlacemarks();

    const showTransport = currentTransportState === "transport" && !userHasLimitedAccess;

    // Загружаем объекты в зависимости от состояния
    switch (currentObjectsState) {
        case "all":
            console.log('Загрузка ВСЕХ объектов');
            loadBuildings("all");
            break;
        case "without_marks":
            console.log('Загрузка объектов без отметок');
            loadBuildings("without_marks");
            break;
    }

    if (showTransport && !userHasLimitedAccess) {
        console.log('Загрузка транспорта');
        loadCars();
    } else {
        console.log('Транспорт скрыт');
    }
}

function loadBuildings(filterType) {
    fetch(`/api/get_objects/?filter=${filterType}`)
        .then(response => {
            if (response.status === 403 || response.status === 401) {
                // Пользователь не авторизован - перенаправляем на страницу логина
                window.location.href = '/login/';
                return;
            }
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(objectsData => {
            console.log('Полученные объекты:', objectsData);
            
            if (objectsData.error) {
                console.error('Ошибка загрузки объектов:', objectsData.error);
                setBelarusBounds();
                return;
            }

            const placemarks = [];
            const uniqueAddresses = new Set();

            const customIconSvg = 'data:image/svg+xml;charset=utf-8,' +
                encodeURIComponent(
                    '<svg xmlns="http://www.w3.org/2000/svg" width="35" height="35" fill="currentColor" class="bi bi-geo-alt-fill" viewBox="0 0 16 16">' +
                    '<path fill="#de4c15" d="M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10m0-7a3 3 0 1 1 0-6 3 3 0 0 1 0 6"/>' +
                    '</svg>'
                );

            objectsData.forEach(function (obj) {
                if (obj.latitude && obj.longitude && !uniqueAddresses.has(obj.address)) {
                    uniqueAddresses.add(obj.address);
                    const placemark = createBuildingPlacemark(obj, customIconSvg);
                    placemarks.push(placemark);
                    buildingPlacemarks.push(placemark);
                }
            });

            if (placemarks.length > 0) { 
                clusterer.add(placemarks); 
                console.log(`Добавлено ${placemarks.length} объектов на карту`);
            } else {
                console.log('Нет объектов для отображения на карту');
            }

            if (currentTransportState === "no_transport" || userHasLimitedAccess) {
                setBelarusBounds();
            }
        })
        .catch(error => {
            console.error('Ошибка загрузки объектов:', error);
            setBelarusBounds();
        });
}

function loadCars() {
    // Если пользователь с ограниченными правами, не загружаем автомобили
    if (userHasLimitedAccess) {
        console.log('Skipping car load for user with limited access');
        return;
    }

    fetch('/api/get_tracker_locations/')
        .then(response => {
            if (response.status === 403 || response.status === 401) {
                // Пользователь не авторизован - перенаправляем на страницу логина
                window.location.href = '/login/';
                return;
            }
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(trackersData => {
            console.log('Получены данные трекеров:', trackersData);

            if (trackersData.error) {
                console.error('Ошибка загрузки трекеров:', trackersData.error);
                return;
            }

            const validTrackers = trackersData.filter(tracker =>
                tracker.latitude && tracker.longitude
            );

            if (validTrackers.length === 0) {
                console.log('Нет валидных данных для отображения автомобилей');
                return;
            }

            // Очищаем предыдущие метки автомобилей
            clearCarPlacemarks();

            validTrackers.forEach(function (tracker) {
                const placemark = createCarPlacemark(tracker);
                carPlacemarks.push(placemark);
                map.geoObjects.add(placemark);
            });

            console.log(`Добавлено ${validTrackers.length} автомобилей на карту`);

            // Если есть и объекты и автомобили, подгоняем карту под все
            if (buildingPlacemarks.length > 0 || validTrackers.length > 0) {
                setTimeout(() => {
                    const allPlacemarks = [...buildingPlacemarks, ...carPlacemarks];
                    if (allPlacemarks.length > 0) {
                        const group = new ymaps.GeoObjectCollection();
                        allPlacemarks.forEach(pm => group.add(pm));
                        const bounds = group.getBounds();
                        if (bounds) {
                            map.setBounds(bounds, {
                                checkZoomRange: true,
                                zoomMargin: 50
                            });
                        }
                    }
                }, 100);
            }

            if (currentTransportState === "transport" && !userHasLimitedAccess) {
                startAutoUpdate();
            }
        })
        .catch(error => {
            console.error('Ошибка загрузки автомобилей:', error);
        });
}


// Функция для установки фиксированных границ Беларуси
function setBelarusBounds() {
    // Fallback: центр Беларуси
    map.setCenter([53.9, 27.5], 7);
}

function createBuildingPlacemark(obj, customIconSvg) {
    return new ymaps.Placemark(
        [obj.latitude, obj.longitude],
        {
            balloonContent: createBuildingBalloonContent(obj),
            clusterCaption: obj.customer
        },
        {
            iconLayout: 'default#image',
            iconImageHref: customIconSvg,
            iconImageSize: [30, 30],
            iconImageOffset: [-15, -30],
            balloonCloseButton: false
        }
    );
}

function createCarPlacemark(tracker) {
    const carIconSvg = 'data:image/svg+xml;charset=utf-8,' +
        encodeURIComponent(
            '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24">' +
            '<path d="M2.52 3.515A2.5 2.5 0 0 1 4.82 2h6.362c1 0 1.904.596 2.298 1.515l.792 1.848c.075.175.21.319.38.404.5.25.855.715.965 1.262l.335 1.679q.05.242.049.49v.413c0 .814-.39 1.543-1 1.997V13.5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1-.5-.5v-1.338c-1.292.048-2.745.088-4 .088s-2.708-.04-4-.088V13.5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1-.5-.5v-1.892c-.61-.454-1-1.183-1-1.997v-.413a2.5 2.5 0 0 1 .049-.49l.335-1.68c.11-.546.465-1.012.964-1.261a.8.8 0 0 0 .381-.404l.792-1.848ZM3 10a1 1 0 1 0 0-2 1 1 0 0 0 0 2m10 0a1 1 0 1 0 0-2 1 1 0 0 0 0 2M6 8a1 1 0 0 0 0 2h4a1 1 0 1 0 0-2zM2.906 5.189a.51.51 0 0 0 .497.731c.91-.073 3.35-.17 4.597-.17s3.688.097 4.597.17a.51.51 0 0 0 .497-.731l-.956-1.913A.5.5 0 0 0 11.691 3H4.309a.5.5 0 0 0-.447.276L2.906 5.19Z" fill="#de4c15"/>' +
            '</svg>'
        );

    return new ymaps.Placemark(
        [tracker.latitude, tracker.longitude],
        {
            balloonContent: createCarBalloonContent(tracker),
            hintContent: tracker.car_id
        },
        {
            iconLayout: 'default#image',
            iconImageHref: carIconSvg,
            iconImageSize: [35, 35],
            iconImageOffset: [-10, -20],
            balloonCloseButton: false
        }
    );
}

function clearCarPlacemarks() {
    carPlacemarks.forEach(placemark => {
        map.geoObjects.remove(placemark);
    });
    carPlacemarks = [];
}

function clearBuildingPlacemarks() {
    buildingPlacemarks = [];
}

// Обновите функцию startAutoUpdate
function startAutoUpdate() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }

    // Если пользователь с ограниченными правами, не запускаем автообновление
    if (userHasLimitedAccess) {
        console.log('Auto-update disabled for user with limited access');
        return;
    }

    updateInterval = setInterval(() => {
        if (currentTransportState === "transport") {
            fetch('/api/get_tracker_locations/')
                .then(response => response.json())
                .then(trackersData => {
                    if (!trackersData.error) {
                        trackersData.forEach(tracker => {
                            const existingPlacemark = carPlacemarks.find(p =>
                                p.properties.get('balloonContent').includes(tracker.car_id)
                            );
                            if (existingPlacemark && tracker.latitude && tracker.longitude) {
                                existingPlacemark.geometry.setCoordinates([tracker.latitude, tracker.longitude]);
                            }
                        });
                    }
                })
                .catch(error => {
                    console.error('Ошибка обновления автомобилей:', error);
                });
        }
    }, 30000);
}

// Функции переключения кнопок
function toggleObjectsFilter() {
    const switchElement = document.getElementById('objectsSwitch');
    const isChecked = switchElement.checked;

    if (isChecked) {
        currentObjectsState = objectsFilterStates.all;
    } else {
        currentObjectsState = objectsFilterStates.without_marks;
    }

    loadObjects();
}

function toggleTransportFilter() {
    // Если пользователь с ограниченными правами, игнорируем переключение транспорта
    if (userHasLimitedAccess) {
        console.log('Transport toggle ignored for user with limited access');
        return;
    }

    const switchElement = document.getElementById('transportSwitch');
    const isChecked = switchElement.checked;

    // Останавливаем автообновление при выключении транспорта
    if (!isChecked && updateInterval) {
        clearInterval(updateInterval);
    }

    if (isChecked) {
        currentTransportState = transportFilterStates.transport;
    } else {
        currentTransportState = transportFilterStates.no_transport;
    }

    loadObjects();
}

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

// Инициализация карты
ymaps.ready(function () {
    initMap();

    // Обработчики для переключателей
    document.getElementById('objectsSwitch').addEventListener('change', toggleObjectsFilter);
    document.getElementById('transportSwitch').addEventListener('change', toggleTransportFilter);

    map.events.add('click', function () {
        map.balloon.close();
        if (clusterer.balloon) {
            clusterer.balloon.close();
        }
    });
});

