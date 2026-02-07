// Test script to verify dynamic statistics functionality
console.log('🧪 Testing Dynamic Statistics System');

// Wait for page to load
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Page loaded, starting tests...');
    
    // Test 1: Check if statistics show 0 initially (no slots generated)
    setTimeout(() => {
        const totalSlotsElement = document.querySelector('[data-stat="total-slots"]');
        const revenueElement = document.querySelector('[data-stat="revenue"]');
        
        if (totalSlotsElement) {
            console.log('📊 Initial Total Slots:', totalSlotsElement.textContent);
        }
        
        if (revenueElement) {
            console.log('💰 Initial Revenue:', revenueElement.textContent);
        }
        
        // Test 2: Simulate slot generation
        if (window.playgroundForm && typeof window.playgroundForm.updateDynamicStatistics === 'function') {
            console.log('🔄 Testing dynamic statistics update...');
            window.playgroundForm.updateDynamicStatistics();
            
            setTimeout(() => {
                console.log('📊 After update - Total Slots:', totalSlotsElement?.textContent);
                console.log('💰 After update - Revenue:', revenueElement?.textContent);
            }, 1000);
        }
        
        // Test 3: Check Google Maps API
        if (window.google && window.google.maps) {
            console.log('🗺️ Google Maps API loaded successfully!');
        } else {
            console.log('❌ Google Maps API not loaded');
        }
        
        // Test 4: Currency API test
        if (window.playgroundForm && typeof window.playgroundForm.fetchCurrencyFromBackend === 'function') {
            console.log('💱 Testing currency detection...');
            window.playgroundForm.fetchCurrencyFromBackend().then(currency => {
                console.log('💱 Detected currency:', currency);
            }).catch(err => {
                console.log('❌ Currency detection failed:', err);
            });
        }
        
    }, 2000);
});

// Helper function to test notification system
function testNotifications() {
    if (window.playgroundForm && typeof window.playgroundForm.showNotification === 'function') {
        console.log('🔔 Testing notification system...');
        window.playgroundForm.showNotification('✅ Test notification - Statistics are now purely dynamic!', 'success');
    }
}

// Expose test function globally
window.testDynamicStats = testNotifications;

console.log('🧪 Dynamic Statistics Test Script Loaded');
console.log('📝 Run testDynamicStats() in console to test notifications');
