class ExchangeRateApp {
    constructor() {
        this.chart = null;
        this.autoRefreshInterval = null;
        this.apiBaseUrl = '/api';
        this.currentRates = {
            binance: 0,
            bcv: 0,
            average: 0
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initChart();
        this.loadInitialData();
        this.setupAutoRefresh();
        this.initTabs();
        this.initCalculator();
    }

    setupEventListeners() {
        // Refresh data button
        document.getElementById('refresh-data').addEventListener('click', () => {
            this.refreshAllData();
        });

        // Export data button
        document.getElementById('export-data').addEventListener('click', () => {
            this.exportData();
        });

        // Auto refresh toggle
        document.getElementById('auto-refresh-toggle').addEventListener('change', (e) => {
            if (e.target.checked) {
                this.setupAutoRefresh();
            } else {
                this.clearAutoRefresh();
            }
        });

        // Time range selector
        document.getElementById('time-range').addEventListener('change', (e) => {
            this.updateChart(e.target.value);
        });

        // Refresh chart button
        document.getElementById('refresh-chart').addEventListener('click', () => {
            const timeRange = document.getElementById('time-range').value;
            this.updateChart(timeRange);
        });

        // Tab navigation
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                this.switchTab(e.target.closest('.tab-button').dataset.tab);
            });
        });

        // Calculator events
        document.getElementById('toggle-usd').addEventListener('click', () => {
            this.setCurrencyMode('USD');
        });

        document.getElementById('toggle-ves').addEventListener('click', () => {
            this.setCurrencyMode('VES');
        });

        document.getElementById('amount-input').addEventListener('input', (e) => {
            this.calculateConversion();
        });

        // document.getElementById('calculate-btn').addEventListener('click', () => {
        //     this.calculateConversion();
        // });

        document.getElementById('clear-calc').addEventListener('click', () => {
            this.clearCalculator();
        });
    }

    async loadInitialData() {
        try {
            await Promise.all([
                this.loadBinanceRate(),
                this.loadBCVRate(),
                this.loadAverageRate(),
                this.updateChart('24h')
            ]);
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showNotification('Error loading initial data', 'error');
        }
    }

    async loadBinanceRate() {
        try {
            this.updateStatus('binance-status', 'loading');
            const response = await fetch(`${this.apiBaseUrl}/binance/realtime_ves`);
            
            if (!response.ok) throw new Error('Failed to fetch Binance rate');
            
            const data = await response.json();
            this.currentRates.binance = parseFloat(data.average_price);
            document.getElementById('binance-rate').textContent = this.formatRate(data.average_price);
            document.getElementById('binance-time').textContent = this.formatTime(new Date().toISOString());
            document.getElementById('binance-rate-calc').textContent = this.formatRate(data.average_price);
            this.updateStatus('binance-status', 'online');
        } catch (error) {
            console.error('Error loading Binance rate:', error);
            document.getElementById('binance-rate').textContent = 'Error';
            document.getElementById('binance-rate-calc').textContent = 'Error';
            this.updateStatus('binance-status', 'error');
        }
    }

    async loadBCVRate() {
        try {
            this.updateStatus('bcv-status', 'loading');
            const response = await fetch(`${this.apiBaseUrl}/bcv/dolar`);
            
            if (!response.ok) throw new Error('Failed to fetch BCV rate');
            
            const data = await response.json();
            this.currentRates.bcv = parseFloat(data.rate);
            document.getElementById('bcv-rate').textContent = this.formatRate(data.rate);
            document.getElementById('bcv-time').textContent = this.formatTime(data.date);
            document.getElementById('bcv-rate-calc').textContent = this.formatRate(data.rate);
            this.updateStatus('bcv-status', 'online');
        } catch (error) {
            console.error('Error loading BCV rate:', error);
            document.getElementById('bcv-rate').textContent = 'Error';
            document.getElementById('bcv-rate-calc').textContent = 'Error';
            this.updateStatus('bcv-status', 'error');
        }
    }

    async loadAverageRate() {
        try {
            this.updateStatus('average-status', 'loading');
            const response = await fetch(`${this.apiBaseUrl}/dolar/venezuela`);
            
            if (!response.ok) throw new Error('Failed to fetch average rate');
            
            const data = await response.json();
            this.currentRates.average = parseFloat(data.average_usdt_ves);
            document.getElementById('average-rate').textContent = this.formatRate(data.average_usdt_ves);
            document.getElementById('average-rate-calc').textContent = this.formatRate(data.average_usdt_ves);
            this.updateStatus('average-status', 'online');
        } catch (error) {
            console.error('Error loading average rate:', error);
            document.getElementById('average-rate').textContent = 'Error';
            document.getElementById('average-rate-calc').textContent = 'Error';
            this.updateStatus('average-status', 'error');
        }
    }

    async refreshAllData() {
        this.showNotification('Refreshing data...', 'info');
        await this.loadInitialData();
        this.showNotification('Data refreshed successfully!', 'success');
    }

    initChart() {
        const ctx = document.getElementById('rateChart').getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Binance P2P',
                        data: [],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 2,
                        fill: true
                    },
                    {
                        label: 'BCV Rate',
                        data: [],
                        borderColor: '#f093fb',
                        backgroundColor: 'rgba(240, 147, 251, 0.1)',
                        borderWidth: 2,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Exchange Rate History'
                    },
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Rate (VES)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    async updateChart(timeRange = '24h') {
        try {
            // Calculate date range based on selection
            const endDate = new Date();
            const startDate = new Date();
            
            switch(timeRange) {
                case '24h':
                    startDate.setHours(startDate.getHours() - 24);
                    break;
                case '7d':
                    startDate.setDate(startDate.getDate() - 7);
                    break;
                case '30d':
                    startDate.setDate(startDate.getDate() - 30);
                    break;
            }

            const startDateStr = startDate.toISOString().split('T')[0];
            const endDateStr = endDate.toISOString().split('T')[0];

            // Fetch both history data in parallel
            const [bcvResponse, binanceResponse] = await Promise.all([
                fetch(`${this.apiBaseUrl}/history/bcv?start_date=${startDateStr}&end_date=${endDateStr}&currency=USD`),
                fetch(`${this.apiBaseUrl}/history/binance?start_date=${startDateStr}&end_date=${endDateStr}&fiat=VES&asset=USDT&trade_type=BUY`)
            ]);
            
            if (!bcvResponse.ok || !binanceResponse.ok) {
                throw new Error('Failed to fetch history data');
            }
            
            const bcvData = await bcvResponse.json();
            const binanceData = await binanceResponse.json();
            
            // Process data for chart
            const allDates = new Set();
            
            // Collect all unique dates
            if (bcvData.data) {
                bcvData.data.forEach(item => {
                    if (item.created_at) allDates.add(item.created_at.split('T')[0]);
                });
            }
            
            if (binanceData.data) {
                binanceData.data.forEach(item => {
                    if (item.created_at) allDates.add(item.created_at.split('T')[0]);
                });
            }

            const sortedDates = Array.from(allDates).sort();
            const labels = sortedDates.map(date => this.formatChartDate(date));
            
            // Create data arrays with matching dates
            const bcvPrices = sortedDates.map(date => {
                const item = bcvData.data?.find(d => d.created_at?.startsWith(date));
                return item ? parseFloat(item.price) : null;
            });
            
            const binancePrices = sortedDates.map(date => {
                const item = binanceData.data?.find(d => d.created_at?.startsWith(date));
                return item ? parseFloat(item.average_price) : null;
            });

            this.chart.data.labels = labels;
            this.chart.data.datasets[0].data = binancePrices;
            this.chart.data.datasets[1].data = bcvPrices;
            this.chart.update();

        } catch (error) {
            console.error('Error updating chart:', error);
            this.showNotification('Error updating chart', 'error');
        }
    }

    async exportData() {
        try {
            // Get both BCV and Binance history data
            const endDate = new Date();
            const startDate = new Date();
            startDate.setDate(startDate.getDate() - 30); // Last 30 days
            
            const startDateStr = startDate.toISOString().split('T')[0];
            const endDateStr = endDate.toISOString().split('T')[0];

            const [bcvResponse, binanceResponse] = await Promise.all([
                fetch(`${this.apiBaseUrl}/history/bcv?start_date=${startDateStr}&end_date=${endDateStr}&currency=USD`),
                fetch(`${this.apiBaseUrl}/history/binance?start_date=${startDateStr}&end_date=${endDateStr}&fiat=VES&asset=USDT&trade_type=BUY`)
            ]);
            
            if (!bcvResponse.ok || !binanceResponse.ok) {
                throw new Error('Failed to export data');
            }
            
            const bcvData = await bcvResponse.json();
            const binanceData = await binanceResponse.json();
            
            // Create CSV content
            let csvContent = "Date,BCV_Rate,Binance_Rate\n";
            
            // Combine and process data
            const allDates = new Set();
            if (bcvData.data) bcvData.data.forEach(item => allDates.add(item.created_at?.split('T')[0]));
            if (binanceData.data) binanceData.data.forEach(item => allDates.add(item.created_at?.split('T')[0]));
            
            const sortedDates = Array.from(allDates).sort();
            
            sortedDates.forEach(date => {
                const bcvItem = bcvData.data?.find(d => d.created_at?.startsWith(date));
                const binanceItem = binanceData.data?.find(d => d.created_at?.startsWith(date));
                
                const bcvPrice = bcvItem ? bcvItem.price : '';
                const binancePrice = binanceItem ? binanceItem.average_price : '';
                
                csvContent += `${date},${bcvPrice},${binancePrice}\n`;
            });
            
            const blob = new Blob([csvContent], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `exchange_rates_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            this.showNotification('Data exported successfully!', 'success');
        } catch (error) {
            console.error('Error exporting data:', error);
            this.showNotification('Error exporting data', 'error');
        }
    }

    setupAutoRefresh() {
        this.clearAutoRefresh();
        this.autoRefreshInterval = setInterval(() => {
            this.loadBinanceRate();
            this.loadBCVRate();
            this.loadAverageRate();
        }, 30000); // 30 seconds
    }

    clearAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }

    updateStatus(elementId, status) {
        const element = document.getElementById(elementId);
        element.className = `status-indicator ${status}`;
        
        switch (status) {
            case 'online':
                element.textContent = 'Online';
                break;
            case 'loading':
                element.innerHTML = '<span class="spinner"></span> Loading';
                break;
            case 'error':
                element.textContent = 'Error';
                break;
            default:
                element.textContent = 'Unknown';
        }
    }

    formatRate(rate) {
        if (typeof rate !== 'number') return '--';
        return new Intl.NumberFormat('es-VE', {
            style: 'currency',
            currency: 'VES',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(rate);
    }

    formatTime(timestamp) {
        if (!timestamp) return '--';
        const date = new Date(timestamp);
        return new Intl.DateTimeFormat('es-VE', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }

    formatChartTime(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return new Intl.DateTimeFormat('es-VE', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }

    formatChartDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('es-VE', {
            month: 'short',
            day: 'numeric'
        }).format(date);
    }

    showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notification => notification.remove());

        // Create new notification
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    // Tab Management Functions
    initTabs() {
        // Show the first tab by default
        this.switchTab('history');
    }

    switchTab(tabName) {
        // Remove active class from all tabs and panes
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));

        // Add active class to selected tab and pane
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        document.getElementById(`${tabName}-tab`).classList.add('active');

        // If switching to calculator tab, refresh rates
        if (tabName === 'calculator') {
            this.updateCalculatorRates();
        }
    }

    // Calculator Functions
    initCalculator() {
        this.currentCurrency = 'USD';
        this.setCurrencyMode('USD');
    }

    setCurrencyMode(currency) {
        this.currentCurrency = currency;
        
        // Update button states
        document.querySelectorAll('.currency-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`toggle-${currency.toLowerCase()}`).classList.add('active');

        // Update input display
        if (currency === 'USD') {
            document.getElementById('input-symbol').textContent = '$';
            document.getElementById('input-currency').textContent = 'USD';
        } else {
            document.getElementById('input-symbol').textContent = 'Bs.';
            document.getElementById('input-currency').textContent = 'VES';
        }

        // Update result currencies
        this.updateResultCurrencies();
        
        // Recalculate if there's an amount
        this.calculateConversion();
    }

    updateResultCurrencies() {
        const targetCurrency = this.currentCurrency === 'USD' ? 'VES' : 'USD';
        const targetSymbol = targetCurrency === 'USD' ? '$' : 'Bs.';

        document.getElementById('binance-symbol').textContent = targetSymbol;
        document.getElementById('binance-currency').textContent = targetCurrency;
        document.getElementById('bcv-symbol').textContent = targetSymbol;
        document.getElementById('bcv-currency').textContent = targetCurrency;
        document.getElementById('average-symbol').textContent = targetSymbol;
        document.getElementById('average-currency').textContent = targetCurrency;
    }

    updateCalculatorRates() {
        // Update the displayed rates in the calculator
        document.getElementById('binance-rate-calc').textContent = this.formatRate(this.currentRates.binance);
        document.getElementById('bcv-rate-calc').textContent = this.formatRate(this.currentRates.bcv);
        document.getElementById('average-rate-calc').textContent = this.formatRate(this.currentRates.average);
    }

    calculateConversion() {
        const amount = parseFloat(document.getElementById('amount-input').value) || 0;
        
        if (amount <= 0) {
            this.clearResults();
            return;
        }

        let binanceResult, bcvResult, averageResult;

        if (this.currentCurrency === 'USD') {
            // Convert USD to VES
            binanceResult = amount * this.currentRates.binance;
            bcvResult = amount * this.currentRates.bcv;
            averageResult = amount * this.currentRates.average;
        } else {
            // Convert VES to USD
            binanceResult = amount / this.currentRates.binance;
            bcvResult = amount / this.currentRates.bcv;
            averageResult = amount / this.currentRates.average;
        }

        // Update result displays
        document.getElementById('binance-result').textContent = this.formatAmount(binanceResult);
        document.getElementById('bcv-result').textContent = this.formatAmount(bcvResult);
        document.getElementById('average-result').textContent = this.formatAmount(averageResult);
    }

    clearCalculator() {
        document.getElementById('amount-input').value = '';
        this.clearResults();
    }

    clearResults() {
        document.getElementById('binance-result').textContent = '0.00';
        document.getElementById('bcv-result').textContent = '0.00';
        document.getElementById('average-result').textContent = '0.00';
    }

    formatAmount(amount) {
        if (typeof amount !== 'number' || isNaN(amount)) return '0.00';
        return new Intl.NumberFormat('es-VE', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.exchangeRateApp = new ExchangeRateApp();
});

// Service Worker registration (for PWA capabilities)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}