// Global variables
let priceChart = null;
let priceData = [];
const maxDataPoints = 100;

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', () => {
    initializeChart();
    setupEventListeners();
    updateStatus();
    // Poll status every second
    setInterval(updateStatus, 1000);
});

// Initialize price chart
function initializeChart() {
    const ctx = document.getElementById('priceChart').getContext('2d');
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Price',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false
                }
            },
            animation: {
                duration: 0
            }
        }
    });
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('startButton').addEventListener('click', startBot);
    document.getElementById('stopButton').addEventListener('click', stopBot);
}

// Update chart with new price data
function updateChart(price) {
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    
    priceChart.data.labels.push(timeStr);
    priceChart.data.datasets[0].data.push(price);
    
    // Keep only last N data points
    if (priceChart.data.labels.length > maxDataPoints) {
        priceChart.data.labels.shift();
        priceChart.data.datasets[0].data.shift();
    }
    
    priceChart.update('none'); // Update without animation
}

// Update dashboard status
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        // Update status badges
        document.getElementById('botMode').textContent = data.mode.toUpperCase();
        document.getElementById('botStatus').textContent = data.status.toUpperCase();
        
        // Update status badge colors
        const statusBadge = document.getElementById('botStatus');
        statusBadge.className = data.status === 'running' 
            ? 'ml-2 px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800'
            : 'ml-2 px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800';
        
        // Update balance and positions
        document.getElementById('balance').textContent = formatCurrency(data.balances.USDT);
        document.getElementById('openPositions').textContent = data.positions.length;
        
        // Update PnL
        const pnl = data.total_pnl || 0;
        const pnlElement = document.getElementById('pnl');
        pnlElement.textContent = formatCurrency(pnl);
        pnlElement.className = `text-2xl font-semibold ${pnl >= 0 ? 'text-green-600' : 'text-red-600'}`;
        
        // Update price chart if we have positions
        if (data.positions.length > 0) {
            const lastPosition = data.positions[0];
            updateChart(lastPosition.current_price);
        }
        
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

// Start the trading bot
async function startBot() {
    try {
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        if (result.status === 'success') {
            console.log('Bot started successfully');
        } else {
            console.error('Failed to start bot:', result.message);
        }
        
    } catch (error) {
        console.error('Error starting bot:', error);
    }
}

// Stop the trading bot
async function stopBot() {
    try {
        const response = await fetch('/api/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        if (result.status === 'success') {
            console.log('Bot stopped successfully');
        } else {
            console.error('Failed to stop bot:', result.message);
        }
        
    } catch (error) {
        console.error('Error stopping bot:', error);
    }
}

// Format currency values
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}
