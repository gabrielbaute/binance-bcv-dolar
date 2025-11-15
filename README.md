# BnB-BCV: Venezuelan Currency Exchange Rate Scraper

![Work in Progress](https://img.shields.io/badge/status-work%20in%20progress-yellow)

---

### ⚠️ Under Heavy Development

This project is currently in a very active development phase. APIs, schemas, and functionalities are subject to change without notice. It is not yet recommended for production use.

---

## About The Project

This project was born out of the need for reliable, open-source information regarding the Venezuelan currency exchange market, which is often plagued by speculation and non-transparent sources. Our goal is to provide developers and the general public with direct, unadulterated data from verifiable sources.

We aim to offer a clear and trustworthy alternative to privatized and often speculative currency information providers, empowering the community with tools for better financial awareness.

## Core Features

- **Central Bank of Venezuela (BCV):** Scrapes the official USD, EUR, and other currency exchange rates directly from the BCV website.
- **Binance P2P:** Queries peer-to-peer exchange rates for various currency pairs against USDT (USD Theter), providing a real-world market value.

## Getting Started

### Prerequisites

- Python 3.8+

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your_username/bnb-bcv.git
    cd bnb-bcv
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

## Usage

The core functionalities are provided as services. Here's a basic example of how to use them:

```python
import asyncio
from app.services.bcv_scrapper import BCVScraper
from app.services.binance_p2p import BinanceP2P

async def main():
    # --- Get Official BCV Rates ---
    print("Fetching data from BCV...")
    bcv_scraper = BCVScraper()
    all_rates = bcv_scraper.get_all_exchange_rates()
    if all_rates.dolar:
        print(f"Official BCV Rate (USD): {all_rates.dolar.rate:.2f} VEF")
    if all_rates.euro:
        print(f"Official BCV Rate (EUR): {all_rates.euro.rate:.2f} VEF")

    print("-" * 20)

    # --- Get Binance P2P Rate for USDT/VEF ---
    print("\nFetching data from Binance P2P...")
    binance_p2p = BinanceP2P()
    # Get the buy rate for USDT with VEF
    usdt_ves_pair = binance_p2p.get_pair(fiat="VES", asset="USDT", trade_type="BUY", rows=10)
    
    if usdt_ves_pair and usdt_ves_pair.prices:
        print(f"Binance P2P (USDT/VEF) Average Price: {usdt_ves_pair.average_price:.2f} VEF")
        print(f"Binance P2P (USDT/VEF) Median Price: {usdt_ves_pair.median_price:.2f} VEF")

if __name__ == "__main__":
    # Note: The BinanceP2P service uses `requests` which is synchronous.
    # For this example, we run the main function directly.
    # If you integrate this into an async application, ensure to handle blocking calls appropriately.
    asyncio.run(main())
```

## Roadmap

We have a number of features and improvements planned for the future. Here's what's on our radar:

- [ ] **Database Support:** Persist historical data for trend analysis.
- [ ] **Automation:** Implement scheduled jobs to fetch data automatically.
- [ ] **Web Interface:** Create a user-friendly web GUI to display the data.
- [ ] **Telegram Bot:** A bot to query current rates on the go.
- [ ] **Historical Charts:** Generate and display charts for currency performance over time.
- [ ] **Public API:** Expose the data through a well-documented public API.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

Since the project is in its early stages, the best way to contribute right now is by opening an issue to discuss a feature you\'d like to add or a bug you\'ve found.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

This project is not yet licensed. An open-source license will be added as the project matures.
