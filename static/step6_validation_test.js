// Step 6 Validation Test Script
// Run this in browser console after loading the form

async function validateStep6Fixes() {
    console.log('🧪 Starting Step 6 validation test...');
    
    // Test 1: Check if sport type select element exists
    const sportTypeSelect = document.getElementById('sport_type_select');
    console.log('✅ Test 1 - Sport type select element:', sportTypeSelect ? 'FOUND' : 'NOT FOUND');
    
    if (sportTypeSelect) {
        console.log('📋 Available options:', Array.from(sportTypeSelect.options).map(opt => opt.text));
    }
    
    // Test 2: Check location elements
    const countrySelect = document.getElementById('country');
    const stateSelect = document.getElementById('state');
    const citySelect = document.getElementById('city');
    console.log('✅ Test 2 - Location elements:', {
        country: countrySelect ? 'FOUND' : 'NOT FOUND',
        state: stateSelect ? 'FOUND' : 'NOT FOUND', 
        city: citySelect ? 'FOUND' : 'NOT FOUND'
    });
    
    // Test 3: Check preview elements
    const previewLocation = document.getElementById('preview-location');
    const previewSports = document.getElementById('preview-sports');
    const previewTimeslots = document.getElementById('preview-timeslots');
    console.log('✅ Test 3 - Preview elements:', {
        location: previewLocation ? 'FOUND' : 'NOT FOUND',
        sports: previewSports ? 'FOUND' : 'NOT FOUND',
        timeslots: previewTimeslots ? 'FOUND' : 'NOT FOUND'
    });
    
    // Test 4: Check if functions exist
    console.log('✅ Test 4 - Functions availability:', {
        getSelectedSports: typeof window.playgroundForm?.getSelectedSports === 'function',
        formatLocationForPreview: typeof window.playgroundForm?.formatLocationForPreview === 'function',
        fixStep6CommonIssues: typeof window.playgroundForm?.fixStep6CommonIssues === 'function'
    });
    
    // Test 5: Quick form fill for testing
    console.log('🔧 Test 5 - Quick filling form for testing...');
    
    // Fill basic info
    const nameInput = document.getElementById('name');
    if (nameInput) nameInput.value = 'Test Playground';
    
    const descInput = document.getElementById('description');
    if (descInput) descInput.value = 'Test description for validation';
    
    const priceInput = document.getElementById('price_per_hour');
    if (priceInput) priceInput.value = '50';
    
    const capacityInput = document.getElementById('capacity');
    if (capacityInput) capacityInput.value = '20';
    
    // Select playground type
    if (sportTypeSelect && sportTypeSelect.options.length > 1) {
        sportTypeSelect.selectedIndex = 1;
        sportTypeSelect.dispatchEvent(new Event('change'));
        console.log('✅ Selected sport type:', sportTypeSelect.options[1].text);
    }
    
    // Fill location if possible
    if (countrySelect && countrySelect.options.length > 1) {
        countrySelect.selectedIndex = 1;
        countrySelect.dispatchEvent(new Event('change'));
        console.log('✅ Selected country:', countrySelect.options[1].text);
    }
    
    console.log('✅ Test completed - Check the form and navigate to Step 6 to validate fixes');
    console.log('🎯 To navigate directly to Step 6, run: navigateToStep6()');
}

function navigateToStep6() {
    if (window.playgroundForm) {
        console.log('🎯 Navigating to Step 6...');
        window.playgroundForm.showStep(6);
        
        setTimeout(() => {
            console.log('🔍 Checking Step 6 status...');
            const locationElement = document.getElementById('preview-location');
            const sportsElement = document.getElementById('preview-sports');
            const timeslotsElement = document.getElementById('preview-timeslots');
            
            console.log('📍 Location display:', locationElement?.textContent);
            console.log('🏃 Sports display:', sportsElement?.innerHTML);
            console.log('⏰ Timeslots display:', timeslotsElement?.innerHTML ? 'HAS CONTENT' : 'EMPTY');
            
            // Force fixes
            if (window.playgroundForm.fixStep6CommonIssues) {
                console.log('🔧 Running fixes...');
                window.playgroundForm.fixStep6CommonIssues();
            }
        }, 2000);
    } else {
        console.log('❌ playgroundForm not available');
    }
}

// Auto-run the validation
validateStep6Fixes();
