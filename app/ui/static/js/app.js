class ExchangeRateApp {
    constructor() {
        this.chart = null;
        this.autoRefreshInterval = null;
        this.apiBaseUrl = 'http://localhost:8000';
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initChart();
        this.loadInitialData();
        this.setupAutoRefresh();
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
            document.getElementById('binance-rate').textContent = this.formatRate(data.average_price);
            document.getElementById('binance-time').textContent = this.formatTime(new Date().toISOString());
            this.updateStatus('binance-status', 'online');
        } catch (error) {
            console.error('Error loading Binance rate:', error);
            document.getElementById('binance-rate').textContent = 'Error';
            this.updateStatus('binance-status', 'error');
        }
    }

    async loadBCVRate() {
        try {
            this.updateStatus('bcv-status', 'loading');
            const response = await fetch(`${this.apiBaseUrl}/bcv/dolar`);
            
            if (!response.ok) throw new Error('Failed to fetch BCV rate');
            
            const data = await response.json();
            document.getElementById('bcv-rate').textContent = this.formatRate(data.rate);
            document.getElementById('bcv-time').textContent = this.formatTime(data.date);
            this.updateStatus('bcv-status', 'online');
        } catch (error) {
            console.error('Error loading BCV rate:', error);
            document.getElementById('bcv-rate').textContent = 'Error';
            this.updateStatus('bcv-status', 'error');
        }
    }

    async loadAverageRate() {
        try {
            this.updateStatus('average-status', 'loading');
            const response = await fetch(`${this.apiBaseUrl}/dolar/venezuela`);
            
            if (!response.ok) throw new Error('Failed to fetch average rate');
            
            const data = await response.json();
            document.getElementById('average-rate').textContent = this.formatRate(data.average_usdt_ves);
            this.updateStatus('average-status', 'online');
        } catch (error) {
            console.error('Error loading average rate:', error);
            document.getElementById('average-rate').textContent = 'Error';
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