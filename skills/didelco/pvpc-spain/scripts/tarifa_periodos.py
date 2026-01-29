#!/usr/bin/env python3
"""
Identifica periodos tarifarios 2.0TD (valle/llano/punta)
Ajustado por horario de verano/invierno
"""

import sys
from datetime import datetime

def is_summer_time():
    """
    Detecta si estamos en horario de verano (último domingo de marzo a último domingo de octubre)
    """
    now = datetime.now()
    month = now.month
    
    # Verano: abril a octubre (inclusive)
    # Invierno: noviembre a marzo
    return 4 <= month <= 10

def get_period_info(hour=None, weekday=None):
    """
    Devuelve el periodo tarifario para una hora y día de la semana dados
    hour: 0-23, si None usa hora actual
    weekday: 0=lunes...6=domingo, si None usa día actual
    
    Tarifa 2.0TD:
    - VALLE: 00:00-08:00 todos los días + sábados y domingos completos + festivos
    - LLANO: 08:00-10:00, 14:00-18:00, 22:00-00:00 (lun-vie)
    - PUNTA: 10:00-14:00, 18:00-22:00 (lun-vie)
    
    Nota: Los periodos son iguales en verano e invierno para la tarifa 2.0TD
    """
    if hour is None:
        hour = datetime.now().hour
    if weekday is None:
        weekday = datetime.now().weekday()
    
    # Sábado (5) o domingo (6) = todo el día valle
    if weekday in [5, 6]:
        return {
            'period': 'VALLE',
            'emoji': '🌙',
            'description': 'Fin de semana (todo el día valle)'
        }
    
    # Lunes a viernes
    if 0 <= hour < 8:
        return {
            'period': 'VALLE',
            'emoji': '🌙',
            'description': 'Periodo valle (00:00-08:00)'
        }
    elif 8 <= hour < 10 or 14 <= hour < 18 or 22 <= hour < 24:
        return {
            'period': 'LLANO',
            'emoji': '⚡',
            'description': 'Periodo llano'
        }
    else:  # 10-14 o 18-22
        return {
            'period': 'PUNTA',
            'emoji': '🔴',
            'description': 'Periodo punta'
        }

def get_next_valle():
    """Calcula cuándo empieza el próximo periodo valle"""
    now = datetime.now()
    current_hour = now.hour
    weekday = now.weekday()
    
    # Si es viernes tarde/noche, el siguiente valle es sábado todo el día
    if weekday == 4 and current_hour >= 8:
        return {
            'starts_in_hours': 24 - current_hour,
            'description': 'Sábado (todo el día valle)'
        }
    
    # Si es sábado o domingo, ya estamos en valle
    if weekday in [5, 6]:
        return {
            'starts_in_hours': 0,
            'description': 'Ahora (fin de semana)'
        }
    
    # Lunes a viernes
    if current_hour >= 8:
        # El siguiente valle es a las 00:00 del día siguiente
        hours_until = 24 - current_hour
        return {
            'starts_in_hours': hours_until,
            'description': '00:00-08:00 (mañana)'
        }
    else:
        # Estamos en valle ahora
        return {
            'starts_in_hours': 0,
            'description': 'Ahora (00:00-08:00)'
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Consulta periodos tarifarios 2.0TD')
    parser.add_argument('--now', action='store_true', 
                       help='Muestra periodo actual')
    parser.add_argument('--hour', type=int, 
                       help='Hora específica (0-23)')
    parser.add_argument('--weekday', type=int,
                       help='Día de la semana (0=lun, 6=dom)')
    parser.add_argument('--all', action='store_true',
                       help='Muestra todos los periodos del día')
    
    args = parser.parse_args()
    
    summer = is_summer_time()
    season = "verano ☀️" if summer else "invierno ❄️"
    
    if args.all:
        print(f"📅 Periodos tarifarios 2.0TD (horario de {season})\n")
        print("Lunes a Viernes:")
        print("  🌙 VALLE: 00:00-08:00")
        print("  ⚡ LLANO: 08:00-10:00, 14:00-18:00, 22:00-00:00")
        print("  🔴 PUNTA: 10:00-14:00, 18:00-22:00")
        print("\nSábados, Domingos y Festivos:")
        print("  🌙 VALLE: Todo el día (00:00-24:00)")
        print("\nNota: Los periodos son iguales en verano e invierno para 2.0TD")
    elif args.now or args.hour is not None:
        hour = args.hour if args.hour is not None else None
        weekday = args.weekday if args.weekday is not None else None
        
        period = get_period_info(hour, weekday)
        next_valle = get_next_valle()
        
        now = datetime.now()
        print(f"📅 {now.strftime('%d/%m/%Y %H:%M')} (horario de {season})\n")
        print(f"{period['emoji']} Periodo actual: {period['period']}")
        print(f"   {period['description']}\n")
        
        if next_valle['starts_in_hours'] > 0:
            print(f"🌙 Próximo valle: en {next_valle['starts_in_hours']}h")
            print(f"   {next_valle['description']}")
        else:
            print("🌙 Estás en periodo valle ahora")
    else:
        # Muestra info general
        print(f"Tarifa 2.0TD - Horario de {season}")
        print("\nPara ver periodos: --all")
        print("Para ver periodo actual: --now")

if __name__ == '__main__':
    main()
