# BnB-BCV: API Abierta para Tasas de Cambio en Venezuela

Version: 0.1.5

![Estado](https://img.shields.io/badge/status-en%20desarrollo-yellow)
![Licencia](https://img.shields.io/badge/license-GPLv3-blue)

---

### ⚠️ Proyecto en Desarrollo Activo

Este proyecto se encuentra en una fase de desarrollo muy activa. Las APIs, esquemas y funcionalidades pueden cambiar sin previo aviso. Aunque ya es funcional, aún no se recomienda para entornos críticos de producción.

---

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
- Docker y Docker Compose (para despliegue recomendado)

### Instalación local

1. Clonar el repositorio:
   ```sh
   git clone https://github.com/tu_usuario/bnb-bcv.git
   cd bnb-bcv
   ```

2. Crear entorno virtual:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instalar dependencias:
   ```sh
   pip install -r requirements.txt
   ```

4. Ejecutar la API:
   ```sh
   uvicorn app.main:app --reload
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
            - INSTANCE_DIR=${INSTANCE_DIR:-/instance}
            - LOG_DIR=${LOG_DIR:-/logs}
            - NTFY_URL=${NTFY_URL:-}
            - NTFY_TOPIC=${NTFY_TOPIC:-}
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
- [ ] Gráficas históricas de desempeño  
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