import os
import sys
import django
import requests
import time
from django.db import transaction
from django.conf import settings

# Настройка Django environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LIFTEH_project.settings')
    django.setup()
    print("Django успешно настроен")
except Exception as e:
    print(f"Ошибка настройки Django: {e}")
    sys.exit(1)

from LIFTEH.models import Object

def geocode_address(address):
    """Геокодирование адреса с помощью Yandex Geocoder API"""
    base_url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        'apikey': 'b0a03b93-14f2-4e5a-b38a-25ee1d5296e0',
        'geocode': address,
        'format': 'json',
        'results': 1
    }
    
    try:
        print(f"Геокодируем адрес: {address}")
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Извлекаем координаты из ответа
        features = data.get('response', {}).get('GeoObjectCollection', {}).get('featureMember', [])
        
        if features:
            geo_object = features[0]['GeoObject']
            pos = geo_object['Point']['pos']
            longitude, latitude = map(float, pos.split())
            
            # Проверяем, что координаты в пределах Беларуси
            if 23.0 <= longitude <= 33.0 and 51.0 <= latitude <= 57.0:
                return latitude, longitude
            else:
                print(f"Координаты вне Беларуси: {latitude}, {longitude}")
        
        return None, None
        
    except requests.RequestException as e:
        print(f"Ошибка при геокодировании адреса {address}: {e}")
        return None, None
    except (KeyError, ValueError) as e:
        print(f"Ошибка парсинга ответа для адреса {address}: {e}")
        return None, None

@transaction.atomic
def import_geocodes():
    """Основная функция для импорта геокодов"""
    print("Начинаем геокодирование адресов...")
    
    try:
        # Получаем объекты без координат
        objects_to_geocode = Object.objects.filter(
            latitude__isnull=True, 
            longitude__isnull=True
        )
        
        total = objects_to_geocode.count()
        print(f"Найдено {total} объектов без координат")
        
        if total == 0:
            print("Нет объектов для геокодирования")
            return
        
        success_count = 0
        error_count = 0
        
        for i, obj in enumerate(objects_to_geocode, 1):
            print(f"\nОбрабатываем объект {i}/{total}: {obj.address}")
            
            latitude, longitude = geocode_address(obj.address)
            
            if latitude and longitude:
                obj.latitude = latitude
                obj.longitude = longitude
                obj.save()
                success_count += 1
                print(f"✓ Найдены координаты: {latitude}, {longitude}")
            else:
                error_count += 1
                print(f"✗ Координаты не найдены для адреса: {obj.address}")
            
            # Задержка для соблюдения лимитов API
            time.sleep(1.1)
        
        print(f"\nГеокодирование завершено!")
        print(f"Успешно: {success_count}")
        print(f"Ошибок: {error_count}")
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import_geocodes()