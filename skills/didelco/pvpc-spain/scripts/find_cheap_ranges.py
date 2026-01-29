#!/usr/bin/env python3
"""
Encuentra rangos de horas con precios baratos
"""

import sys
import json
from get_pvpc import get_pvpc_data, get_stats

def find_cheap_hours(prices, percentile=30):
    """
    Encuentra horas con precio por debajo del percentil dado
    """
    if not prices:
        return []
    
    price_values = sorted([p['price'] for p in prices])
    threshold_idx = int(len(price_values) * percentile / 100)
    threshold = price_values[threshold_idx]
    
    cheap_hours = [p for p in prices if p['price'] <= threshold]
    return cheap_hours, threshold

def group_consecutive_hours(hours, tolerance=0.01):
    """
    Agrupa horas consecutivas con precios similares
    tolerance: diferencia máxima de precio para considerar similares (€/kWh)
    """
    if not hours:
        return []
    
    # Ordenar por hora
    sorted_hours = sorted(hours, key=lambda x: x['hour'])
    
    ranges = []
    current_range = [sorted_hours[0]]
    
    for i in range(1, len(sorted_hours)):
        prev = sorted_hours[i-1]
        curr = sorted_hours[i]
        
        # Agregar solo si es consecutiva Y precio similar
        if (curr['hour'] == prev['hour'] + 1 and 
            abs(curr['price'] - prev['price']) <= tolerance):
            current_range.append(curr)
        else:
            if len(current_range) >= 2:  # Solo rangos de 2+ horas
                ranges.append(current_range)
            current_range = [curr]
    
    # Añadir último rango
    if len(current_range) >= 2:
        ranges.append(current_range)
    
    return ranges

def format_range(hours_range):
    """Formatea un rango de horas para mostrar"""
    if not hours_range:
        return ""
    
    start = hours_range[0]['hour']
    last_hour = hours_range[-1]['hour']
    end = last_hour + 1
    
    # Si end es 24, mostrarlo como "al día siguiente"
    end_display = end if end < 24 else 0
    crosses_midnight = end >= 24
    
    min_price = min(h['price'] for h in hours_range)
    max_price = max(h['price'] for h in hours_range)
    avg_price = sum(h['price'] for h in hours_range) / len(hours_range)
    
    return {
        'start': start,
        'end': end_display,
        'end_raw': end,
        'crosses_midnight': crosses_midnight,
        'duration': len(hours_range),
        'min_price': round(min_price, 4),
        'max_price': round(max_price, 4),
        'avg_price': round(avg_price, 4)
    }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Encuentra horas baratas')
    parser.add_argument('--percentile', type=int, default=30, 
                       help='Percentil para considerar "barato" (default: 30)')
    parser.add_argument('--tolerance', type=float, default=0.01,
                       help='Diferencia máxima de precio para agrupar (€/kWh)')
    parser.add_argument('--json', action='store_true', help='Salida JSON')
    
    args = parser.parse_args()
    
    prices = get_pvpc_data()
    if not prices:
        print("No se pudieron obtener los datos", file=sys.stderr)
        sys.exit(1)
    
    stats = get_stats(prices)
    cheap_hours, threshold = find_cheap_hours(prices, args.percentile)
    ranges = group_consecutive_hours(cheap_hours, args.tolerance)
    
    if args.json:
        output = {
            'threshold': round(threshold, 4),
            'ranges': [format_range(r) for r in ranges],
            'stats': stats
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"🔋 Horas baratas hoy (≤{args.percentile}% del día, ≤{threshold:.4f} €/kWh)\n")
        
        if not ranges:
            print("No hay rangos baratos consecutivos hoy")
            sys.exit(0)
        
        # Ordenar rangos por duración (más largo primero)
        ranges.sort(key=lambda r: len(r), reverse=True)
        
        for i, r in enumerate(ranges, 1):
            info = format_range(r)
            end_str = f"{info['end']:02d}:00"
            if info['crosses_midnight']:
                end_str += " (día siguiente)"
            print(f"{i}. {info['start']:02d}:00 - {end_str} ({info['duration']}h)")
            print(f"   💰 {info['min_price']:.4f} - {info['max_price']:.4f} €/kWh (media: {info['avg_price']:.4f})")
            
            # Calcular ahorro vs media
            saving = ((stats['mean'] - info['avg_price']) / stats['mean']) * 100
            print(f"   💚 Ahorro vs media: {saving:.1f}%\n")

if __name__ == '__main__':
    main()
