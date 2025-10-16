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
let userHasLimitedAccess = false;
let isLoading = false;

// Функция для проверки прав доступа
function checkUserAccess() {
    const hasAccessEntries = document.body.getAttribute('data-has-access-entries') === 'true';
    const isSuperuser = document.body.getAttribute('data-user-is-superuser') === 'true';

    userHasLimitedAccess = (!isSuperuser && hasAccessEntries);

    if (userHasLimitedAccess) {
        const transportSwitch = document.getElementById('transportSwitch');
        const transportSwitchContainer = transportSwitch ? transportSwitch.closest('.filter-switch') : null;

        if (transportSwitchContainer) {
            transportSwitchContainer.style.display = 'none';
            // console.log('Transport switch hidden for user with limited access');
        }

        currentTransportState = transportFilterStates.no_transport;
        if (transportSwitch) {
            transportSwitch.checked = false;
        }
    }
    // console.log(`User access - Limited: ${userHasLimitedAccess}, Superuser: ${isSuperuser}`);
    return userHasLimitedAccess;
}

function initMap() {
    const isLimitedAccess = checkUserAccess();

    if (map) {
        map.destroy();
    }

    map = new ymaps.Map('map', {
        center: [53.9, 27.5],
        zoom: 7
    });

    // Удаляем все стандартные элементы управления
    // map.controls.remove('zoomControl');
    map.controls.remove('geolocationControl');
    map.controls.remove('searchControl');
    map.controls.remove('typeSelector');
    map.controls.remove('fullscreenControl');
    map.controls.remove('rulerControl');
    map.controls.remove('trafficControl');
    map.controls.remove('routeButtonControl');

    // Инициализируем кластеризатор с настройками, которые не скрывают отдельные метки
    clusterer = new ymaps.Clusterer({
        preset: 'islands#invertedOrangeClusterIcons',
        clusterDisableClickZoom: true,
        clusterOpenBalloonOnClick: true,
        gridSize: 64,
        clusterHideIconOnBalloonOpen: false,
        geoObjectHideIconOnBalloonOpen: false,
        groupByCoordinates: false
    });

    map.geoObjects.add(clusterer);

    loadObjects();
}

function loadObjects() {
    // console.log('=== НАЧАЛО loadObjects ===');
    // console.log('isLoading:', isLoading);
    // console.log('buildingPlacemarks до очистки:', buildingPlacemarks.length);
    // console.log('carPlacemarks до очистки:', carPlacemarks.length);

    if (clusterer && typeof clusterer.getGeoObjects === 'function') {
        // console.log('clusterer geoObjects до очистки:', clusterer.getGeoObjects().length);
    }

    if (isLoading) {
        // console.log('Загрузка уже выполняется, пропускаем...');
        return;
    }

    isLoading = true;
    // console.log(`Загрузка объектов: состояние объектов = ${currentObjectsState}, состояние транспорта = ${currentTransportState}`);

    clearAllPlacemarks();

    const showTransport = currentTransportState === "transport" && !userHasLimitedAccess;

    loadBuildings(currentObjectsState).then(() => {
        if (showTransport && !userHasLimitedAccess) {
            // console.log('Загрузка транспорта после объектов');
            return loadCars();
        } else {
            // console.log('Транспорт скрыт');
            return Promise.resolve();
        }
    }).then(() => {
        updateMapBounds();
    }).catch(error => {
        console.error('Ошибка при загрузке данных:', error);
    }).finally(() => {
        // console.log('buildingPlacemarks после загрузки:', buildingPlacemarks.length);
        // console.log('carPlacemarks после загрузки:', carPlacemarks.length);
        if (clusterer && typeof clusterer.getGeoObjects === 'function') {
        }
        isLoading = false;
    });
}

function loadBuildings(filterType) {
    return new Promise((resolve, reject) => {
        fetch(`/api/get_objects/?filter=${filterType}`)
            .then(response => {
                if (response.status === 403 || response.status === 401) {
                    window.location.href = '/login/';
                    return reject(new Error('Unauthorized'));
                }
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(objectsData => {
                // console.log('Полученные объекты:', objectsData);
                if (objectsData.error) {
                    console.error('Ошибка загрузки объектов:', objectsData.error);
                    resolve();
                    return;
                }

                const placemarks = [];
                const uniqueAddresses = new Set();
                const uniqueCoords = new Set();

                const customIconSvg = 'data:image/svg+xml;charset=utf-8,' +
                    encodeURIComponent(
                        '<svg xmlns="http://www.w3.org/2000/svg" width="35" height="35" fill="currentColor" class="bi bi-geo-alt-fill" viewBox="0 0 16 16">' +
                        '<path fill="#de4c15" d="M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10m0-7a3 3 0 1 1 0-6 3 3 0 0 1 0 6"/>' +
                        '</svg>'
                    );

                objectsData.forEach(function (obj) {
                    if (obj.latitude && obj.longitude && !uniqueAddresses.has(obj.address)) {
                        const coordKey = `${obj.latitude.toFixed(6)},${obj.longitude.toFixed(6)}`;
                        if (!uniqueCoords.has(coordKey)) {
                            uniqueAddresses.add(obj.address);
                            uniqueCoords.add(coordKey);

                            const placemark = createBuildingPlacemark(obj, customIconSvg);
                            placemarks.push(placemark);
                            buildingPlacemarks.push(placemark);
                        } else {
                            // console.log('🚫 Пропущен дубликат координат:', coordKey, obj.address);
                        }
                    }
                });
                // console.log(`📍 Уникальных координат: ${uniqueCoords.size}`);
                // console.log(`📍 Уникальных адресов: ${uniqueAddresses.size}`);
                if (placemarks.length > 0) {
                    clusterer.add(placemarks);
                    // console.log(`✅ Добавлено ${placemarks.length} объектов в кластеризатор`);

                    setTimeout(() => {
                        if (clusterer && typeof clusterer.getGeoObjects === 'function') {
                            // console.log('🔍 Меток в кластеризаторе после добавления:', clusterer.getGeoObjects().length);
                        }
                    }, 100);
                } else {
                    // console.log('❌ Нет объектов для отображения на карту');
                }

                resolve();
            })
            .catch(error => {
                console.error('Ошибка загрузки объектов:', error);
                reject(error);
            });
    });
}

function loadCars() {
    return new Promise((resolve, reject) => {
        if (userHasLimitedAccess) {
            console.log('Skipping car load for user with limited access');
            resolve();
            return;
        }

        fetch('/api/get_tracker_locations/')
            .then(response => {
                if (response.status === 403 || response.status === 401) {
                    window.location.href = '/login/';
                    return reject(new Error('Unauthorized'));
                }
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(trackersData => {
                // console.log('Получены данные трекеров:', trackersData);

                if (trackersData.error) {
                    // console.error('Ошибка загрузки трекеров:', trackersData.error);
                    resolve();
                    return;
                }

                const validTrackers = trackersData.filter(tracker =>
                    tracker.latitude && tracker.longitude
                );

                if (validTrackers.length === 0) {
                    // console.log('Нет валидных данных для отображения автомобилей');
                    resolve();
                    return;
                }
                clearCarPlacemarks();
                validTrackers.forEach(function (tracker) {
                    const placemark = createCarPlacemark(tracker);
                    carPlacemarks.push(placemark);
                    map.geoObjects.add(placemark);
                });

                if (currentTransportState === "transport" && !userHasLimitedAccess) {
                    startAutoUpdate();
                }
                // console.log(`✅ Добавлено ${validTrackers.length} автомобилей на карту`);
                resolve();
            })
            .catch(error => {
                console.error('Ошибка загрузки автомобилей:', error);
                reject(error);
            });
    });
}

// Добавьте в начало файла с другими переменными
let isFirstLoad = true;
// ФУНКЦИЯ ОТРИСОВКИ ОБЪЕКТОВ
function updateMapBounds() {
    setTimeout(() => {
        const allPlacemarks = [...buildingPlacemarks, ...carPlacemarks];
        // console.log(`📍 Всего меток для границ: ${allPlacemarks.length}`);

        if (allPlacemarks.length > 0) {
            if (isFirstLoad) {
                // Только при первой загрузке устанавливаем границы
                calculateBoundsManually();
                isFirstLoad = false;
            } else {
                // При последующих переключениях фильтров сохраняем текущий вид
                // console.log('📍 Сохранены текущие границы карты (не первая загрузка)');
            }
        } else {
            map.setCenter([53.9, 27.5], 7);
            // console.log('📍 Установлены границы по умолчанию');
            isFirstLoad = true; // Сбрасываем флаг если меток нет
        }
    }, 500);
}

// Ручной расчет границ
function calculateBoundsManually() {
    const allPlacemarks = [...buildingPlacemarks, ...carPlacemarks];
    const coordinates = [];

    // Собираем все координаты
    allPlacemarks.forEach(pm => {
        if (pm && pm.geometry) {
            try {
                const coords = pm.geometry.getCoordinates();
                if (coords && Array.isArray(coords) && coords.length === 2) {
                    coordinates.push(coords);
                }
            } catch (error) {
                // console.log('Ошибка получения координат метки:', error);
            }
        }
    });

    if (coordinates.length === 0) {
        // console.log('❌ Нет валидных координат для расчета границ');
        map.setCenter([53.9, 27.5], 7);
        return;
    }
    // Вычисляем минимальные и максимальные координаты
    let minLat = coordinates[0][0];
    let maxLat = coordinates[0][0];
    let minLon = coordinates[0][1];
    let maxLon = coordinates[0][1];

    coordinates.forEach(coord => {
        minLat = Math.min(minLat, coord[0]);
        maxLat = Math.max(maxLat, coord[0]);
        minLon = Math.min(minLon, coord[1]);
        maxLon = Math.max(maxLon, coord[1]);
    });

    // Добавляем отступы
    const latMargin = (maxLat - minLat) * 0.1;
    const lonMargin = (maxLon - minLon) * 0.1;

    const bounds = [
        [minLat - latMargin, minLon - lonMargin],
        [maxLat + latMargin, maxLon + lonMargin]
    ];

    // console.log('📐 Рассчитанные границы:', bounds);

    try {
        map.setBounds(bounds(), { // ПРОБЛЕМА БЫЛА ТУТ
            checkZoomRange: true,
            zoomMargin: 0
        });
        console.log('✅ Границы установлены через ручной расчет');
    } catch (error) {
        // console.log('❌ Ошибка установки границ:', error);
        // Последний резервный способ
        const centerLat = (minLat + maxLat) / 2;
        const centerLon = (minLon + maxLon) / 2;
        map.setCenter([centerLat, centerLon], 7);
        // console.log('📍 Установлен центр карты по координатам меток');
    }
}

function clearAllPlacemarks() {
    if (clusterer && typeof clusterer.removeAll === 'function') {
        clusterer.removeAll();
    }
    clearCarPlacemarks();
    buildingPlacemarks = [];
    setTimeout(() => {
        if (clusterer && typeof clusterer.getGeoObjects === 'function') {
        }
    }, 50);
}

// ИНИЦИИРОВАНИЕ ОЧИСТКИ АВТОМОБИЛЕЙ
function clearCarPlacemarks() {
    carPlacemarks.forEach(placemark => {
        map.geoObjects.remove(placemark);
    });
    carPlacemarks = [];
}

function createBuildingPlacemark(obj, customIconSvg) {
    const placemark = new ymaps.Placemark(
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
            balloonCloseButton: false,
            hideIconOnBalloonOpen: false
        }
    );
    return placemark;
}

function createCarPlacemark(tracker) {
    const carIconSvg = 'data:image/svg+xml;charset=utf-8,' +
        encodeURIComponent(
            '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24">' +
            '<path d="M2.52 3.515A2.5 2.5 0 0 1 4.82 2h6.362c1 0 1.904.596 2.298 1.515l.792 1.848c.075.175.21.319.38.404.5.25.855.715.965 1.262l.335 1.679q.05.242.049.49v.413c0 .814-.39 1.543-1 1.997V13.5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1-.5-.5v-1.338c-1.292.048-2.745.088-4 .088s-2.708-.04-4-.088V13.5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1-.5-.5v-1.892c-.61-.454-1-1.183-1-1.997v-.413a2.5 2.5 0 0 1 .049-.49l.335-1.68c.11-.546.465-1.012.964-1.261a.8.8 0 0 0 .381-.404l.792-1.848ZM3 10a1 1 0 1 0 0-2 1 1 0 0 0 0 2m10 0a1 1 0 1 0 0-2 1 1 0 0 0 0 2M6 8a1 1 0 0 0 0 2h4a1 1 0 1 0 0-2zM2.906 5.189a.51.51 0 0 0 .497.731c.91-.073 3.35-.17 4.597-.17s3.688.097 4.597.17a.51.51 0 0 0 .497-.731l-.956-1.913A.5.5 0 0 0 11.691 3H4.309a.5.5 0 0 0-.447.276L2.906 5.19Z" fill="#de4c15"/>' +
            '</svg>'
        );

    const placemark = new ymaps.Placemark(
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
            balloonCloseButton: false,
            hideIconOnBalloonOpen: false
        }
    );
    return placemark;
}


function startAutoUpdate() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }

    if (userHasLimitedAccess) {
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
    if (userHasLimitedAccess) {
        return;
    }

    const switchElement = document.getElementById('transportSwitch');
    const isChecked = switchElement.checked;

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


// Инициализация карты
ymaps.ready(function () {
    initMap();

    document.getElementById('objectsSwitch').addEventListener('change', toggleObjectsFilter);
    document.getElementById('transportSwitch').addEventListener('change', toggleTransportFilter);

    map.events.add('click', function () {
        map.balloon.close();
        if (clusterer.balloon) {
            clusterer.balloon.close();
        }
    });
});
