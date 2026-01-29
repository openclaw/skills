#!/usr/bin/env python3
"""
Clasifica precios PVPC como ALTO/MEDIO/BAJO
basado en percentiles del día
"""

import sys
from get_pvpc import get_pvpc_data, get_stats, get_current_price

def classify_price(price, stats):
    """
    Clasifica un precio como ALTO/MEDIO/BAJO
    basado en percentiles del día
    
    BAJO: < percentil 30
    MEDIO: percentil 30-70
    ALTO: > percentil 70
    """
    mean = stats['mean']
    price_range = stats['max'] - stats['min']
    
    # Calcular percentiles aproximados
    p30 = stats['min'] + (price_range * 0.3)
    p70 = stats['min'] + (price_range * 0.7)
    
    if price <= p30:
        return {
            'level': 'BAJO',
            'emoji': '🟢',
            'description': 'Precio bajo (oportunidad de ahorro)'
        }
    elif price >= p70:
        return {
            'level': 'ALTO',
            'emoji': '🔴',
            'description': 'Precio alto (evita consumos no esenciales)'
        }
    else:
        return {
            'level': 'MEDIO',
            'emoji': '🟡',
            'description': 'Precio medio'
        }

def get_price_context(price, stats):
    """
    Genera contexto completo del precio actual
    """
    classification = classify_price(price, stats)
    
    # Calcular desviación respecto a la media
    deviation = ((price - stats['mean']) / stats['mean']) * 100
    
    # Posición en el rango del día
    position = ((price - stats['min']) / (stats['max'] - stats['min'])) * 100
    
    return {
        'classification': classification,
        'deviation_percent': round(deviation, 1),
        'position_percent': round(position, 1),
        'below_mean': price < stats['mean'],
        'stats': stats
    }

def main():
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description='Clasifica precio PVPC')
    parser.add_argument('--price', type=float,
                       help='Precio a clasificar (€/kWh)')
    parser.add_argument('--now', action='store_true',
                       help='Clasifica precio actual')
    
    args = parser.parse_args()
    
    prices = get_pvpc_data()
    if not prices:
        print("No se pudieron obtener los datos", file=sys.stderr)
        sys.exit(1)
    
    stats = get_stats(prices)
    
    if args.now:
        current = get_current_price(prices)
        if not current:
            print("No hay datos para la hora actual", file=sys.stderr)
            sys.exit(1)
        price = current['price']
        hour = current['hour']
    elif args.price:
        price = args.price
        hour = None
    else:
        print("Usa --now o --price", file=sys.stderr)
        sys.exit(1)
    
    context = get_price_context(price, stats)
    cls = context['classification']
    
    print(f"{cls['emoji']} PRECIO {cls['level']}")
    if hour is not None:
        print(f"   {hour:02d}:00: {price:.4f} €/kWh")
    else:
        print(f"   {price:.4f} €/kWh")
    
    print(f"\n📊 Contexto del día:")
    print(f"   Media: {stats['mean']:.4f} €/kWh")
    print(f"   Mínimo: {stats['min']:.4f} €/kWh ({stats['min_hour']:02d}:00)")
    print(f"   Máximo: {stats['max']:.4f} €/kWh ({stats['max_hour']:02d}:00)")
    
    if context['below_mean']:
        print(f"\n💰 {abs(context['deviation_percent']):.1f}% por debajo de la media")
    else:
        print(f"\n💸 {context['deviation_percent']:.1f}% por encima de la media")
    
    print(f"📍 Posición: {context['position_percent']:.0f}% del rango diario")
    print(f"\n💡 {cls['description']}")

if __name__ == '__main__':
    main()
