---
name: jwdiario
description: Buscar y obtener el texto diario de la página oficial de los Testigos de Jehová en español (wol.jw.org/es/). Utiliza web_fetch para acceder al contenido y extraer el texto del día actual. Use cuando se solicite el texto diario de JW o contenido bíblico diario de fuentes JW.
---

# Habilidad JWDiario

Esta habilidad permite obtener el texto diario de la página oficial de los Testigos de Jehová en español (wol.jw.org/es/).

## Funcionalidad principal

La habilidad realiza lo siguiente:
1. Accede a la página de la Biblioteca en Línea de los Testigos de Jehová
2. Extrae el texto diario correspondiente a la fecha actual
3. Presenta el texto con contexto bíblico y explicación pertinente

## Uso típico

Cuando se solicita:
- "Texto diario de JW"
- "Texto de hoy de JW"
- "Buscar texto del día en JW"
- "Mostrar lectura diaria de JW"

## Flujo de trabajo

1. Usa `web_fetch` para acceder a https://wol.jw.org/es/
2. Extrae el contenido del día actual
3. Formatea el texto de manera clara y legible
4. Incluye el versículo bíblico correspondiente y su explicación

## Ejemplo de uso

```
Usuario: "Texto diario de JW por favor"
Habilidad: Obtiene el texto del día desde wol.jw.org/es/ y lo presenta con el versículo bíblico y explicación correspondiente.
```

## Recursos necesarios

- `web_fetch` para acceder al sitio web
- Capacidad de procesamiento de texto para formatear correctamente la salida