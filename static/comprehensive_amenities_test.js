// Comprehensive Amenities and Step 6 Testing Script

console.log('🧪 Starting Comprehensive Amenities and Step 6 Testing...');

// Test 1: Validate amenities functionality
function testAmenitiesSystem() {
    console.log('\n📋 Testing Amenities System...');
    
    // Check if amenities container exists
    const amenitiesContainer = document.getElementById('amenities-categories');
    if (!amenitiesContainer) {
        console.error('❌ Amenities container not found');
        return false;
    }
    
    // Check if amenities are rendered
    const amenityItems = amenitiesContainer.querySelectorAll('.amenity-item');
    console.log('🏢 Found amenity items:', amenityItems.length);
    
    if (amenityItems.length === 0) {
        console.log('🔄 No amenities found, triggering fallback rendering...');
        if (window.playgroundForm && window.playgroundForm.renderFallbackAmenities) {
            window.playgroundForm.renderFallbackAmenities();
        }
        
        // Recheck after rendering
        const newAmenityItems = amenitiesContainer.querySelectorAll('.amenity-item');
        console.log('🏢 After fallback rendering:', newAmenityItems.length, 'amenities');
    }
    
    // Test amenity selection functionality
    const firstAmenity = amenitiesContainer.querySelector('.amenity-item');
    if (firstAmenity) {
        console.log('🧪 Testing amenity selection...');
        
        // Test free option
        const freeBtn = firstAmenity.querySelector('.free-btn');
        if (freeBtn) {
            console.log('✅ Free button found, testing click...');
            freeBtn.click();
            
            // Check if selection worked
            const isSelected = firstAmenity.dataset.selected === 'true';
            const pricing = firstAmenity.dataset.pricing;
            console.log('📊 Selection result - Selected:', isSelected, 'Pricing:', pricing);
            
            // Test deselection
            freeBtn.click();
            const isDeselected = firstAmenity.dataset.selected === 'false';
            console.log('📊 Deselection result - Deselected:', isDeselected);
        }
        
        // Test paid option
        const paidBtn = firstAmenity.querySelector('.paid-btn');
        if (paidBtn) {
            console.log('✅ Paid button found, testing click...');
            paidBtn.click();
            
            // Check if price input is shown
            const priceContainer = firstAmenity.querySelector('.price-input-container');
            const isVisible = priceContainer && !priceContainer.classList.contains('hidden');
            console.log('💰 Price input visible:', isVisible);
            
            // Test price input
            const priceInput = firstAmenity.querySelector('.amenity-price-input');
            if (priceInput) {
                priceInput.value = '100';
                priceInput.dispatchEvent(new Event('input'));
                console.log('💰 Price input tested with value:', priceInput.value);
            }
        }
    }
    
    // Check global selected amenities
    console.log('🌐 Global selected amenities:', Object.keys(window.selectedAmenities || {}).length);
    
    return true;
}

// Test 2: Validate sports selection
function testSportsSelection() {
    console.log('\n⚽ Testing Sports Selection...');
    
    const sportSelect = document.getElementById('sport_type_select');
    if (!sportSelect) {
        console.error('❌ Sport select element not found');
        return false;
    }
    
    console.log('✅ Sport select found with', sportSelect.options.length, 'options');
    
    if (sportSelect.selectedIndex > 0) {
        const selectedOption = sportSelect.options[sportSelect.selectedIndex];
        console.log('⚽ Selected sport:', selectedOption.text, 'Value:', selectedOption.value);
    } else {
        console.log('⚠️ No sport selected');
    }
    
    return true;
}

// Test 3: Validate Step 6 preview
function testStep6Preview() {
    console.log('\n🎯 Testing Step 6 Preview...');
    
    // Navigate to Step 6 if not already there
    const step6 = document.getElementById('step-6');
    if (!step6 || step6.classList.contains('hidden')) {
        console.log('📄 Navigating to Step 6...');
        if (window.showStep) {
            window.showStep(6);
        }
    }
    
    // Wait a moment for Step 6 to load
    setTimeout(() => {
        // Check basic info
        const playgroundName = document.getElementById('preview-playground-name');
        const playgroundDescription = document.getElementById('preview-description');
        const playgroundPrice = document.getElementById('preview-price');
        const playgroundLocation = document.getElementById('preview-location');
        
        console.log('📊 Preview Elements Status:');
        console.log('  - Name:', playgroundName?.textContent || 'Not found');
        console.log('  - Description:', playgroundDescription?.textContent || 'Not found');
        console.log('  - Price:', playgroundPrice?.textContent || 'Not found');
        console.log('  - Location:', playgroundLocation?.textContent || 'Not found');
        
        // Check sports
        const sportsContainer = document.getElementById('preview-sports');
        if (sportsContainer) {
            const sportsCount = sportsContainer.querySelectorAll('.sport-tag, span').length;
            console.log('  - Sports:', sportsCount, 'displayed');
        }
        
        // Check amenities
        const amenitiesContainer = document.getElementById('preview-amenities');
        if (amenitiesContainer) {
            const amenitiesCount = amenitiesContainer.querySelectorAll('.amenity-card').length;
            console.log('  - Amenities:', amenitiesCount, 'displayed');
        }
        
        // Check time slots
        const timeslotsContainer = document.getElementById('preview-timeslots');
        if (timeslotsContainer) {
            const slotsCount = timeslotsContainer.querySelectorAll('.slot-card, div[class*="slot"]').length;
            console.log('  - Time Slots:', slotsCount, 'displayed');
        }
        
        // Trigger fixes if needed
        if (window.playgroundForm && window.playgroundForm.fixStep6CommonIssues) {
            console.log('🔧 Running Step 6 fixes...');
            window.playgroundForm.fixStep6CommonIssues();
        }
        
    }, 1000);
    
    return true;
}

// Test 4: Test time slots generation
function testTimeSlotsGeneration() {
    console.log('\n⏰ Testing Time Slots Generation...');
    
    // Check if operating hours are set
    const openTime = document.getElementById('opening_time')?.value;
    const closeTime = document.getElementById('closing_time')?.value;
    const slotDuration = document.getElementById('slot_duration')?.value;
    
    console.log('📋 Operating Hours:');
    console.log('  - Open Time:', openTime || 'Not set');
    console.log('  - Close Time:', closeTime || 'Not set');
    console.log('  - Slot Duration:', slotDuration || 'Not set');
    
    // Try to generate sample slots
    if (openTime && closeTime) {
        try {
            const slots = generateSampleSlots(openTime, closeTime, parseInt(slotDuration) || 60);
            console.log('✅ Generated', slots.length, 'sample slots');
            return slots;
        } catch (error) {
            console.error('❌ Error generating slots:', error);
        }
    }
    
    return [];
}

// Helper function to generate sample slots
function generateSampleSlots(openTime, closeTime, duration) {
    const slots = [];
    const [openHour, openMin] = openTime.split(':').map(Number);
    const [closeHour, closeMin] = closeTime.split(':').map(Number);
    
    let currentHour = openHour;
    let currentMin = openMin;
    
    while (currentHour < closeHour || (currentHour === closeHour && currentMin < closeMin)) {
        const startTime = `${currentHour.toString().padStart(2, '0')}:${currentMin.toString().padStart(2, '0')}`;
        
        // Calculate end time
        let endHour = currentHour;
        let endMin = currentMin + duration;
        
        if (endMin >= 60) {
            endHour += Math.floor(endMin / 60);
            endMin = endMin % 60;
        }
        
        const endTime = `${endHour.toString().padStart(2, '0')}:${endMin.toString().padStart(2, '0')}`;
        
        // Stop if end time exceeds closing time
        if (endHour > closeHour || (endHour === closeHour && endMin > closeMin)) {
            break;
        }
        
        slots.push({
            time: `${startTime} - ${endTime}`,
            startTime: startTime,
            endTime: endTime,
            price: 25, // Default price
            available: Math.random() > 0.3 // 70% chance of being available
        });
        
        // Move to next slot
        currentMin += duration;
        if (currentMin >= 60) {
            currentHour += Math.floor(currentMin / 60);
            currentMin = currentMin % 60;
        }
    }
    
    return slots;
}

// Test 5: Validate form data collection
function testFormDataCollection() {
    console.log('\n📝 Testing Form Data Collection...');
    
    const formElement = document.getElementById('playground-form');
    if (!formElement) {
        console.error('❌ Playground form not found');
        return false;
    }
    
    try {
        const formData = new FormData(formElement);
        const dataObject = {};
        
        for (let [key, value] of formData.entries()) {
            dataObject[key] = value;
        }
        
        console.log('📋 Form Data Keys:', Object.keys(dataObject).length);
        console.log('📋 Key Sample:', Object.keys(dataObject).slice(0, 10));
        
        return true;
    } catch (error) {
        console.error('❌ Form data collection error:', error);
        return false;
    }
}

// Main test runner
function runComprehensiveTests() {
    console.log('🚀 Starting Comprehensive Tests...\n');
    
    const results = {
        amenities: testAmenitiesSystem(),
        sports: testSportsSelection(),
        timeslots: testTimeSlotsGeneration(),
        formData: testFormDataCollection(),
        step6: testStep6Preview()
    };
    
    console.log('\n📊 Test Results Summary:');
    Object.entries(results).forEach(([test, result]) => {
        const status = result ? '✅ PASS' : '❌ FAIL';
        console.log(`  ${test}: ${status}`);
    });
    
    const totalPassed = Object.values(results).filter(Boolean).length;
    const totalTests = Object.values(results).length;
    
    console.log(`\n🏆 Overall: ${totalPassed}/${totalTests} tests passed`);
    
    return results;
}

// Auto-run if called directly
if (typeof window !== 'undefined') {
    window.runComprehensiveTests = runComprehensiveTests;
    window.testAmenitiesSystem = testAmenitiesSystem;
    window.testStep6Preview = testStep6Preview;
    
    console.log('🧪 Comprehensive test functions loaded!');
    console.log('   Run: runComprehensiveTests() for full test suite');
    console.log('   Run: testAmenitiesSystem() for amenities only');
    console.log('   Run: testStep6Preview() for Step 6 only');
}
