---
name: pvpc-spain
description: Consulta y optimiza precios de electricidad PVPC en España (tarifa 2.0TD para usuarios domésticos). Usa cuando necesites (1) precio actual con contexto (alto/medio/bajo vs día), (2) identificar periodos valle/llano/punta según horario, (3) encontrar las horas más baratas del día, (4) optimizar cuándo usar electrodomésticos (lavadora, lavavajillas, secadora, etc.) para minimizar coste eléctrico.
---

# PVPC España

Skill para consultar precios PVPC (Precio Voluntario Pequeño Consumidor) en España y optimizar el consumo eléctrico. Todos los datos se obtienen de la API pública de ESIOS (Red Eléctrica de España) para la tarifa 2.0TD.

## Consultas disponibles

### 1. Precio actual con contexto

Muestra el precio actual clasificado como ALTO/MEDIO/BAJO según percentiles del día.

```bash
# Precio actual completo
python scripts/get_pvpc.py --now

# Clasificación detallada
python scripts/precio_referencia.py --now
```

**Respuesta incluye:**
- Precio actual (€/kWh)
- Mínimo y máximo del día
- Clasificación: BAJO (<percentil 30), MEDIO (30-70), ALTO (>70)
- Desviación respecto a la media del día

### 2. Periodos tarifarios (valle/llano/punta)

Identifica el periodo actual según tarifa 2.0TD, ajustado por día de la semana.

```bash
# Periodo actual
python scripts/tarifa_periodos.py --now

# Ver todos los periodos
python scripts/tarifa_periodos.py --all
```

**Periodos 2.0TD:**
- **VALLE** 🌙: 00:00-08:00 (todos los días) + sábados/domingos completos
- **LLANO** ⚡: 08:00-10:00, 14:00-18:00, 22:00-00:00 (lun-vie)
- **PUNTA** 🔴: 10:00-14:00, 18:00-22:00 (lun-vie)

**Nota:** Los periodos son iguales en horario de verano e invierno para 2.0TD.

### 3. Horas más baratas del día

Encuentra rangos de horas con precios por debajo del percentil 30 del día.

```bash
# Rangos baratos (por defecto percentil 30)
python scripts/find_cheap_ranges.py

# Ajustar percentil
python scripts/find_cheap_ranges.py --percentile 40
```

**Respuesta incluye:**
- Rangos de 2+ horas consecutivas con precios bajos
- Precio mínimo/máximo/medio de cada rango
- Ahorro porcentual vs media del día
- Ordenados por duración (rangos más largos primero)

### 4. Optimizar electrodomésticos

Encuentra la ventana de N horas consecutivas con menor coste total.

```bash
# Lavadora (2 horas por defecto)
python scripts/optimize_appliance.py --duration 2 --name lavadora

# Lavavajillas (3 horas)
python scripts/optimize_appliance.py --duration 3 --name lavavajillas

# Secadora (1.5 horas)
python scripts/optimize_appliance.py --duration 2 --name secadora
```

**Respuesta incluye:**
- Hora óptima de inicio y fin
- Coste total del ciclo (€)
- Desglose de precio por hora
- Ahorro vs usar en horario medio
- Hasta 2 alternativas con <10% diferencia de coste

## Salida JSON

Todos los scripts soportan `--json` para integración programática:

```bash
python scripts/get_pvpc.py --json
python scripts/find_cheap_ranges.py --json
python scripts/optimize_appliance.py --duration 3 --json
```

## Ejemplos de uso desde el agente

**Usuario:** "¿Cuánto cuesta la luz ahora?"
```bash
python scripts/get_pvpc.py --now
python scripts/precio_referencia.py --now
```

**Usuario:** "¿Cuándo es más barata la luz hoy?"
```bash
python scripts/find_cheap_ranges.py
```

**Usuario:** "¿Cuándo pongo la lavadora?"
```bash
python scripts/optimize_appliance.py --duration 2 --name lavadora
```

**Usuario:** "¿Cuándo es valle?"
```bash
python scripts/tarifa_periodos.py --now
```

**Usuario:** "¿Cuándo pongo el lavavajillas que dura 3 horas?"
```bash
python scripts/optimize_appliance.py --duration 3 --name lavavajillas
```

## Notas técnicas

- **Fuente de datos:** API pública de ESIOS (Red Eléctrica de España)
- **Tarifa:** PVPC 2.0TD (usuarios domésticos con potencia <10 kW)
- **Actualización:** Los precios se publican diariamente alrededor de las 20:00 para el día siguiente
- **Precios:** Incluyen todos los términos (energía, peajes, cargos) en €/kWh
- **Sin autenticación:** Usa endpoint público, no requiere token

## Limitaciones

- Los datos históricos no se almacenan localmente (cada consulta es fresh)
- La clasificación ALTO/MEDIO/BAJO es relativa al día actual, no a históricos
- Los festivos nacionales no se detectan automáticamente (se tratan como días laborables)
- Requiere conectividad a internet para consultar la API
