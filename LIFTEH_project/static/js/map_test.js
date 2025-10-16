// ИСПРАВЛЕННЫЕ КОМАНДЫ ДЛЯ ОТЛАДКИ
window.debugMap = {
  checkVisibility: function () {
    console.log('=== ОТЛАДКА КАРТЫ ===');
    console.log('🏠 buildingPlacemarks:', buildingPlacemarks.length);
    console.log('🚗 carPlacemarks:', carPlacemarks.length);

    if (clusterer && typeof clusterer.getGeoObjects === 'function') {
      const geoObjects = clusterer.getGeoObjects();
      console.log('📍 Меток в кластеризаторе:', geoObjects.length);

      // Покажем первые 5 меток
      geoObjects.slice(0, 5).forEach((obj, i) => {
        try {
          const coords = obj.geometry.getCoordinates();
          console.log(`Метка ${i}:`, coords);
        } catch (error) {
          console.log(`Метка ${i}: Ошибка получения координат`);
        }
      });
    } else {
      console.log('❌ Кластеризатор не доступен');
    }

    // Проверим центр и зум карты
    console.log('🎯 Центр карты:', map.getCenter());
    console.log('🔍 Зум карты:', map.getZoom());
  },

  showAllObjects: function () {
    console.log('=== ВСЕ ОБЪЕКТЫ ===');
    buildingPlacemarks.forEach((pm, i) => {
      try {
        const coords = pm.geometry.getCoordinates();
        console.log(`Объект ${i}: ${coords[0]}, ${coords[1]}`);
      } catch (error) {
        console.log(`Объект ${i}: Ошибка координат`);
      }
    });
  },

  // Новая функция для проверки отображения меток
  checkMapObjects: function () {
    console.log('=== ПРОВЕРКА ОТОБРАЖЕНИЯ МЕТОК ===');
    if (clusterer && typeof clusterer.getGeoObjects === 'function') {
      const objects = clusterer.getGeoObjects();
      console.log('Видимых меток на карте:', objects.length);

      objects.forEach((obj, i) => {
        const coords = obj.geometry.getCoordinates();
        const pixelCoords = map.getPixelCoordinates(coords);
        console.log(`Метка ${i}: coords=${coords}, pixel=${pixelCoords}`);
      });
    }
  }
};

// Проверка через 3 секунды после загрузки
setTimeout(() => {
  console.log('=== ФИНАЛЬНАЯ ПРОВЕРКА ЧЕРЕЗ 3 СЕКУНДЫ ===');
  if (window.debugMap && typeof window.debugMap.checkVisibility === 'function') {
    window.debugMap.checkVisibility();
  } else {
    console.log('❌ debugMap не доступен');
  }
}, 3000);