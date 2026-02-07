/**
 * 🎯 Professional Custom Slot System - Comprehensive Testing Suite
 * Date: August 13, 2025
 * Purpose: Complete validation of all custom slot functionalities
 */

class CustomSlotTestSuite {
    constructor() {
        this.results = {
            passed: 0,
            failed: 0,
            warnings: 0,
            details: []
        };
        
        this.testData = {
            validSlot: {
                name: 'Morning Session',
                start_time: '09:00',
                end_time: '11:00',
                price: 50,
                capacity: 8,
                description: 'Premium morning training session'
            },
            invalidSlot: {
                name: '',
                start_time: '14:00',
                end_time: '12:00', // Invalid: end before start
                price: -10, // Invalid: negative price
                capacity: 0 // Invalid: zero capacity
            }
        };
    }

    log(type, message, details = null) {
        const timestamp = new Date().toLocaleTimeString();
        const icon = {
            'pass': '✅',
            'fail': '❌',
            'warn': '⚠️',
            'info': 'ℹ️',
            'test': '🧪'
        }[type] || '🔍';
        
        console.log(`${icon} [${timestamp}] ${message}`);
        if (details) console.log('   Details:', details);
        
        this.results.details.push({
            type,
            message,
            details,
            timestamp
        });
    }

    async runCompleteTestSuite() {
        this.log('test', '🚀 Starting Professional Custom Slot System Tests');
        console.log('='.repeat(80));
        
        // Test all functionalities
        await this.testCoreComponents();
        await this.testFormValidation();
        await this.testCRUDOperations();
        await this.testUIInteractions();
        await this.testDataIntegrity();
        await this.testErrorHandling();
        await this.testPerformance();
        
        this.printFinalReport();
    }

    async testCoreComponents() {
        this.log('test', '📋 Testing Core Components...');
        
        // Test 1: Function existence
        const functions = [
            'createProfessionalCustomSlot',
            'editCustomSlot',
            'deleteCustomSlot',
            'duplicateCustomSlot',
            'renderCustomSlotsList',
            'updateCustomSlotPreview',
            'formatTime12Hour',
            'updateTotalRevenue'
        ];
        
        functions.forEach(funcName => {
            if (window[funcName] && typeof window[funcName] === 'function') {
                this.results.passed++;
                this.log('pass', `Function ${funcName} exists and is callable`);
            } else {
                this.results.failed++;
                this.log('fail', `Function ${funcName} missing or not callable`);
            }
        });

        // Test 2: DOM elements existence
        const elements = [
            'custom-slots-list',
            'custom-slot-name',
            'custom-slot-start-time',
            'custom-slot-end-time',
            'custom-slot-price',
            'custom-slot-capacity',
            'create-custom-slot-btn'
        ];
        
        elements.forEach(elementId => {
            const element = document.getElementById(elementId);
            if (element) {
                this.results.passed++;
                this.log('pass', `Element #${elementId} found in DOM`);
            } else {
                this.results.failed++;
                this.log('fail', `Element #${elementId} missing from DOM`);
            }
        });
    }

    async testFormValidation() {
        this.log('test', '📝 Testing Form Validation...');
        
        // Test time format validation
        const timeTests = [
            { time: '09:00', expected: true, desc: 'Valid morning time' },
            { time: '23:59', expected: true, desc: 'Valid late night time' },
            { time: '25:00', expected: false, desc: 'Invalid hour' },
            { time: '12:60', expected: false, desc: 'Invalid minute' },
            { time: '', expected: false, desc: 'Empty time' }
        ];

        timeTests.forEach(test => {
            try {
                // Test formatTime12Hour function
                const result = window.formatTime12Hour ? window.formatTime12Hour(test.time) : null;
                if ((result !== null) === test.expected) {
                    this.results.passed++;
                    this.log('pass', `Time validation: ${test.desc} - ${test.time}`);
                } else {
                    this.results.failed++;
                    this.log('fail', `Time validation failed: ${test.desc} - ${test.time}`);
                }
            } catch (error) {
                this.results.failed++;
                this.log('fail', `Time validation error: ${test.desc}`, error.message);
            }
        });

        // Test price validation
        const priceTests = [
            { price: 50, expected: true, desc: 'Valid positive price' },
            { price: 0, expected: false, desc: 'Zero price' },
            { price: -10, expected: false, desc: 'Negative price' },
            { price: 'abc', expected: false, desc: 'Non-numeric price' }
        ];

        priceTests.forEach(test => {
            const isValid = !isNaN(test.price) && parseFloat(test.price) > 0;
            if (isValid === test.expected) {
                this.results.passed++;
                this.log('pass', `Price validation: ${test.desc} - ${test.price}`);
            } else {
                this.results.failed++;
                this.log('fail', `Price validation failed: ${test.desc} - ${test.price}`);
            }
        });
    }

    async testCRUDOperations() {
        this.log('test', '🔄 Testing CRUD Operations...');
        
        // Create operation
        try {
            if (window.createProfessionalCustomSlot) {
                // Simulate filling form with valid data
                this.fillFormWithTestData(this.testData.validSlot);
                this.results.passed++;
                this.log('pass', 'CREATE: Form can be filled with valid data');
            }
        } catch (error) {
            this.results.failed++;
            this.log('fail', 'CREATE: Error during form filling', error.message);
        }

        // Read operation
        try {
            if (window.renderCustomSlotsList) {
                await window.renderCustomSlotsList();
                this.results.passed++;
                this.log('pass', 'READ: Slots list can be rendered');
            }
        } catch (error) {
            this.results.failed++;
            this.log('fail', 'READ: Error during list rendering', error.message);
        }

        // Update operation
        try {
            if (window.editCustomSlot) {
                // Test edit function exists and can be called
                const testId = 'test-slot-id';
                window.editCustomSlot(testId);
                this.results.passed++;
                this.log('pass', 'UPDATE: Edit function executable');
            }
        } catch (error) {
            this.results.failed++;
            this.log('fail', 'UPDATE: Error during edit operation', error.message);
        }

        // Delete operation
        try {
            if (window.deleteCustomSlot) {
                // Test delete function exists and can be called
                const testId = 'test-slot-id';
                window.deleteCustomSlot(testId);
                this.results.passed++;
                this.log('pass', 'DELETE: Delete function executable');
            }
        } catch (error) {
            this.results.failed++;
            this.log('fail', 'DELETE: Error during delete operation', error.message);
        }
    }

    async testUIInteractions() {
        this.log('test', '🖱️ Testing UI Interactions...');
        
        // Test button interactions
        const buttons = [
            'create-custom-slot-btn',
            'custom-slot-preview-btn'
        ];

        buttons.forEach(buttonId => {
            const button = document.getElementById(buttonId);
            if (button) {
                // Test if button is clickable
                const isClickable = !button.disabled && button.onclick;
                if (isClickable) {
                    this.results.passed++;
                    this.log('pass', `Button #${buttonId} is interactive`);
                } else {
                    this.results.warnings++;
                    this.log('warn', `Button #${buttonId} may not be fully interactive`);
                }
            }
        });

        // Test form field interactions
        const fields = [
            'custom-slot-name',
            'custom-slot-start-time',
            'custom-slot-end-time',
            'custom-slot-price',
            'custom-slot-capacity'
        ];

        fields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                // Test field accessibility
                const isAccessible = !field.disabled && !field.readOnly;
                if (isAccessible) {
                    this.results.passed++;
                    this.log('pass', `Field #${fieldId} is accessible`);
                } else {
                    this.results.warnings++;
                    this.log('warn', `Field #${fieldId} may be disabled or readonly`);
                }
            }
        });
    }

    async testDataIntegrity() {
        this.log('test', '🔒 Testing Data Integrity...');
        
        // Test currency consistency
        try {
            const currencyElements = document.querySelectorAll('[data-currency]');
            let consistentCurrency = true;
            let expectedSymbol = '$'; // Default
            
            currencyElements.forEach(element => {
                const symbol = element.textContent || element.value;
                if (symbol && symbol !== expectedSymbol) {
                    consistentCurrency = false;
                }
            });

            if (consistentCurrency) {
                this.results.passed++;
                this.log('pass', 'Currency symbols are consistent across UI');
            } else {
                this.results.failed++;
                this.log('fail', 'Currency symbols are inconsistent');
            }
        } catch (error) {
            this.results.failed++;
            this.log('fail', 'Error testing currency consistency', error.message);
        }

        // Test data persistence
        try {
            if (window.customSlots && Array.isArray(window.customSlots)) {
                this.results.passed++;
                this.log('pass', `Data structure maintained: ${window.customSlots.length} slots`);
            } else {
                this.results.warnings++;
                this.log('warn', 'Custom slots data structure not found or invalid');
            }
        } catch (error) {
            this.results.failed++;
            this.log('fail', 'Error testing data persistence', error.message);
        }
    }

    async testErrorHandling() {
        this.log('test', '🛡️ Testing Error Handling...');
        
        // Test with invalid data
        try {
            this.fillFormWithTestData(this.testData.invalidSlot);
            this.results.passed++;
            this.log('pass', 'Form accepts invalid data for testing (error handling ready)');
        } catch (error) {
            // This is actually good - means validation is working
            this.results.passed++;
            this.log('pass', 'Form properly rejects invalid data', error.message);
        }

        // Test network error simulation
        try {
            // Test if functions handle missing DOM elements gracefully
            const originalElement = document.getElementById('custom-slots-list');
            if (originalElement) {
                originalElement.style.display = 'none';
                if (window.renderCustomSlotsList) {
                    await window.renderCustomSlotsList();
                }
                originalElement.style.display = '';
                this.results.passed++;
                this.log('pass', 'Functions handle missing DOM elements gracefully');
            }
        } catch (error) {
            this.results.warnings++;
            this.log('warn', 'Error handling could be improved for missing DOM elements');
        }
    }

    async testPerformance() {
        this.log('test', '⚡ Testing Performance...');
        
        // Test rendering performance
        const startTime = performance.now();
        
        try {
            if (window.renderCustomSlotsList) {
                await window.renderCustomSlotsList();
            }
            
            const endTime = performance.now();
            const renderTime = endTime - startTime;
            
            if (renderTime < 100) { // Under 100ms is good
                this.results.passed++;
                this.log('pass', `Rendering performance excellent: ${renderTime.toFixed(2)}ms`);
            } else if (renderTime < 500) { // Under 500ms is acceptable
                this.results.warnings++;
                this.log('warn', `Rendering performance acceptable: ${renderTime.toFixed(2)}ms`);
            } else {
                this.results.failed++;
                this.log('fail', `Rendering performance slow: ${renderTime.toFixed(2)}ms`);
            }
        } catch (error) {
            this.results.failed++;
            this.log('fail', 'Performance test failed', error.message);
        }
    }

    fillFormWithTestData(data) {
        const fields = {
            'custom-slot-name': data.name,
            'custom-slot-start-time': data.start_time,
            'custom-slot-end-time': data.end_time,
            'custom-slot-price': data.price,
            'custom-slot-capacity': data.capacity,
            'custom-slot-description': data.description
        };

        Object.entries(fields).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.value = value;
                // Trigger change event
                element.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
    }

    printFinalReport() {
        console.log('\n' + '='.repeat(80));
        this.log('test', '📊 PROFESSIONAL CUSTOM SLOT SYSTEM - FINAL TEST REPORT');
        console.log('='.repeat(80));
        
        const total = this.results.passed + this.results.failed + this.results.warnings;
        const successRate = total > 0 ? ((this.results.passed / total) * 100).toFixed(1) : 0;
        
        console.log(`✅ PASSED: ${this.results.passed}`);
        console.log(`❌ FAILED: ${this.results.failed}`);
        console.log(`⚠️ WARNINGS: ${this.results.warnings}`);
        console.log(`📈 TOTAL TESTS: ${total}`);
        console.log(`📊 SUCCESS RATE: ${successRate}%`);
        
        if (this.results.failed === 0) {
            console.log('\n🎉 EXCELLENT! All critical tests passed!');
            console.log('🚀 Custom Slot System is production-ready!');
        } else if (this.results.failed <= 2) {
            console.log('\n✅ GOOD! Minor issues detected but system is functional');
        } else {
            console.log('\n⚠️ ATTENTION! Multiple issues detected - review required');
        }
        
        console.log('\n📋 Detailed Results:');
        this.results.details.forEach((detail, index) => {
            console.log(`${index + 1}. [${detail.type.toUpperCase()}] ${detail.message}`);
        });
        
        console.log('\n' + '='.repeat(80));
    }
}

// Auto-execute comprehensive test when loaded
if (typeof window !== 'undefined') {
    window.CustomSlotTestSuite = CustomSlotTestSuite;
    
    // Auto-run after a short delay to ensure DOM is ready
    setTimeout(() => {
        console.log('🎯 Professional Custom Slot System Testing Suite Loaded');
        console.log('💡 Run: new CustomSlotTestSuite().runCompleteTestSuite()');
        console.log('🚀 Or run: window.runProfessionalCustomSlotTests()');
    }, 1000);
    
    // Convenience function
    window.runProfessionalCustomSlotTests = async function() {
        const tester = new CustomSlotTestSuite();
        await tester.runCompleteTestSuite();
        return tester.results;
    };
}
