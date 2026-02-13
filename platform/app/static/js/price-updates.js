/**
 * Real-time price updates via WebSocket
 */

// Connect to Socket.IO
const socket = io();

socket.on('connect', () => {
    console.log('Connected to WebSocket');
    socket.emit('join_price_updates');
});

socket.on('disconnect', () => {
    console.log('Disconnected from WebSocket');
});

socket.on('price_update', (data) => {
    console.log('Price update received:', data);
    
    // Update live price display
    const livePriceEl = document.getElementById('live-price');
    if (livePriceEl) {
        livePriceEl.textContent = `$${data.our_price.toFixed(2)}`;
        
        // Add animation
        livePriceEl.classList.add('animate-pulse');
        setTimeout(() => {
            livePriceEl.classList.remove('animate-pulse');
        }, 1000);
    }
    
    // Update savings percent
    const savingsEl = document.querySelector('.text-clout-cyan');
    if (savingsEl && data.savings_percent) {
        savingsEl.textContent = `Save ${data.savings_percent.toFixed(1)}% vs competitors`;
    }
    
    // Update price table
    updatePriceTable(data);
    
    // Update calculator
    updateCalculator();
});

function updatePriceTable(data) {
    const tableBody = document.getElementById('price-table-body');
    if (!tableBody) return;
    
    let html = '';
    
    // Add competitor rows
    for (const [competitor, price] of Object.entries(data.competitor_prices)) {
        const diff = ((price - data.our_price) / data.our_price * 100).toFixed(1);
        html += `
            <tr class="border-b border-gray-800">
                <td class="py-4 px-4">${competitor}</td>
                <td class="py-4 px-4">$${price.toFixed(2)}</td>
                <td class="py-4 px-4 text-red-400">+${diff}%</td>
            </tr>
        `;
    }
    
    // Add our row
    html += `
        <tr class="bg-clout-gold/10">
            <td class="py-4 px-4 font-bold text-clout-gold">CloutScape (Us)</td>
            <td class="py-4 px-4 font-bold text-clout-gold">$${data.our_price.toFixed(2)}</td>
            <td class="py-4 px-4 font-bold text-clout-cyan">BEST PRICE</td>
        </tr>
    `;
    
    tableBody.innerHTML = html;
}

// Fetch initial prices on page load
window.addEventListener('DOMContentLoaded', () => {
    fetch('/api/v1/prices/live')
        .then(response => response.json())
        .then(data => {
            console.log('Initial prices loaded:', data);
        })
        .catch(error => {
            console.error('Error fetching initial prices:', error);
        });
});
