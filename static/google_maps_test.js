// Comprehensive Google Maps API Test Script
console.log('🗺️ Testing Complete Google Maps Integration');

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Page loaded, starting comprehensive Google Maps tests...');
    
    // Wait for both page and Google Maps API to load
    setTimeout(() => {
        runGoogleMapsTests();
    }, 3000);
});

function runGoogleMapsTests() {
    console.log('🧪 Running Google Maps Integration Tests...');
    
    // Test 1: Google Maps API Status
    if (window.google && window.google.maps) {
        console.log('✅ Google Maps API loaded successfully!');
        console.log('🔑 API Key: AIzaSyAoW0TB8i9Gfjfly1EJf8Kr1FFTPuORYnE');
    } else {
        console.log('❌ Google Maps API not loaded');
        return;
    }
    
    // Test 2: Check AdvancedPlaygroundForm methods
    if (window.playgroundForm) {
        console.log('🧪 Testing AdvancedPlaygroundForm map methods...');
        
        const methods = [
            'getCurrentLocation',
            'generateMapsLink', 
            'generateDirectionLink',
            'previewLocation',
            'updateMapFromAddress'
        ];
        
        methods.forEach(method => {
            if (typeof window.playgroundForm[method] === 'function') {
                console.log(`✅ Method ${method} exists and is callable`);
            } else {
                console.log(`❌ Method ${method} missing or not a function`);
            }
        });
    } else {
        console.log('❌ playgroundForm not available');
    }
    
    // Test 3: DOM Elements Check
    const elements = [
        { id: 'get-current-location', name: 'Get Current Location Button' },
        { id: 'generate-maps-link', name: 'Generate Maps Link Button' },
        { id: 'generate-direction-link', name: 'Generate Direction Link Button' },
        { id: 'preview-location', name: 'Preview Location Button' },
        { id: 'google-map', name: 'Main Map Container' },
        { id: 'map-loading', name: 'Map Loading Indicator' },
        { id: 'google_maps_link', name: 'Maps Link Input Field' },
        { id: 'address', name: 'Address Field' },
        { id: 'location-map-preview', name: 'Location Map Preview' }
    ];
    
    elements.forEach(el => {
        const element = document.getElementById(el.id);
        if (element) {
            console.log(`✅ ${el.name} found in DOM`);
            
            // Check if buttons have click handlers
            if (el.id.includes('button') || el.id.includes('get-') || el.id.includes('generate') || el.id.includes('preview')) {
                if (element.onclick) {
                    console.log(`✅ ${el.name} has click handler`);
                } else {
                    console.log(`⚠️ ${el.name} missing click handler`);
                }
            }
        } else {
            console.log(`❌ ${el.name} not found in DOM`);
        }
    });
    
    // Test 4: Address Field Integration
    const addressField = document.getElementById('address');
    if (addressField && addressField.value) {
        console.log(`📍 Current address: "${addressField.value}"`);
        console.log('🔄 Testing automatic map update...');
        if (window.playgroundForm && typeof window.playgroundForm.updateMapFromAddress === 'function') {
            window.playgroundForm.updateMapFromAddress();
        }
    }
    
    // Test 5: Map Container Status
    const mapContainer = document.getElementById('google-map');
    const mapLoading = document.getElementById('map-loading');
    
    if (mapContainer) {
        console.log('🗺️ Map container status:');
        console.log(`   - Container exists: ✅`);
        console.log(`   - Container visible: ${mapContainer.style.display !== 'none' ? '✅' : '❌'}`);
        console.log(`   - Container size: ${mapContainer.offsetWidth}x${mapContainer.offsetHeight}`);
    }
    
    if (mapLoading) {
        console.log(`🔄 Loading indicator visible: ${mapLoading.style.display !== 'none' ? '✅' : '❌'}`);
    }
    
    console.log('\n📝 Manual Test Functions Available:');
    console.log('   - testCurrentLocation() - Test geolocation');
    console.log('   - testMapsGeneration() - Test maps link generation');
    console.log('   - testDirections() - Test direction links');
    console.log('   - testMapUpdate() - Test automatic map update');
    console.log('   - fillTestAddress() - Fill test address and update map');
}

// Manual Test Functions
window.testCurrentLocation = function() {
    console.log('🧪 Testing getCurrentLocation...');
    if (window.playgroundForm && typeof window.playgroundForm.getCurrentLocation === 'function') {
        window.playgroundForm.getCurrentLocation();
    } else {
        console.log('❌ getCurrentLocation method not available');
    }
};

window.testMapsGeneration = function() {
    console.log('🧪 Testing generateMapsLink and previewLocation...');
    if (window.playgroundForm) {
        if (typeof window.playgroundForm.generateMapsLink === 'function') {
            window.playgroundForm.generateMapsLink();
        }
        
        setTimeout(() => {
            if (typeof window.playgroundForm.previewLocation === 'function') {
                window.playgroundForm.previewLocation();
            }
        }, 1000);
    } else {
        console.log('❌ playgroundForm not available');
    }
};

window.testDirections = function() {
    console.log('🧪 Testing generateDirectionLink...');
    if (window.playgroundForm && typeof window.playgroundForm.generateDirectionLink === 'function') {
        window.playgroundForm.generateDirectionLink();
    } else {
        console.log('❌ generateDirectionLink method not available');
    }
};

window.testMapUpdate = function() {
    console.log('🧪 Testing updateMapFromAddress...');
    if (window.playgroundForm && typeof window.playgroundForm.updateMapFromAddress === 'function') {
        window.playgroundForm.updateMapFromAddress();
    } else {
        console.log('❌ updateMapFromAddress method not available');
    }
};

window.fillTestAddress = function() {
    console.log('🧪 Filling test address and updating map...');
    const addressField = document.getElementById('address');
    if (addressField) {
        addressField.value = '1600 Amphitheatre Parkway, Mountain View, CA, USA';
        addressField.dispatchEvent(new Event('input'));
        
        setTimeout(() => {
            if (window.playgroundForm && typeof window.playgroundForm.updateMapFromAddress === 'function') {
                window.playgroundForm.updateMapFromAddress();
            }
        }, 500);
    } else {
        console.log('❌ Address field not found');
    }
};

console.log('🗺️ Comprehensive Google Maps Test Script Loaded');
console.log('🚀 Tests will run automatically in 3 seconds...');
