/**
 * GP Calculator functionality
 */

let currentPrice = 0;
let averageCompetitorPrice = 0;

// Fetch current prices
async function fetchPrices() {
    try {
        const response = await fetch('/api/v1/prices/live');
        const data = await response.json();
        currentPrice = data.our_price || 0;
        averageCompetitorPrice = data.average_competitor || 0;
        updateCalculator();
    } catch (error) {
        console.error('Error fetching prices:', error);
    }
}

function updateCalculator() {
    const slider = document.getElementById('gp-slider');
    if (!slider) return;
    
    const gpAmount = parseInt(slider.value);
    const gpInMillions = gpAmount;
    
    // Update amount display
    const amountEl = document.getElementById('gp-amount');
    if (amountEl) {
        if (gpInMillions >= 1000) {
            amountEl.textContent = `${(gpInMillions / 1000).toFixed(1)}B GP`;
        } else {
            amountEl.textContent = `${gpInMillions}M GP`;
        }
    }
    
    // Calculate total price
    const totalPrice = (gpInMillions * currentPrice);
    const totalPriceEl = document.getElementById('total-price');
    if (totalPriceEl) {
        totalPriceEl.textContent = `$${totalPrice.toFixed(2)}`;
    }
    
    // Calculate savings
    const competitorTotal = (gpInMillions * averageCompetitorPrice);
    const savings = competitorTotal - totalPrice;
    const savingsEl = document.getElementById('savings-amount');
    if (savingsEl) {
        savingsEl.textContent = `$${savings.toFixed(2)}`;
    }
}

// Initialize calculator
window.addEventListener('DOMContentLoaded', () => {
    const slider = document.getElementById('gp-slider');
    if (slider) {
        slider.addEventListener('input', updateCalculator);
        fetchPrices();
    }
});
