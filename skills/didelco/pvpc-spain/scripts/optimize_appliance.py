#!/usr/bin/env python3
"""
Encuentra el mejor momento para usar electrodomésticos
según duración y precios PVPC
"""

import sys
import json
from get_pvpc import get_pvpc_data, get_stats

def find_best_window(prices, duration):
    """
    Encuentra la ventana de N horas consecutivas con menor coste total
    """
    if not prices or duration > len(prices):
        return None
    
    # Ordenar por hora para asegurar secuencia
    sorted_prices = sorted(prices, key=lambda x: x['hour'])
    
    best_window = None
    best_cost = float('inf')
    
    for i in range(len(sorted_prices) - duration + 1):
        window = sorted_prices[i:i+duration]
        
        # Verificar que las horas son consecutivas
        if all(window[j]['hour'] == window[j-1]['hour'] + 1 
               for j in range(1, len(window))):
            
            total_cost = sum(h['price'] for h in window)
            
            if total_cost < best_cost:
                best_cost = total_cost
                best_window = window
    
    if best_window:
        return {
            'start': best_window[0]['hour'],
            'end': best_window[-1]['hour'] + 1,
            'hours': best_window,
            'total_cost': round(best_cost, 4),
            'avg_price': round(best_cost / duration, 4)
        }
    
    return None

def find_alternatives(prices, duration, best_window, threshold=1.10):
    """
    Encuentra ventanas alternativas dentro del threshold (ej: +10%)
    """
    if not best_window:
        return []
    
    sorted_prices = sorted(prices, key=lambda x: x['hour'])
    alternatives = []
    max_cost = best_window['total_cost'] * threshold
    
    for i in range(len(sorted_prices) - duration + 1):
        window = sorted_prices[i:i+duration]
        
        if all(window[j]['hour'] == window[j-1]['hour'] + 1 
               for j in range(1, len(window))):
            
            total_cost = sum(h['price'] for h in window)
            start_hour = window[0]['hour']
            
            # Excluir la mejor ventana y las que superan threshold
            if (start_hour != best_window['start'] and 
                total_cost <= max_cost):
                alternatives.append({
                    'start': start_hour,
                    'end': window[-1]['hour'] + 1,
                    'total_cost': round(total_cost, 4),
                    'diff_percent': round(((total_cost - best_window['total_cost']) / 
                                         best_window['total_cost']) * 100, 1)
                })
    
    # Ordenar por coste
    alternatives.sort(key=lambda x: x['total_cost'])
    return alternatives[:2]  # Top 2 alternativas

def main():
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description='Optimiza uso de electrodomésticos')
    parser.add_argument('--duration', type=int, required=True,
                       help='Duración en horas del electrodoméstico')
    parser.add_argument('--name', default='electrodoméstico',
                       help='Nombre del electrodoméstico (ej: lavadora)')
    parser.add_argument('--alternatives', type=int, default=2,
                       help='Número de alternativas a mostrar')
    parser.add_argument('--json', action='store_true', help='Salida JSON')
    
    args = parser.parse_args()
    
    prices = get_pvpc_data()
    if not prices:
        print("No se pudieron obtener los datos", file=sys.stderr)
        sys.exit(1)
    
    stats = get_stats(prices)
    best = find_best_window(prices, args.duration)
    
    if not best:
        print(f"No se encontró ventana de {args.duration}h consecutivas", file=sys.stderr)
        sys.exit(1)
    
    alternatives = find_alternatives(prices, args.duration, best)
    
    if args.json:
        output = {
            'appliance': args.name,
            'duration': args.duration,
            'best': best,
            'alternatives': alternatives,
            'stats': stats
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        emoji_map = {
            'lavadora': '🧺',
            'lavavajillas': '🍽️',
            'secadora': '👕',
            'horno': '🍕',
            'calefaccion': '🔥'
        }
        emoji = emoji_map.get(args.name.lower(), '⚡')
        
        print(f"{emoji} Mejor momento para {args.name} ({args.duration}h)\n")
        print(f"⏰ Inicio recomendado: {best['start']:02d}:00")
        print(f"⏱️  Finaliza: {best['end']:02d}:00\n")
        print(f"💰 Coste total: {best['total_cost']:.4f} €")
        print(f"📊 Precio medio: {best['avg_price']:.4f} €/kWh\n")
        
        print("📈 Desglose por hora:")
        for h in best['hours']:
            print(f"   • {h['hour']:02d}:00: {h['price']:.4f} €/kWh")
        
        # Calcular ahorro vs media
        cost_at_avg = stats['mean'] * args.duration
        saving = cost_at_avg - best['total_cost']
        saving_percent = (saving / cost_at_avg) * 100
        
        print(f"\n💚 Ahorro vs media del día: {saving:.4f} € ({saving_percent:.1f}%)")
        
        # Alternativas
        if alternatives:
            print(f"\n🔄 Alternativas:")
            for i, alt in enumerate(alternatives, 1):
                print(f"   {i}. {alt['start']:02d}:00-{alt['end']:02d}:00")
                print(f"      Coste: {alt['total_cost']:.4f} € (+{alt['diff_percent']}%)")

if __name__ == '__main__':
    main()
