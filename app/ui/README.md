# UI Frontend

This folder contains the frontend user interface for the P2P Exchange Rate API with advanced tab navigation and calculator functionality.

## Structure

```
ui/
├── index.html              # Main HTML file with tab navigation
├── static/
│   ├── css/
│   │   └── styles.css      # Main stylesheet with responsive design and tab/calculator styles
│   ├── js/
│   │   ├── app.js          # Main JavaScript application with tab and calculator functionality
│   │   └── sw.js           # Service Worker for PWA functionality
│   ├── assets/
│   │   └── README.md       # Assets folder for images, icons, etc.
│   └── manifest.json       # PWA manifest file
```

## New Features Added

### Tab Navigation System
- **Rate History Tab**: Historical charts and data export functionality
- **Calculator Tab**: Bi-directional currency conversion tool
- **Smooth Transitions**: Animated tab switching with modern design

### Advanced Calculator
- **Bi-directional conversion**: Convert USD ↔ VES
- **Multiple rate sources**: Binance P2P, BCV Official, and Average rates
- **Real-time calculations**: Updates as you type
- **Currency toggle**: Easy switching between input currencies
- **Clear functionality**: Reset calculator with one click

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