# UI del dashboard

La interfaz se sirve desde `/` mediante FastAPI. El front está implementado con Svelte 5 y TanStack Charts 1.1.0. Los estilos editables están en `app/ui/src/app.css`; Vite genera `app/ui/static/js/app.js` y `app/ui/static/css/app.css`.

## Vistas

- **Resumen:** BCV USD/VES, Binance P2P USDT/VES y tasa de referencia actuales en una gráfica de barras. La brecha actual compara Binance con BCV.
- **Histórico:** líneas y puntos de BCV y Binance. El rango de 24 h usa intervalos horarios UTC; los demás usan días UTC. Se muestra la última observación válida de cada fuente dentro de cada intervalo, sin rellenar huecos. Un rango con una sola observación también muestra su punto.
- **Brecha:** diferencia Binance − BCV en bolívares y porcentaje relativo al BCV. En rangos diarios solo se comparan días con valores de ambas fuentes. En 24 h, cada observación horaria de Binance usa la tasa BCV guardada más reciente antes de ella, con un máximo de 72 h de antigüedad. La vista indica la fecha de la tasa BCV usada para el último punto; no se presenta como una nueva observación BCV.
- **Calculadora:** conversión USD ↔ VES con cada tasa disponible. Una tasa ausente se muestra como no disponible.

Los rangos rápidos son 24 h, 7, 30 y 90 días y año en curso. Cada selección actualiza los campos **Desde** y **Hasta**. Al elegir un año, los campos se sitúan en el inicio y fin de ese año y el calendario queda limitado a él; puedes ajustar, por ejemplo, marzo a junio de 2025 y pulsar **Aplicar fechas**. **Cualquier año** quita ese límite para elegir fechas de años distintos. Las fechas son inclusivas y se interpretan en UTC. La lista de años se obtiene de las fechas extremas guardadas para BCV y Binance; no aparecen años si la base está vacía. Histórico y Brecha comparten la selección mientras cambias de tab. La selección inicial es **7 días** porque una ventana de 24 h puede no contener una observación BCV comparable, incluso si Binance tiene datos recientes. Para los años anteriores al inicio del registro Binance, Histórico muestra BCV sin inventar valores; Brecha indica que no hay registros Binance para calcularla. El CSV del histórico exporta el rango seleccionado con celdas vacías cuando falta una observación. La navegación admite teclado y enlaces con `?tab=summary|history|spread|calculator`; el acceso directo PWA de calculadora sigue usando `?tab=calculator`.

El rango **24 h** es móvil y se cuenta desde la hora actual en UTC. Si no hay registros dentro de esa ventana, Histórico y Brecha muestran la fecha de los últimos registros guardados y ofrecen abrir 7 días. Esto permite distinguir una base con datos antiguos de una base sin registros.

El límite superior del calendario se actualiza al cambiar el día UTC. **Actualizar tasas** también vuelve a consultar los años disponibles y sincroniza los rangos rápidos con la fecha actual, sin sobrescribir fechas personalizadas pendientes de aplicar. Si falla la consulta de años, aparece **Reintentar**; una base vacía muestra **Sin años**.

## Datos

La UI consume las rutas existentes `/api/v1/binance/realtime_ves`, `/api/v1/bcv/realtime` (con respaldo en `/api/v1/bcv/dolar`), `/api/v1/dolar/realtime_dolar_promedio` (con respaldo en `/api/v1/dolar/dolar_promedio`), `/api/v1/history/bcv` y `/api/v1/history/binance`. La paginación histórica carga todas las páginas dentro del límite configurado por el cliente. No se agregan endpoints ni se mezclan fiats con unidades distintas.

## Desarrollo

Desde la raíz del repositorio:

```sh
npm ci
npm run build:ui
npm run build:ui:dev
npm run check:ui
npm run test:ui
```

`npm run build:ui:dev` recompila al modificar fuentes. Ejecuta FastAPI con `uv run uvicorn app.main:app --reload` después de crear el bundle. La imagen Docker usa Node 22 para construir los assets con `npm ci`. Si cambias estilos o la plantilla, verifica también la vista móvil y actualiza el cache del service worker cuando cambien las rutas de assets.
