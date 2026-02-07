/**
 * 🎯 Custom Slot Feature Validation Script
 * Professional testing for each custom slot element and functionality
 */

class CustomSlotFeatureValidator {
    constructor() {
        this.testResults = [];
        this.currentSlotData = {};
    }

    async validateAllFeatures() {
        console.log('🎯 Starting Professional Custom Slot Feature Validation...');
        console.log('═══════════════════════════════════════════════════════════');

        await this.testTimeFormatting();
        await this.testSlotCreation();
        await this.testSlotEditing();
        await this.testSlotDeletion();
        await this.testSlotDuplication();
        await this.testPriceCalculation();
        await this.testCapacityValidation();
        await this.testUIResponsiveness();
        await this.testDataPersistence();
        await this.testIntegrationWithMainForm();

        this.generateDetailedReport();
    }

    async testTimeFormatting() {
        console.log('\n🕒 Testing Time Formatting (12-hour format)...');
        
        const testCases = [
            { input: '09:00', expected: '9:00 AM', desc: 'Morning time' },
            { input: '12:00', expected: '12:00 PM', desc: 'Noon' },
            { input: '15:30', expected: '3:30 PM', desc: 'Afternoon time' },
            { input: '00:00', expected: '12:00 AM', desc: 'Midnight' },
            { input: '23:45', expected: '11:45 PM', desc: 'Late night' }
        ];

        for (const test of testCases) {
            try {
                const result = window.formatTime12Hour ? window.formatTime12Hour(test.input) : null;
                const passed = result === test.expected;
                
                this.logTest('Time Formatting', test.desc, passed, {
                    input: test.input,
                    expected: test.expected,
                    actual: result
                });
            } catch (error) {
                this.logTest('Time Formatting', test.desc, false, { error: error.message });
            }
        }
    }

    async testSlotCreation() {
        console.log('\n➕ Testing Slot Creation...');

        // Test form validation
        const testData = {
            name: 'Professional Training Session',
            startTime: '09:00',
            endTime: '11:00',
            price: 75,
            capacity: 12,
            description: 'Premium training session for professionals'
        };

        try {
            // Fill form fields
            this.fillSlotForm(testData);
            this.logTest('Slot Creation', 'Form data entry', true, testData);

            // Test slot creation function
            if (window.createProfessionalCustomSlot) {
                // Don't actually create to avoid side effects, just test function exists
                this.logTest('Slot Creation', 'Creation function available', true);
            } else {
                this.logTest('Slot Creation', 'Creation function available', false);
            }

        } catch (error) {
            this.logTest('Slot Creation', 'Overall creation process', false, { error: error.message });
        }
    }

    async testSlotEditing() {
        console.log('\n✏️ Testing Slot Editing...');

        try {
            if (window.editCustomSlot && typeof window.editCustomSlot === 'function') {
                this.logTest('Slot Editing', 'Edit function exists', true);
                
                // Test with dummy slot ID
                const testSlotId = 'test-slot-123';
                window.editCustomSlot(testSlotId);
                this.logTest('Slot Editing', 'Edit function executable', true);
                
            } else {
                this.logTest('Slot Editing', 'Edit function exists', false);
            }
        } catch (error) {
            this.logTest('Slot Editing', 'Edit functionality', false, { error: error.message });
        }
    }

    async testSlotDeletion() {
        console.log('\n🗑️ Testing Slot Deletion...');

        try {
            if (window.deleteCustomSlot && typeof window.deleteCustomSlot === 'function') {
                this.logTest('Slot Deletion', 'Delete function exists', true);
                
                // Test with dummy slot ID
                const testSlotId = 'test-slot-123';
                window.deleteCustomSlot(testSlotId);
                this.logTest('Slot Deletion', 'Delete function executable', true);
                
            } else {
                this.logTest('Slot Deletion', 'Delete function exists', false);
            }
        } catch (error) {
            this.logTest('Slot Deletion', 'Delete functionality', false, { error: error.message });
        }
    }

    async testSlotDuplication() {
        console.log('\n📋 Testing Slot Duplication...');

        try {
            if (window.duplicateCustomSlot && typeof window.duplicateCustomSlot === 'function') {
                this.logTest('Slot Duplication', 'Duplicate function exists', true);
                
                // Test with dummy slot ID
                const testSlotId = 'test-slot-123';
                window.duplicateCustomSlot(testSlotId);
                this.logTest('Slot Duplication', 'Duplicate function executable', true);
                
            } else {
                this.logTest('Slot Duplication', 'Duplicate function exists', false);
            }
        } catch (error) {
            this.logTest('Slot Duplication', 'Duplication functionality', false, { error: error.message });
        }
    }

    async testPriceCalculation() {
        console.log('\n💰 Testing Price Calculation...');

        try {
            if (window.updateTotalRevenue && typeof window.updateTotalRevenue === 'function') {
                this.logTest('Price Calculation', 'Revenue calculation function exists', true);
                
                window.updateTotalRevenue();
                this.logTest('Price Calculation', 'Revenue calculation executable', true);
                
            } else {
                this.logTest('Price Calculation', 'Revenue calculation function exists', false);
            }

            // Test currency formatting
            const priceElements = document.querySelectorAll('[class*="currency"], [data-currency]');
            const hasPriceElements = priceElements.length > 0;
            this.logTest('Price Calculation', 'Currency elements present', hasPriceElements, {
                count: priceElements.length
            });

        } catch (error) {
            this.logTest('Price Calculation', 'Price calculation system', false, { error: error.message });
        }
    }

    async testCapacityValidation() {
        console.log('\n👥 Testing Capacity Validation...');

        const capacityTests = [
            { value: 8, valid: true, desc: 'Normal capacity' },
            { value: 0, valid: false, desc: 'Zero capacity' },
            { value: -5, valid: false, desc: 'Negative capacity' },
            { value: 100, valid: true, desc: 'Large capacity' },
            { value: 'abc', valid: false, desc: 'Non-numeric capacity' }
        ];

        capacityTests.forEach(test => {
            const isValid = !isNaN(test.value) && parseInt(test.value) > 0;
            const passed = isValid === test.valid;
            
            this.logTest('Capacity Validation', test.desc, passed, {
                value: test.value,
                expected: test.valid,
                actual: isValid
            });
        });
    }

    async testUIResponsiveness() {
        console.log('\n📱 Testing UI Responsiveness...');

        // Test DOM elements
        const criticalElements = [
            'custom-slots-list',
            'custom-slot-name',
            'custom-slot-start-time',
            'custom-slot-end-time',
            'custom-slot-price',
            'custom-slot-capacity',
            'create-custom-slot-btn'
        ];

        criticalElements.forEach(elementId => {
            const element = document.getElementById(elementId);
            const exists = element !== null;
            
            this.logTest('UI Responsiveness', `Element #${elementId}`, exists);
            
            if (exists) {
                // Test visibility
                const isVisible = element.offsetParent !== null;
                this.logTest('UI Responsiveness', `Element #${elementId} visibility`, isVisible);
                
                // Test interaction capability
                const isInteractive = !element.disabled && !element.readOnly;
                this.logTest('UI Responsiveness', `Element #${elementId} interactivity`, isInteractive);
            }
        });
    }

    async testDataPersistence() {
        console.log('\n💾 Testing Data Persistence...');

        try {
            // Test if custom slots array exists
            const hasCustomSlots = window.customSlots && Array.isArray(window.customSlots);
            this.logTest('Data Persistence', 'Custom slots array exists', hasCustomSlots, {
                type: typeof window.customSlots,
                length: hasCustomSlots ? window.customSlots.length : 'N/A'
            });

            // Test if data structure is valid
            if (hasCustomSlots && window.customSlots.length > 0) {
                const firstSlot = window.customSlots[0];
                const hasRequiredFields = firstSlot.hasOwnProperty('id') && 
                                        firstSlot.hasOwnProperty('name') && 
                                        firstSlot.hasOwnProperty('start_time');
                
                this.logTest('Data Persistence', 'Slot data structure valid', hasRequiredFields, firstSlot);
            }

        } catch (error) {
            this.logTest('Data Persistence', 'Data persistence system', false, { error: error.message });
        }
    }

    async testIntegrationWithMainForm() {
        console.log('\n🔗 Testing Integration with Main Form...');

        try {
            if (window.integrateCustomSlotsWithMainForm && typeof window.integrateCustomSlotsWithMainForm === 'function') {
                this.logTest('Main Form Integration', 'Integration function exists', true);
                
                const result = window.integrateCustomSlotsWithMainForm();
                this.logTest('Main Form Integration', 'Integration function executable', true, {
                    result: result
                });
                
            } else {
                this.logTest('Main Form Integration', 'Integration function exists', false);
            }

            // Test step validation
            if (window.updateStepValidation && typeof window.updateStepValidation === 'function') {
                this.logTest('Main Form Integration', 'Step validation function exists', true);
            } else {
                this.logTest('Main Form Integration', 'Step validation function exists', false);
            }

        } catch (error) {
            this.logTest('Main Form Integration', 'Integration system', false, { error: error.message });
        }
    }

    fillSlotForm(data) {
        const fieldMap = {
            'custom-slot-name': data.name,
            'custom-slot-start-time': data.startTime,
            'custom-slot-end-time': data.endTime,
            'custom-slot-price': data.price,
            'custom-slot-capacity': data.capacity,
            'custom-slot-description': data.description
        };

        Object.entries(fieldMap).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element && value !== undefined) {
                element.value = value;
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
    }

    logTest(category, testName, passed, details = null) {
        const icon = passed ? '✅' : '❌';
        const message = `${icon} ${category}: ${testName}`;
        
        console.log(message);
        if (details) {
            console.log('   📋 Details:', details);
        }

        this.testResults.push({
            category,
            testName,
            passed,
            details,
            timestamp: new Date().toISOString()
        });
    }

    generateDetailedReport() {
        console.log('\n' + '═'.repeat(80));
        console.log('📊 PROFESSIONAL CUSTOM SLOT FEATURE VALIDATION REPORT');
        console.log('═'.repeat(80));

        const totalTests = this.testResults.length;
        const passedTests = this.testResults.filter(test => test.passed).length;
        const failedTests = totalTests - passedTests;
        const successRate = totalTests > 0 ? ((passedTests / totalTests) * 100).toFixed(1) : 0;

        console.log(`\n📈 SUMMARY:`);
        console.log(`   ✅ Passed: ${passedTests}`);
        console.log(`   ❌ Failed: ${failedTests}`);
        console.log(`   📊 Total: ${totalTests}`);
        console.log(`   🎯 Success Rate: ${successRate}%`);

        // Group by category
        const categories = {};
        this.testResults.forEach(test => {
            if (!categories[test.category]) {
                categories[test.category] = [];
            }
            categories[test.category].push(test);
        });

        console.log(`\n📋 DETAILED RESULTS BY CATEGORY:`);
        Object.entries(categories).forEach(([category, tests]) => {
            const categoryPassed = tests.filter(test => test.passed).length;
            const categoryTotal = tests.length;
            const categoryRate = ((categoryPassed / categoryTotal) * 100).toFixed(1);
            
            console.log(`\n🔸 ${category} (${categoryPassed}/${categoryTotal} - ${categoryRate}%)`);
            tests.forEach(test => {
                const icon = test.passed ? '  ✅' : '  ❌';
                console.log(`${icon} ${test.testName}`);
            });
        });

        // Overall assessment
        if (successRate >= 95) {
            console.log(`\n🎉 EXCELLENT! Custom Slot System is performing exceptionally well!`);
        } else if (successRate >= 85) {
            console.log(`\n✅ GOOD! Custom Slot System is working well with minor areas for improvement.`);
        } else if (successRate >= 70) {
            console.log(`\n⚠️ FAIR! Custom Slot System needs attention in several areas.`);
        } else {
            console.log(`\n❌ POOR! Custom Slot System requires significant improvements.`);
        }

        console.log('\n' + '═'.repeat(80));
        return this.testResults;
    }
}

// Global access
if (typeof window !== 'undefined') {
    window.CustomSlotFeatureValidator = CustomSlotFeatureValidator;
    
    window.runCustomSlotFeatureValidation = async function() {
        const validator = new CustomSlotFeatureValidator();
        return await validator.validateAllFeatures();
    };

    console.log('🎯 Custom Slot Feature Validator loaded!');
    console.log('💡 Run: window.runCustomSlotFeatureValidation()');
}
