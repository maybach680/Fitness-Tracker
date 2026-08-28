import httpx
from typing import Optional, Dict, Any
import os

OPENFOODFACTS_API = os.getenv("OPENFOODFACTS_API", "https://world.openfoodfacts.org")


async def get_product_by_barcode(barcode: str) -> Optional[Dict[str, Any]]:
    """
    Получить продукт из Open Food Facts по штрихкоду.
    
    API endpoint: https://world.openfoodfacts.org/api/v0/product/{barcode}.json
    
    Возвращает данные о продукте или None если не найден.
    """
    url = f"{OPENFOODFACTS_API}/api/v0/product/{barcode}.json"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            data = response.json()
            
            # Проверяем статус ответа
            if data.get('status') != 1:
                return None
            
            product = data.get('product', {})
            
            # Извлекаем нужные данные
            result = {
                'barcode': barcode,
                'name': product.get('product_name', product.get('product_name_en', 'Unknown Product')),
                'calories_per_100g': 0,
                'protein_per_100g': 0,
                'fat_per_100g': 0,
                'carbs_per_100g': 0,
            }
            
            # Получаем нутриенты
            nutriments = product.get('nutriments', {})
            
            # Калории могут быть в кДж (energy_100g) или в ккал (energy-kcal_100g)
            energy_kj = nutriments.get('energy_100g')
            energy_kcal = nutriments.get('energy-kcal_100g')
            
            if energy_kcal:
                result['calories_per_100g'] = round(energy_kcal, 1)
            elif energy_kj:
                # Конвертируем кДж в ккал: 1 ккал = 4.184 кДж
                result['calories_per_100g'] = round(energy_kj / 4.184, 1)
            
            # Белки, жиры, углеводы
            result['protein_per_100g'] = round(nutriments.get('proteins_100g', 0), 1)
            result['fat_per_100g'] = round(nutriments.get('fat_100g', 0), 1)
            result['carbs_per_100g'] = round(nutriments.get('carbohydrates_100g', 0), 1)
            
            return result
            
        except httpx.HTTPError as e:
            print(f"HTTP error while fetching from OFF: {e}")
            return None
        except Exception as e:
            print(f"Error while fetching from OFF: {e}")
            return None


async def search_products(query: str, limit: int = 20) -> list:
    """
    Поиск продуктов по названию в Open Food Facts.
    
    API endpoint: https://world.openfoodfacts.org/cgi/search.pl
    
    Возвращает список найденных продуктов.
    """
    url = f"{OPENFOODFACTS_API}/cgi/search.pl"
    params = {
        'search_terms': query,
        'search_simple': 1,
        'action': 'process',
        'json': 'true',
        'page_size': limit,
        'fields': 'code,product_name,nutriments'
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            products = data.get('products', [])
            results = []
            
            for product in products:
                nutriments = product.get('nutriments', {})
                energy_kj = nutriments.get('energy_100g')
                energy_kcal = nutriments.get('energy-kcal_100g')
                
                calories = 0
                if energy_kcal:
                    calories = round(energy_kcal, 1)
                elif energy_kj:
                    calories = round(energy_kj / 4.184, 1)
                
                results.append({
                    'barcode': product.get('code', ''),
                    'name': product.get('product_name', 'Unknown'),
                    'calories_per_100g': calories,
                    'protein_per_100g': round(nutriments.get('proteins_100g', 0), 1),
                    'fat_per_100g': round(nutriments.get('fat_100g', 0), 1),
                    'carbs_per_100g': round(nutriments.get('carbohydrates_100g', 0), 1),
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching OFF: {e}")
            return []
