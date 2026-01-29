#!/usr/bin/env python3
"""
Consulta precios PVPC desde la API de ESIOS (Red Eléctrica de España)
Sin necesidad de token - usa endpoint público alternativo
"""

import json
import sys
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError

def get_pvpc_data(date_str=None):
    """
    Obtiene datos PVPC para una fecha específica
    date_str: formato YYYY-MM-DD, por defecto hoy
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    # API pública de ESIOS (no requiere token)
    url = f"https://api.esios.ree.es/archives/70/download_json?locale=es&date={date_str}"
    
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return parse_pvpc_response(data)
    except URLError as e:
        print(f"Error consultando API: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error procesando datos: {e}", file=sys.stderr)
        return None

def parse_pvpc_response(data):
    """Parsea respuesta de la API y extrae precios por hora"""
    if 'PVPC' not in data:
        return None
    
    prices = []
    for entry in data['PVPC']:
        try:
            # Formato "00-01" -> hora 0, "01-02" -> hora 1, etc.
            hour_str = entry['Hora'].split('-')[0]
            hour = int(hour_str)
            if hour == 24:  # "24-01" del día siguiente
                continue
            # Precio en €/kWh (viene en €/MWh, dividir por 1000)
            price = float(entry['PCB'].replace(',', '.')) / 1000
            prices.append({'hour': hour, 'price': round(price, 4)})
        except (KeyError, ValueError) as e:
            continue
    
    return prices

def get_current_price(prices):
    """Obtiene el precio de la hora actual"""
    current_hour = datetime.now().hour
    for p in prices:
        if p['hour'] == current_hour:
            return p
    return None

def get_stats(prices):
    """Calcula estadísticas del día"""
    if not prices:
        return None
    
    price_values = [p['price'] for p in prices]
    return {
        'min': min(price_values),
        'max': max(price_values),
        'mean': round(sum(price_values) / len(price_values), 4),
        'min_hour': min(prices, key=lambda x: x['price'])['hour'],
        'max_hour': max(prices, key=lambda x: x['price'])['hour']
    }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Consulta precios PVPC')
    parser.add_argument('--date', help='Fecha YYYY-MM-DD (por defecto hoy)')
    parser.add_argument('--now', action='store_true', help='Muestra precio actual')
    parser.add_argument('--all', action='store_true', help='Muestra todos los precios del día')
    parser.add_argument('--json', action='store_true', help='Salida en formato JSON')
    
    args = parser.parse_args()
    
    prices = get_pvpc_data(args.date)
    
    if not prices:
        print("No se pudieron obtener los datos", file=sys.stderr)
        sys.exit(1)
    
    stats = get_stats(prices)
    
    if args.json:
        output = {
            'prices': prices,
            'stats': stats,
            'current': get_current_price(prices)
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    elif args.now:
        current = get_current_price(prices)
        if current:
            print(f"Precio actual ({current['hour']:02d}:00): {current['price']:.4f} €/kWh")
            print(f"Mínimo hoy: {stats['min']:.4f} €/kWh ({stats['min_hour']:02d}:00)")
            print(f"Máximo hoy: {stats['max']:.4f} €/kWh ({stats['max_hour']:02d}:00)")
            print(f"Media hoy: {stats['mean']:.4f} €/kWh")
        else:
            print("No hay datos para la hora actual", file=sys.stderr)
            sys.exit(1)
    elif args.all:
        for p in prices:
            print(f"{p['hour']:02d}:00 - {p['price']:.4f} €/kWh")
    else:
        # Por defecto muestra resumen
        print(f"Resumen PVPC ({datetime.now().strftime('%d/%m/%Y')})")
        print(f"Min: {stats['min']:.4f} €/kWh ({stats['min_hour']:02d}:00)")
        print(f"Max: {stats['max']:.4f} €/kWh ({stats['max_hour']:02d}:00)")
        print(f"Media: {stats['mean']:.4f} €/kWh")

if __name__ == '__main__':
    main()
