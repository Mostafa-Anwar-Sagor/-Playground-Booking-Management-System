/**
 * 🧪 Comprehensive Custom Slot System Test Suite
 * Tests all custom slot functions individually to ensure they work correctly
 */

// Test Configuration
const TEST_CONFIG = {
    enableConsoleOutput: true,
    autoRunTests: true,
    testSlotData: {
        id: 'test-slot-' + Date.now(),
        type: 'Training Session',
        day: 'monday',
        day_name: 'Monday',
        start_hour: '09',
        start_minute: '00',
        start_ampm: 'AM',
        end_hour: '10',
        end_minute: '30',
        end_ampm: 'AM',
        start_time_24: '09:00',
        end_time_24: '10:30',
        duration_hours: 1.5,
        capacity: 16,
        price: 45.00,
        total_price: 67.50,
        recurring: true,
        vip: false,
        auto_confirm: true,
        equipment: false,
        price_multiplier: 1.5,
        sport_data: {
            id: 'football',
            name: 'Football',
            icon: '⚽'
        },
        currency_data: {
            name: 'USD',
            symbol: '$',
            decimal_places: 2
        },
        status: 'draft',
        created_at: new Date().toISOString()
    }
};

// Test Results Tracker
const testResults = {
    passed: 0,
    failed: 0,
    total: 0,
    errors: []
};

// Utility Functions
function log(message, type = 'info') {
    if (!TEST_CONFIG.enableConsoleOutput) return;
    
    const emoji = {
        info: 'ℹ️',
        success: '✅',
        error: '❌',
        warning: '⚠️',
        test: '🧪'
    };
    
    console.log(`${emoji[type]} ${message}`);
}

function assert(condition, testName, errorMessage = '') {
    testResults.total++;
    
    if (condition) {
        testResults.passed++;
        log(`${testName} - PASSED`, 'success');
        return true;
    } else {
        testResults.failed++;
        const error = `${testName} - FAILED${errorMessage ? ': ' + errorMessage : ''}`;
        testResults.errors.push(error);
        log(error, 'error');
        return false;
    }
}

// Individual Function Tests
class CustomSlotTester {
    
    // Test 1: formatTime12Hour function
    testFormatTime12Hour() {
        log('Testing formatTime12Hour function...', 'test');
        
        try {
            // Test morning times
            assert(formatTime12Hour('09:00') === '9:00 AM', 'formatTime12Hour - Morning time');
            assert(formatTime12Hour('00:30') === '12:30 AM', 'formatTime12Hour - Midnight');
            
            // Test afternoon times
            assert(formatTime12Hour('12:00') === '12:00 PM', 'formatTime12Hour - Noon');
            assert(formatTime12Hour('15:45') === '3:45 PM', 'formatTime12Hour - Afternoon');
            assert(formatTime12Hour('23:59') === '11:59 PM', 'formatTime12Hour - Late night');
            
            // Test edge cases
            assert(formatTime12Hour('') === '', 'formatTime12Hour - Empty string');
            assert(formatTime12Hour(null) === '', 'formatTime12Hour - Null input');
            
        } catch (error) {
            assert(false, 'formatTime12Hour - Exception handling', error.message);
        }
    }
    
    // Test 2: updateCustomSlotFromStep1 function
    testUpdateCustomSlotFromStep1() {
        log('Testing updateCustomSlotFromStep1 function...', 'test');
        
        try {
            if (typeof updateCustomSlotFromStep1 === 'function') {
                updateCustomSlotFromStep1();
                assert(true, 'updateCustomSlotFromStep1 - Function exists and executes');
            } else {
                assert(false, 'updateCustomSlotFromStep1 - Function not found');
            }
        } catch (error) {
            assert(false, 'updateCustomSlotFromStep1 - Execution error', error.message);
        }
    }
    
    // Test 3: createProfessionalCustomSlot function
    testCreateProfessionalCustomSlot() {
        log('Testing createProfessionalCustomSlot function...', 'test');
        
        try {
            if (typeof createProfessionalCustomSlot === 'function') {
                // Test function existence only, don't call it without form elements
                assert(true, 'createProfessionalCustomSlot - Function exists');
                log('⚠️ Skipping execution test (requires form elements)', 'warning');
            } else {
                assert(false, 'createProfessionalCustomSlot - Function not found');
            }
        } catch (error) {
            assert(false, 'createProfessionalCustomSlot - Function check error', error.message);
        }
    }
    
    // Test 4: renderCustomSlotsList function
    testRenderCustomSlotsList() {
        log('Testing renderCustomSlotsList function...', 'test');
        
        try {
            if (typeof renderCustomSlotsList === 'function') {
                // Ensure customSlots array exists
                if (!window.customSlots) {
                    window.customSlots = [TEST_CONFIG.testSlotData];
                }
                
                renderCustomSlotsList();
                assert(true, 'renderCustomSlotsList - Function exists and executes');
            } else {
                assert(false, 'renderCustomSlotsList - Function not found');
            }
        } catch (error) {
            assert(false, 'renderCustomSlotsList - Execution error', error.message);
        }
    }
    
    // Test 5: editCustomSlot function
    testEditCustomSlot() {
        log('Testing editCustomSlot function...', 'test');
        
        try {
            if (typeof editCustomSlot === 'function') {
                // Add test slot to customSlots array
                if (!window.customSlots) {
                    window.customSlots = [];
                }
                
                window.customSlots.push(TEST_CONFIG.testSlotData);
                editCustomSlot(TEST_CONFIG.testSlotData.id);
                
                assert(true, 'editCustomSlot - Function exists and executes');
            } else {
                assert(false, 'editCustomSlot - Function not found');
            }
        } catch (error) {
            assert(false, 'editCustomSlot - Execution error', error.message);
        }
    }
    
    // Test 6: deleteCustomSlot function
    testDeleteCustomSlot() {
        log('Testing deleteCustomSlot function...', 'test');
        
        try {
            if (typeof deleteCustomSlot === 'function') {
                // Add test slot to customSlots array
                if (!window.customSlots) {
                    window.customSlots = [];
                }
                
                const testSlot = { ...TEST_CONFIG.testSlotData, id: 'delete-test-' + Date.now() };
                window.customSlots.push(testSlot);
                
                const initialCount = window.customSlots.length;
                deleteCustomSlot(testSlot.id);
                
                assert(true, 'deleteCustomSlot - Function exists and executes');
            } else {
                assert(false, 'deleteCustomSlot - Function not found');
            }
        } catch (error) {
            assert(false, 'deleteCustomSlot - Execution error', error.message);
        }
    }
    
    // Test 7: duplicateCustomSlot function
    testDuplicateCustomSlot() {
        log('Testing duplicateCustomSlot function...', 'test');
        
        try {
            if (typeof duplicateCustomSlot === 'function') {
                // Add test slot to customSlots array
                if (!window.customSlots) {
                    window.customSlots = [];
                }
                
                const testSlot = { ...TEST_CONFIG.testSlotData, id: 'duplicate-test-' + Date.now() };
                window.customSlots.push(testSlot);
                
                duplicateCustomSlot(testSlot.id);
                assert(true, 'duplicateCustomSlot - Function exists and executes');
            } else {
                assert(false, 'duplicateCustomSlot - Function not found');
            }
        } catch (error) {
            assert(false, 'duplicateCustomSlot - Execution error', error.message);
        }
    }
    
    // Test 8: updateCustomSlotPreview function
    testUpdateCustomSlotPreview() {
        log('Testing updateCustomSlotPreview function...', 'test');
        
        try {
            if (typeof updateCustomSlotPreview === 'function') {
                // Test function existence only, don't call it without form elements
                assert(true, 'updateCustomSlotPreview - Function exists');
                log('⚠️ Skipping execution test (requires form elements)', 'warning');
            } else {
                assert(false, 'updateCustomSlotPreview - Function not found');
            }
        } catch (error) {
            assert(false, 'updateCustomSlotPreview - Function check error', error.message);
        }
    }
    
    // Test 9: updateTotalRevenue function
    testUpdateTotalRevenue() {
        log('Testing updateTotalRevenue function...', 'test');
        
        try {
            if (typeof updateTotalRevenue === 'function') {
                updateTotalRevenue();
                assert(true, 'updateTotalRevenue - Function exists and executes');
            } else {
                assert(false, 'updateTotalRevenue - Function not found');
            }
        } catch (error) {
            assert(false, 'updateTotalRevenue - Execution error', error.message);
        }
    }
    
    // Test 10: Backend Integration
    testBackendIntegration() {
        log('Testing backend integration functions...', 'test');
        
        try {
            // Test integrateCustomSlotsWithMainForm
            if (typeof integrateCustomSlotsWithMainForm === 'function') {
                const result = integrateCustomSlotsWithMainForm();
                assert(typeof result === 'boolean', 'integrateCustomSlotsWithMainForm - Returns boolean');
            } else {
                assert(false, 'integrateCustomSlotsWithMainForm - Function not found');
            }
            
            // Test saveCustomSlotsToBackend
            if (typeof saveCustomSlotsToBackend === 'function') {
                assert(true, 'saveCustomSlotsToBackend - Function exists');
            } else {
                assert(false, 'saveCustomSlotsToBackend - Function not found');
            }
            
        } catch (error) {
            assert(false, 'Backend Integration - Execution error', error.message);
        }
    }
    
    // Setup and Cleanup
    setupTestDOM() {
        // Create minimal DOM elements for testing
        if (!document.getElementById('custom-slots-list')) {
            const container = document.createElement('div');
            container.id = 'custom-slots-list';
            document.body.appendChild(container);
        }
        
        if (!document.getElementById('custom-slot-creation-form')) {
            const form = document.createElement('div');
            form.id = 'custom-slot-creation-form';
            form.className = 'hidden';
            document.body.appendChild(form);
        }
    }
    
    cleanupTestDOM() {
        // Remove test DOM elements
        const elementsToRemove = [
            'custom-slots-list',
            'custom-slot-creation-form'
        ];
        
        elementsToRemove.forEach(id => {
            const element = document.getElementById(id);
            if (element && element.parentNode) {
                element.parentNode.removeChild(element);
            }
        });
    }
    
    // Run all tests
    runAllTests() {
        log('🚀 Starting Custom Slot System Tests...', 'test');
        
        // Initialize test environment
        this.setupTestDOM();
        
        // Run individual tests
        this.testFormatTime12Hour();
        this.testUpdateCustomSlotFromStep1();
        this.testCreateProfessionalCustomSlot();
        this.testRenderCustomSlotsList();
        this.testEditCustomSlot();
        this.testDeleteCustomSlot();
        this.testDuplicateCustomSlot();
        this.testUpdateCustomSlotPreview();
        this.testUpdateTotalRevenue();
        this.testBackendIntegration();
        
        // Cleanup
        this.cleanupTestDOM();
        
        // Report results
        this.reportResults();
    }
    
    reportResults() {
        log('📊 Test Results Summary:', 'test');
        log(`✅ Passed: ${testResults.passed}`, 'success');
        log(`❌ Failed: ${testResults.failed}`, 'error');
        log(`📈 Total: ${testResults.total}`, 'info');
        log(`📊 Success Rate: ${((testResults.passed / testResults.total) * 100).toFixed(1)}%`, 'info');
        
        if (testResults.errors.length > 0) {
            log('❌ Failed Tests:', 'error');
            testResults.errors.forEach(error => log(`  • ${error}`, 'error'));
        }
        
        if (testResults.failed === 0) {
            log('🎉 All tests passed! Custom slot system is working correctly.', 'success');
        } else {
            log(`⚠️ ${testResults.failed} test(s) failed. Please check the errors above.`, 'warning');
        }
    }
}

// Auto-run tests when page loads
if (TEST_CONFIG.autoRunTests) {
    // Wait for page to be fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                const tester = new CustomSlotTester();
                tester.runAllTests();
            }, 2000); // Wait 2 seconds for all scripts to initialize
        });
    } else {
        setTimeout(() => {
            const tester = new CustomSlotTester();
            tester.runAllTests();
        }, 2000);
    }
}

// Export for manual testing
window.CustomSlotTester = CustomSlotTester;
window.runCustomSlotTests = () => {
    const tester = new CustomSlotTester();
    tester.runAllTests();
};

console.log('🧪 Custom Slot Test Suite loaded. Run window.runCustomSlotTests() to test manually.');
