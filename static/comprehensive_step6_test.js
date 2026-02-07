// Complete Step 6 Fix Validation Script
// Run this in browser console to test all fixes

async function validateAllStep6Fixes() {
    console.log('🧪 === COMPREHENSIVE STEP 6 VALIDATION TEST ===');
    console.log('🎯 Testing all fixes and functionalities...');
    
    // Test 1: Verify Form Object
    console.log('\n📋 TEST 1: Form Object Validation');
    const hasForm = typeof window.playgroundForm === 'object';
    console.log('✅ playgroundForm object:', hasForm ? 'FOUND' : 'NOT FOUND');
    
    if (!hasForm) {
        console.log('❌ Cannot proceed without playgroundForm object');
        return;
    }
    
    // Test 2: Verify Key Elements
    console.log('\n📋 TEST 2: Key Elements Check');
    const elements = {
        'sport_type_select': document.getElementById('sport_type_select'),
        'country': document.getElementById('country'),
        'state': document.getElementById('state'),
        'city': document.getElementById('city'),
        'preview-location': document.getElementById('preview-location'),
        'preview-sports': document.getElementById('preview-sports'),
        'preview-timeslots': document.getElementById('preview-timeslots'),
        'preview-amenities': document.getElementById('preview-amenities'),
        'amenities-categories': document.getElementById('amenities-categories')
    };
    
    Object.entries(elements).forEach(([name, element]) => {
        console.log(`${element ? '✅' : '❌'} ${name}: ${element ? 'FOUND' : 'NOT FOUND'}`);
    });
    
    // Test 3: Quick Form Fill
    console.log('\n📋 TEST 3: Quick Form Fill for Testing');
    
    // Fill basic info
    const fillData = {
        'name': 'Test Stadium',
        'description': 'A professional testing facility',
        'price_per_hour': '75',
        'capacity': '25'
    };
    
    Object.entries(fillData).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.value = value;
            element.dispatchEvent(new Event('input'));
            console.log(`✅ Filled ${id}: ${value}`);
        }
    });
    
    // Select sport type
    const sportSelect = elements['sport_type_select'];
    if (sportSelect && sportSelect.options.length > 1) {
        sportSelect.selectedIndex = 1;
        sportSelect.dispatchEvent(new Event('change'));
        console.log(`✅ Selected sport: ${sportSelect.options[1].text}`);
    }
    
    // Select location
    const countrySelect = elements['country'];
    if (countrySelect && countrySelect.options.length > 1) {
        countrySelect.selectedIndex = 1;
        countrySelect.dispatchEvent(new Event('change'));
        console.log(`✅ Selected country: ${countrySelect.options[1].text}`);
    }
    
    // Test 4: Amenities Loading
    console.log('\n📋 TEST 4: Amenities Loading Test');
    try {
        if (typeof window.playgroundForm.loadAmenities === 'function') {
            await window.playgroundForm.loadAmenities();
            console.log('✅ Amenities load function executed');
        } else {
            console.log('❌ loadAmenities function not found');
        }
    } catch (error) {
        console.log('⚠️ Amenities load failed, checking fallback...');
        if (typeof window.playgroundForm.renderFallbackAmenities === 'function') {
            window.playgroundForm.renderFallbackAmenities();
            console.log('✅ Fallback amenities rendered');
        }
    }
    
    // Test 5: Navigate to Step 6 and Check Preview
    console.log('\n📋 TEST 5: Step 6 Navigation and Preview Test');
    if (typeof window.playgroundForm.showStep === 'function') {
        window.playgroundForm.showStep(6);
        console.log('✅ Navigated to Step 6');
        
        // Wait for Step 6 to load and check preview
        setTimeout(async () => {
            console.log('\n🔍 STEP 6 PREVIEW VALIDATION:');
            
            // Check location display
            const locationEl = document.getElementById('preview-location');
            const locationText = locationEl?.textContent || 'NOT FOUND';
            console.log(`📍 Location: ${locationText}`);
            
            // Check sports display
            const sportsEl = document.getElementById('preview-sports');
            const sportsContent = sportsEl?.innerHTML || 'NOT FOUND';
            console.log(`🏃 Sports: ${sportsContent.includes('sport') ? 'HAS CONTENT' : 'EMPTY/NO CONTENT'}`);
            
            // Check timeslots
            const timeslotsEl = document.getElementById('preview-timeslots');
            const timeslotsContent = timeslotsEl?.innerHTML || 'NOT FOUND';
            console.log(`⏰ Timeslots: ${timeslotsContent.includes('slot') || timeslotsContent.includes('time') ? 'HAS CONTENT' : 'EMPTY/NO CONTENT'}`);
            
            // Check amenities
            const amenitiesEl = document.getElementById('preview-amenities');
            const amenitiesContent = amenitiesEl?.innerHTML || 'NOT FOUND';
            console.log(`🏢 Amenities: ${amenitiesContent.includes('amenity') || amenitiesContent.length > 50 ? 'HAS CONTENT' : 'EMPTY/NO CONTENT'}`);
            
            // Test 6: Force Fix Common Issues
            console.log('\n📋 TEST 6: Force Fix Common Issues');
            if (typeof window.playgroundForm.fixStep6CommonIssues === 'function') {
                window.playgroundForm.fixStep6CommonIssues();
                console.log('✅ fixStep6CommonIssues executed');
                
                // Re-check after fixes
                setTimeout(() => {
                    console.log('\n🔍 POST-FIX VALIDATION:');
                    
                    const postFixLocation = document.getElementById('preview-location')?.textContent;
                    const postFixSports = document.getElementById('preview-sports')?.innerHTML;
                    const postFixTimeslots = document.getElementById('preview-timeslots')?.innerHTML;
                    const postFixAmenities = document.getElementById('preview-amenities')?.innerHTML;
                    
                    console.log(`📍 Location after fix: ${postFixLocation}`);
                    console.log(`🏃 Sports after fix: ${postFixSports?.includes('sport') ? 'HAS CONTENT' : 'STILL EMPTY'}`);
                    console.log(`⏰ Timeslots after fix: ${postFixTimeslots?.includes('slot') || postFixTimeslots?.includes('time') ? 'HAS CONTENT' : 'STILL EMPTY'}`);
                    console.log(`🏢 Amenities after fix: ${postFixAmenities?.includes('amenity') || (postFixAmenities?.length || 0) > 50 ? 'HAS CONTENT' : 'STILL EMPTY'}`);
                    
                    // Final Summary
                    console.log('\n🏆 === VALIDATION SUMMARY ===');
                    const fixes = [
                        { name: 'Sport Types Detection', status: postFixSports?.includes('sport') ? 'WORKING' : 'NEEDS ATTENTION' },
                        { name: 'Location Display', status: postFixLocation && !postFixLocation.includes('Loading') ? 'WORKING' : 'NEEDS ATTENTION' },
                        { name: 'Time Slots', status: postFixTimeslots?.includes('slot') || postFixTimeslots?.includes('time') ? 'WORKING' : 'NEEDS ATTENTION' },
                        { name: 'Amenities', status: postFixAmenities?.includes('amenity') || (postFixAmenities?.length || 0) > 50 ? 'WORKING' : 'NEEDS ATTENTION' }
                    ];
                    
                    fixes.forEach(fix => {
                        console.log(`${fix.status === 'WORKING' ? '✅' : '⚠️'} ${fix.name}: ${fix.status}`);
                    });
                    
                    const workingCount = fixes.filter(f => f.status === 'WORKING').length;
                    const totalCount = fixes.length;
                    
                    console.log(`\n🎯 OVERALL STATUS: ${workingCount}/${totalCount} fixes working (${Math.round(workingCount/totalCount*100)}%)`);
                    
                    if (workingCount === totalCount) {
                        console.log('🎉 ALL FIXES WORKING CORRECTLY!');
                    } else {
                        console.log('⚠️ Some issues may need additional attention');
                    }
                    
                }, 2000);
                
            } else {
                console.log('❌ fixStep6CommonIssues function not found');
            }
            
        }, 2000);
        
    } else {
        console.log('❌ showStep function not found');
    }
}

// Auto-run validation
console.log('🚀 Starting comprehensive Step 6 validation...');
validateAllStep6Fixes();
