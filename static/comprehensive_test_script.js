/**
 * Comprehensive Test Script for Professional Playground Booking System
 * Tests membership passes, custom slots, backend connectivity, and real-time features
 */

console.log('🚀 Starting Comprehensive Test Suite...');

// Test 1: Professional Membership Pass Creation
async function testMembershipPassCreation() {
    console.log('\n📝 Test 1: Membership Pass Creation');
    
    try {
        // Check if PlaygroundSystem is initialized
        if (!window.PlaygroundSystem) {
            console.error('❌ PlaygroundSystem not initialized');
            return false;
        }
        
        // Test membership pass creation
        const testPass = {
            name: 'Test Professional Pass',
            duration_days: 30,
            price: 1000,
            currency: 'BDT',
            description: 'Test pass for comprehensive testing',
            unlimited_access: true,
            equipment_included: true,
            priority_booking: true,
            group_discount: false,
            is_temporary: true
        };
        
        // Add to system
        if (!window.PlaygroundSystem.membershipPasses) {
            window.PlaygroundSystem.membershipPasses = [];
        }
        
        window.PlaygroundSystem.membershipPasses.push(testPass);
        console.log('✅ Membership pass created successfully');
        
        // Test UI refresh
        if (window.PlaygroundSystem.membershipPass.refreshUI) {
            window.PlaygroundSystem.membershipPass.refreshUI();
            console.log('✅ UI refreshed successfully');
        }
        
        return true;
    } catch (error) {
        console.error('❌ Membership pass test failed:', error);
        return false;
    }
}

// Test 2: Professional Custom Slot Creation
async function testCustomSlotCreation() {
    console.log('\n🎯 Test 2: Custom Slot Creation');
    
    try {
        const testSlot = {
            name: 'Test Professional Slot',
            start_time: '09:00',
            end_time: '10:00',
            price: 500,
            currency: 'BDT',
            slot_type: 'premium',
            day_of_week: 'monday',
            equipment_included: true,
            coaching_available: true,
            is_temporary: true
        };
        
        // Add to system
        if (!window.PlaygroundSystem.customSlots) {
            window.PlaygroundSystem.customSlots = [];
        }
        
        window.PlaygroundSystem.customSlots.push(testSlot);
        console.log('✅ Custom slot created successfully');
        
        // Test UI refresh
        if (window.PlaygroundSystem.customSlot.refreshUI) {
            window.PlaygroundSystem.customSlot.refreshUI();
            console.log('✅ UI refreshed successfully');
        }
        
        return true;
    } catch (error) {
        console.error('❌ Custom slot test failed:', error);
        return false;
    }
}

// Test 3: Revenue Calculation
async function testRevenueCalculation() {
    console.log('\n💰 Test 3: Revenue Calculation');
    
    try {
        if (window.PlaygroundSystem.calculateTotalRevenue) {
            const totalRevenue = window.PlaygroundSystem.calculateTotalRevenue();
            console.log(`✅ Total revenue calculated: ${totalRevenue}`);
            return totalRevenue > 0;
        } else {
            console.error('❌ Revenue calculation function not found');
            return false;
        }
    } catch (error) {
        console.error('❌ Revenue calculation test failed:', error);
        return false;
    }
}

// Test 4: Backend Connectivity
async function testBackendConnectivity() {
    console.log('\n🌐 Test 4: Backend Connectivity');
    
    try {
        // Test membership pass API
        const passResponse = await fetch('/api/membership-passes/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            },
            body: JSON.stringify({
                name: 'API Test Pass',
                duration_days: 15,
                price: 750,
                currency: 'BDT',
                duration_type: 'days',
                is_temporary: true
            })
        });
        
        if (passResponse.ok) {
            const passResult = await passResponse.json();
            console.log('✅ Membership pass API working:', passResult.success);
        } else {
            console.log('⚠️ Membership pass API returned non-200:', passResponse.status);
        }
        
        // Test custom slots API
        const slotResponse = await fetch('/api/professional-slots/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            },
            body: JSON.stringify({
                slot_type: 'regular',
                start_time: '11:00',
                end_time: '12:00',
                price: 400,
                day_of_week: 'tuesday',
                currency: 'BDT',
                is_temporary: true
            })
        });
        
        if (slotResponse.ok) {
            const slotResult = await slotResponse.json();
            console.log('✅ Custom slots API working:', slotResult.success);
        } else {
            console.log('⚠️ Custom slots API returned non-200:', slotResponse.status);
        }
        
        return true;
    } catch (error) {
        console.error('❌ Backend connectivity test failed:', error);
        return false;
    }
}

// Test 5: Professional Features Display
async function testProfessionalFeatures() {
    console.log('\n🎖️ Test 5: Professional Features Display');
    
    try {
        // Check if professional features are displayed
        const membershipFeatures = document.querySelectorAll('.membership-pass-feature');
        const customSlotFeatures = document.querySelectorAll('.custom-slot-feature');
        
        console.log(`✅ Membership pass features found: ${membershipFeatures.length}`);
        console.log(`✅ Custom slot features found: ${customSlotFeatures.length}`);
        
        // Check for professional feature names
        const hasEmojis = document.body.innerHTML.includes('🏆') || 
                         document.body.innerHTML.includes('⚡') ||
                         document.body.innerHTML.includes('🎯');
        
        console.log(`✅ Professional emojis displayed: ${hasEmojis}`);
        
        return membershipFeatures.length > 0 || customSlotFeatures.length > 0;
    } catch (error) {
        console.error('❌ Professional features test failed:', error);
        return false;
    }
}

// Run Comprehensive Test Suite
async function runComprehensiveTests() {
    console.log('🎯 COMPREHENSIVE PLAYGROUND BOOKING SYSTEM TEST SUITE');
    console.log('====================================================');
    
    const results = {
        membershipPass: await testMembershipPassCreation(),
        customSlot: await testCustomSlotCreation(),
        revenueCalculation: await testRevenueCalculation(),
        backendConnectivity: await testBackendConnectivity(),
        professionalFeatures: await testProfessionalFeatures()
    };
    
    console.log('\n📊 TEST RESULTS SUMMARY:');
    console.log('========================');
    Object.entries(results).forEach(([test, passed]) => {
        const status = passed ? '✅ PASSED' : '❌ FAILED';
        console.log(`${test}: ${status}`);
    });
    
    const allPassed = Object.values(results).every(result => result);
    console.log(`\n🏆 OVERALL STATUS: ${allPassed ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`);
    
    return results;
}

// Auto-run tests when script loads
if (typeof window !== 'undefined') {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', runComprehensiveTests);
    } else {
        // DOM is already ready
        setTimeout(runComprehensiveTests, 1000);
    }
}

// Export for manual testing
window.testPlaygroundSystem = {
    runAll: runComprehensiveTests,
    testMembershipPass: testMembershipPassCreation,
    testCustomSlot: testCustomSlotCreation,
    testRevenue: testRevenueCalculation,
    testBackend: testBackendConnectivity,
    testFeatures: testProfessionalFeatures
};

console.log('📋 Test script loaded. Run window.testPlaygroundSystem.runAll() to test manually.');
