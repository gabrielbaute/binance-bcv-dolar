# BnB-BCV: API Abierta para Tasas de Cambio en Venezuela

Version: 0.1.5

![Estado](https://img.shields.io/badge/status-en%20desarrollo-yellow)
![Licencia](https://img.shields.io/badge/license-GPLv3-blue)

## 📌 Acerca del Proyecto

BnB-BCV nace de la necesidad de contar con información **confiable y abierta** sobre el mercado cambiario venezolano, un espacio frecuentemente afectado por especulación y fuentes poco transparentes.  

Nuestro objetivo es ofrecer a desarrolladores, investigadores y al público en general datos directos y verificables, sin manipulación, para fomentar una mayor conciencia financiera.

### 🙏🏾 Reconocimientos

Debemos agradecer al usuario @DevOpsLP, quien publicó primero un script en .gs que sirvió de base para construir el proyecto, pueden consultar su repositorio aquí: https://github.com/DevOpsLP/bcv-binance-google-sheet/tree/main (y si pueden, denle estrellita, se la merece). De no ser por haberme topado con un post suyo en reddit, no habría pensado que era posible usar la API de Binance para obtener el precio del P2P.

---

## 🚀 Funcionalidades Principales

- **Banco Central de Venezuela (BCV):** Obtiene las tasas oficiales de USD, EUR y otras monedas directamente desde el portal del BCV.  
- **Binance P2P:** Consulta las tasas de intercambio peer-to-peer contra USDT, reflejando el valor real de mercado.  
- **API REST con FastAPI:** Documentada automáticamente en `/docs` con OpenAPI/Swagger.  
- **SQLite + Docker:** Persistencia ligera y despliegue reproducible en contenedores.  
- **Healthcheck:** Endpoint `/health` para monitoreo y despliegues en producción.  

---

## 🛠️ Instalación y Uso

### Prerrequisitos
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Administrador de paquetes y entornos de Python)
- Docker y Docker Compose (para despliegue recomendado)

### Instalación local

1. Clonar el repositorio:
   ```sh
   git clone [https://github.com/gabrielbaute/binance-bcv-dolar.git](https://github.com/gabrielbaute/binance-bcv-dolar.git)
   cd binance-bcv-dolar
   ```

2. Inicializar el entorno e instalar dependencias:
`uv` leerá los archivos `pyproject.toml` y `uv.lock` para crear un entorno virtual (`.venv`) e instalar todo lo necesario en un solo paso:

   ```sh
   uv sync
   ```

3. Ejecutar la API:
Puedes levantar el servidor de desarrollo directamente utilizando `uv run`, lo cual asegura que se ejecute dentro del contexto del entorno virtual correcto sin necesidad de activarlo manualmente:
   ```sh
   uv run uvicorn app.main:app --reload
   ```

   O alternativamente:
   ```sh
   uv run app/main.py
   ```

### Despliegue con Docker (recomendado)
1. Desplegar con docker-compose:
Puedes emplear el archivo de ejemplo de docker compose que tenemos en el repo, también puedes copiar y pegar:
   ```yml
   services:
      dolar_vzl:
         container_name: dolar_vzl
         image: ghcr.io/gabrielbaute/binance-bcv-dolar:latest
         restart: unless-stopped
         ports:
            - "${API_PORT:-8000}:8000"
         environment:
            - API_PORT=${API_PORT:-8000}
            - API_HOST=${API_HOST:-0.0.0.0}
            - NTFY_URL=${NTFY_URL:-}
            - NTFY_TOPIC=${NTFY_TOPIC:-}
            - BINANCE_EXTRA_FIATS=${BINANCE_EXTRA_FIATS:-}
            - BINANCE_EXTRA_CRON=${BINANCE_EXTRA_CRON:-}
            - BINANCE_VES_CRON=${BINANCE_VES_CRON:-}
            - BCV_CRON=${BCV_CRON:-}
         volumes:
            - ./instance:/instance
            - ./logs:/logs
         healthcheck:
            test: ["CMD", "curl", "-f", "http://localhost:${API_PORT:-8000}/health"]
            interval: 30s
            timeout: 10s
            retries: 3
            start_period: 60s
   ```
   Esto te dará los valores por defecto.

2. Construir y levantar servicios: Si prefieres hacer el build por tu cuenta, usa el docker-compose disponible en el repositorio
   ```sh
   docker compose up -d --build
   ```

3. Acceder a la documentación interactiva:
   ```
   http://localhost:8000/docs
   ```
   No olviden darle permisos al usuario de docker para poder escribir en los directorios de la app. Pueden hacerlo así:
   ```sh
   sudo chown -R 1000:1000 ./logs ./instance
   ```
4. Acceder a la interfaz gráfica.
   La interfaz gráfica está disponible en la raíz del proyecto:
   ```
   http://localhost:8000/
   ```
---

### Variables de Entorno

El proyecto se configura mediante las siguientes variables de entorno. Puedes crear un archivo `.env` en la raíz del proyecto basándote en esta tabla:

| Variable | Tipo | Por Defecto | Descripción |
| --- | --- | --- | --- |
| **`LOG_LEVEL`** | Cadena (`str`) | `INFO` | Nivel de severidad para el rastreo del sistema (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). |
| **`API_PORT`** | Entero (`int`) | `8000` | Puerto en el que se expondrá la API de la aplicación. |
| **`API_HOST`** | Cadena (`str`) | `0.0.0.0` | Dirección de host para la escucha del servidor de la API. |
| **`NTFY_URL`** | Cadena (`str`) | *Obligatorio* | URL del servidor de notificaciones basado en NTFY para el envío de alertas y reportes. |
| **`NTFY_TOPIC`** | Cadena (`str`) | *Obligatorio* | Tópico específico de NTFY donde se suscribirán los clientes para recibir las alertas. |
| **`BINANCE_EXTRA_FIATS`** | Cadena (`str`) | `PEN,ARS` | Lista de monedas locales (fiat) adicionales a procesar, separadas estrictamente por comas. |
| **`BINANCE_EXTRA_CRON`** | Cadena (`str`) | `0 */3 * * *` | Expresión Cron que define la frecuencia de actualización para las monedas fiat extra (ej: cada 3 horas). |
| **`BINANCE_VES_CRON`** | Cadena (`str`) | `*/30 * * * *` | Expresión Cron que define la frecuencia para el par nativo principal (ej: cada 30 minutos todos los días). |
| **`BCV_CRON`** | Cadena (`str`) | `0 0 * * *` | Expresión Cron que define cuándo se ejecuta el recolector del BCV (ej: todos los días a la medianoche). |

---
## 📊 Ejemplo de Uso

```python
from app.services.bcv_scrapper import BCVScraper
from app.services.binance_p2p import BinanceP2P

# Obtener tasas oficiales del BCV
bcv_scraper = BCVScraper()
rates = bcv_scraper.get_all_exchange_rates()
print(f"Tasa oficial USD: {rates.dolar.rate:.2f} VES")

# Obtener tasas P2P de Binance
binance_p2p = BinanceP2P()
pair = binance_p2p.get_pair(fiat="VES", asset="USDT", trade_type="BUY", rows=10)
print(f"Precio promedio USDT/VES: {pair.average_price:.2f}")
```

---

## 📅 Roadmap

- [x] Persistencia histórica para análisis de tendencias  
- [x] Automatización con jobs programados  
- [x] Interfaz web amigable  
- [ ] Bot de Telegram para consultas rápidas  
- [x] Gráficas históricas de desempeño  
- [x] API pública estable y documentada  (casi)
- [x] Deploy en docker

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Puedes:  
1. Hacer un fork del proyecto  
2. Crear tu rama de feature (`git checkout -b feature/NuevaFeature`)  
3. Commit de tus cambios (`git commit -m 'Agrega nueva feature'`)  
4. Push a tu rama (`git push origin feature/NuevaFeature`)  
5. Abrir un Pull Request  

También puedes abrir un **issue** para reportar errores o proponer mejoras.

---

## 📜 Licencia

Este proyecto está licenciado bajo la **GNU General Public License v3.0 (GPLv3)**.  
Esto significa que:  
- Puedes usarlo y modificarlo libremente, incluso con fines comerciales.  
- Cualquier distribución derivada debe mantenerse bajo licencia GPLv3.  
- Se garantiza que el código permanezca abierto y accesible para la comunidad.  

Consulta el archivo [LICENSE](LICENSE) para más detalles.