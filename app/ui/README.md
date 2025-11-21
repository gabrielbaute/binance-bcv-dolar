# UI Frontend

This folder contains the frontend user interface for the P2P Exchange Rate API.

## Structure

```
ui/
├── index.html              # Main HTML file
├── static/
│   ├── css/
│   │   └── styles.css      # Main stylesheet with responsive design
│   ├── js/
│   │   ├── app.js          # Main JavaScript application
│   │   └── sw.js           # Service Worker for PWA functionality
│   ├── assets/
│   │   └── README.md       # Assets folder for images, icons, etc.
│   └── manifest.json       # PWA manifest file
```

## Features

- **Real-time data**: Displays current exchange rates from Binance P2P and BCV
- **Historical charts**: Interactive charts showing rate history using Chart.js
- **Responsive design**: Optimized for desktop and mobile devices
- **Auto-refresh**: Automatically updates data every 30 seconds
- **Data export**: Export historical data to CSV format
- **PWA support**: Can be installed as a Progressive Web App

## API Endpoints Used

- `/binance/realtime_ves` - Binance P2P USDT/VES rate
- `/bcv/dolar` - BCV USD/VES rate
- `/dolar/venezuela` - Average rate calculation
- `/history/bcv` - BCV historical data
- `/history/binance` - Binance historical data

## Technologies

- **HTML5** with semantic markup
- **CSS3** with flexbox and grid layouts
- **Vanilla JavaScript** (ES6+) with async/await
- **Chart.js** for data visualization
- **Font Awesome** for icons
- **Service Worker** for PWA capabilities

## Usage

The frontend is automatically served when you run the FastAPI application. Navigate to the root URL (`/`) to access the dashboard.

## Customization

- Modify `styles.css` to change the appearance
- Update `app.js` to add new features or modify API calls
- Add images and icons to the `assets/` folder
- Customize the PWA manifest in `manifest.json`