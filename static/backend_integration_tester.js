/**
 * 🎯 BACKEND INTEGRATION & CUSTOM SLOT COMPREHENSIVE TESTING
 * Professional validation suite for all fixed functionalities
 * Date: August 13, 2025
 */

class BackendIntegrationTester {
    constructor() {
        this.results = {
            backendConnectivity: { passed: 0, failed: 0, tests: [] },
            sportTypesSync: { passed: 0, failed: 0, tests: [] },
            currencySystem: { passed: 0, failed: 0, tests: [] },
            customSlotSystem: { passed: 0, failed: 0, tests: [] },
            realTimeFeatures: { passed: 0, failed: 0, tests: [] }
        };
        
        this.startTime = Date.now();
    }

    async runAllTests() {
        console.log('🚀 COMPREHENSIVE BACKEND INTEGRATION & CUSTOM SLOT TESTING');
        console.log('═'.repeat(80));
        console.log('🕒 Test Started:', new Date().toLocaleString());
        console.log('═'.repeat(80));

        await this.testBackendConnectivity();
        await this.testSportTypesIntegration();
        await this.testCurrencySystem();
        await this.testCustomSlotSystem();
        await this.testRealTimeFeatures();
        await this.testErrorHandling();
        
        this.generateComprehensiveReport();
    }

    async testBackendConnectivity() {
        console.log('\n🌐 TESTING BACKEND CONNECTIVITY...');
        console.log('─'.repeat(50));

        // Test 1: Sport Types API
        await this.testApiEndpoint(
            '/api/sport-types/',
            'Sport Types API',
            'backendConnectivity'
        );

        // Test 2: Currency API
        await this.testApiEndpoint(
            '/api/currency/',
            'Currency API',
            'backendConnectivity'
        );

        // Test 3: Currency Detection API
        await this.testApiEndpoint(
            '/api/currency/detect/',
            'Currency Detection API',
            'backendConnectivity'
        );

        // Test 4: Dynamic Data Functions
        this.testFunction(
            'initializeDynamicBackend',
            'Dynamic Backend Initialization',
            'backendConnectivity'
        );
    }

    async testSportTypesIntegration() {
        console.log('\n🏅 TESTING SPORT TYPES INTEGRATION...');
        console.log('─'.repeat(50));

        // Test 1: Sport Types Loading
        this.testFunction(
            'loadSportTypes',
            'Sport Types Loading Function',
            'sportTypesSync'
        );

        // Test 2: Step 1 Sync
        this.testFunction(
            'syncSportTypesWithStep1',
            'Step 1 Synchronization',
            'sportTypesSync'
        );

        // Test 3: Fallback System
        this.testFunction(
            'populateSportTypesWithFallback',
            'Fallback Sport Types',
            'sportTypesSync'
        );

        // Test 4: Data Structure
        const sportTypesData = window.dynamicPlaygroundData?.sportTypes;
        this.logTest(
            'sportTypesSync',
            'Sport Types Data Structure',
            Array.isArray(sportTypesData) && sportTypesData.length > 0,
            { count: sportTypesData?.length || 0 }
        );

        // Test 5: Step 1 Integration
        const step1Data = window.sportTypesData;
        this.logTest(
            'sportTypesSync',
            'Step 1 Data Available',
            Array.isArray(step1Data) && step1Data.length > 0,
            { count: step1Data?.length || 0 }
        );
    }

    async testCurrencySystem() {
        console.log('\n💰 TESTING CURRENCY SYSTEM...');
        console.log('─'.repeat(50));

        // Test 1: Currency Loading
        this.testFunction(
            'loadCurrencies',
            'Currency Loading Function',
            'currencySystem'
        );

        // Test 2: Currency Detection
        this.testFunction(
            'detectUserCurrency',
            'Currency Detection Function',
            'currencySystem'
        );

        // Test 3: Currency Selection
        this.testFunction(
            'updateCurrencySelection',
            'Currency Selection Update',
            'currencySystem'
        );

        // Test 4: Currency Fallback
        this.testFunction(
            'populateCurrenciesWithFallback',
            'Currency Fallback System',
            'currencySystem'
        );

        // Test 5: Currency Sync with Main System
        const hasCurrencySystem = !!window.currencySystem;
        this.logTest(
            'currencySystem',
            'Main Currency System Available',
            hasCurrencySystem
        );

        // Test 6: Currency Display Elements
        const currencyElements = document.querySelectorAll('[data-currency], .currency-symbol');
        this.logTest(
            'currencySystem',
            'Currency Display Elements',
            currencyElements.length > 0,
            { count: currencyElements.length }
        );
    }

    async testCustomSlotSystem() {
        console.log('\n🎯 TESTING CUSTOM SLOT SYSTEM...');
        console.log('─'.repeat(50));

        // Test 1: Core Functions
        const customSlotFunctions = [
            'createProfessionalCustomSlot',
            'editCustomSlot', 
            'deleteCustomSlot',
            'duplicateCustomSlot',
            'renderCustomSlotsList',
            'updateCustomSlotPreview',
            'formatTime12Hour',
            'updateTotalRevenue'
        ];

        customSlotFunctions.forEach(funcName => {
            this.testFunction(funcName, `${funcName} Function`, 'customSlotSystem');
        });

        // Test 2: UI Elements
        const customSlotElements = [
            'custom-slots-list',
            'custom-slot-name',
            'custom-slot-start-time',
            'custom-slot-end-time',
            'custom-slot-price',
            'custom-slot-capacity',
            'create-custom-slot-btn'
        ];

        customSlotElements.forEach(elementId => {
            const element = document.getElementById(elementId);
            this.logTest(
                'customSlotSystem',
                `Element: ${elementId}`,
                !!element
            );
        });

        // Test 3: Time Format Validation
        if (window.formatTime12Hour) {
            const timeTests = [
                { input: '09:00', expected: '9:00 AM' },
                { input: '15:30', expected: '3:30 PM' },
                { input: '12:00', expected: '12:00 PM' },
                { input: '00:00', expected: '12:00 AM' }
            ];

            timeTests.forEach(test => {
                try {
                    const result = window.formatTime12Hour(test.input);
                    this.logTest(
                        'customSlotSystem',
                        `Time Format: ${test.input}`,
                        result === test.expected,
                        { input: test.input, expected: test.expected, actual: result }
                    );
                } catch (error) {
                    this.logTest(
                        'customSlotSystem',
                        `Time Format: ${test.input}`,
                        false,
                        { error: error.message }
                    );
                }
            });
        }

        // Test 4: Data Integration
        if (window.integrateCustomSlotsWithMainForm) {
            try {
                const result = window.integrateCustomSlotsWithMainForm();
                this.logTest(
                    'customSlotSystem',
                    'Main Form Integration',
                    typeof result === 'boolean',
                    { result }
                );
            } catch (error) {
                this.logTest(
                    'customSlotSystem',
                    'Main Form Integration',
                    false,
                    { error: error.message }
                );
            }
        }
    }

    async testRealTimeFeatures() {
        console.log('\n⚡ TESTING REAL-TIME FEATURES...');
        console.log('─'.repeat(50));

        // Test 1: Real-time Setup
        this.testFunction(
            'setupRealTimeUpdates',
            'Real-time Updates Setup',
            'realTimeFeatures'
        );

        // Test 2: Dynamic Data Object
        const hasDynamicData = !!window.dynamicPlaygroundData;
        this.logTest(
            'realTimeFeatures',
            'Dynamic Data Structure',
            hasDynamicData,
            window.dynamicPlaygroundData
        );

        // Test 3: Initialization Status
        const isInitialized = window.dynamicPlaygroundData?.isInitialized;
        this.logTest(
            'realTimeFeatures',
            'System Initialization',
            !!isInitialized
        );

        // Test 4: Event Listeners
        const currencySelector = document.getElementById('currency');
        if (currencySelector) {
            this.logTest(
                'realTimeFeatures',
                'Currency Selector Event Binding',
                currencySelector.onchange !== null
            );
        }
    }

    async testErrorHandling() {
        console.log('\n🛡️ TESTING ERROR HANDLING...');
        console.log('─'.repeat(50));

        // Test 1: Fallback Systems
        this.testFunction(
            'initializeFallbackSystems',
            'Fallback Systems',
            'realTimeFeatures'
        );

        // Test 2: Data Structure Validation
        this.testFunction(
            'ensureDataStructures',
            'Data Structure Validation',
            'realTimeFeatures'
        );

        // Test 3: Final Validation
        this.testFunction(
            'performFinalValidation',
            'Final Validation',
            'realTimeFeatures'
        );
    }

    async testApiEndpoint(url, name, category) {
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            this.logTest(
                category,
                `${name} Connectivity`,
                response.status < 500,
                { status: response.status, url }
            );

            if (response.ok) {
                try {
                    const data = await response.json();
                    this.logTest(
                        category,
                        `${name} Data Format`,
                        typeof data === 'object',
                        { hasData: !!data }
                    );
                } catch (parseError) {
                    this.logTest(
                        category,
                        `${name} Data Format`,
                        false,
                        { error: 'Invalid JSON response' }
                    );
                }
            }
        } catch (error) {
            this.logTest(
                category,
                `${name} Connectivity`,
                false,
                { error: error.message }
            );
        }
    }

    testFunction(funcName, testName, category) {
        const func = window[funcName];
        const exists = func && typeof func === 'function';
        
        this.logTest(category, testName, exists, {
            type: typeof func,
            exists: !!func
        });

        return exists;
    }

    logTest(category, testName, passed, details = null) {
        const icon = passed ? '✅' : '❌';
        const message = `${icon} ${testName}`;
        
        console.log(message);
        if (details) {
            console.log('   📋 Details:', details);
        }

        if (passed) {
            this.results[category].passed++;
        } else {
            this.results[category].failed++;
        }

        this.results[category].tests.push({
            name: testName,
            passed,
            details,
            timestamp: new Date().toISOString()
        });
    }

    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    generateComprehensiveReport() {
        const endTime = Date.now();
        const duration = ((endTime - this.startTime) / 1000).toFixed(2);

        console.log('\n' + '═'.repeat(80));
        console.log('📊 COMPREHENSIVE TEST REPORT - BACKEND INTEGRATION & CUSTOM SLOTS');
        console.log('═'.repeat(80));
        console.log(`🕒 Test Duration: ${duration} seconds`);
        console.log(`📅 Completed: ${new Date().toLocaleString()}`);

        let totalPassed = 0;
        let totalFailed = 0;

        Object.entries(this.results).forEach(([category, results]) => {
            totalPassed += results.passed;
            totalFailed += results.failed;
            
            const categoryTotal = results.passed + results.failed;
            const categoryRate = categoryTotal > 0 ? 
                ((results.passed / categoryTotal) * 100).toFixed(1) : 0;

            console.log(`\n🔸 ${category.toUpperCase()}`);
            console.log(`   ✅ Passed: ${results.passed}`);
            console.log(`   ❌ Failed: ${results.failed}`);
            console.log(`   📊 Success Rate: ${categoryRate}%`);
        });

        const overallTotal = totalPassed + totalFailed;
        const overallRate = overallTotal > 0 ? 
            ((totalPassed / overallTotal) * 100).toFixed(1) : 0;

        console.log(`\n📈 OVERALL SUMMARY:`);
        console.log(`   ✅ Total Passed: ${totalPassed}`);
        console.log(`   ❌ Total Failed: ${totalFailed}`);
        console.log(`   📊 Overall Success Rate: ${overallRate}%`);

        // Assessment
        if (overallRate >= 95) {
            console.log(`\n🎉 EXCELLENT! System is performing exceptionally well!`);
            console.log(`🚀 All backend integrations and custom slot features are operational!`);
        } else if (overallRate >= 85) {
            console.log(`\n✅ GOOD! System is working well with minor areas for improvement.`);
        } else if (overallRate >= 70) {
            console.log(`\n⚠️ FAIR! System needs attention in several areas.`);
        } else {
            console.log(`\n❌ POOR! System requires significant improvements.`);
        }

        // Specific Recommendations
        console.log(`\n💡 RECOMMENDATIONS:`);
        
        if (this.results.backendConnectivity.failed > 0) {
            console.log(`   🌐 Check backend API endpoints and server connectivity`);
        }
        
        if (this.results.sportTypesSync.failed > 0) {
            console.log(`   🏅 Verify sport types data structure and Step 1 integration`);
        }
        
        if (this.results.currencySystem.failed > 0) {
            console.log(`   💰 Review currency system configuration and API responses`);
        }
        
        if (this.results.customSlotSystem.failed > 0) {
            console.log(`   🎯 Validate custom slot functions and UI elements`);
        }
        
        if (this.results.realTimeFeatures.failed > 0) {
            console.log(`   ⚡ Check real-time update mechanisms and event handling`);
        }

        console.log('\n' + '═'.repeat(80));
        
        return {
            summary: {
                totalPassed,
                totalFailed,
                overallRate: parseFloat(overallRate),
                duration: parseFloat(duration)
            },
            categories: this.results
        };
    }
}

// Global access and auto-execution
if (typeof window !== 'undefined') {
    window.BackendIntegrationTester = BackendIntegrationTester;
    
    window.runBackendIntegrationTests = async function() {
        const tester = new BackendIntegrationTester();
        return await tester.runAllTests();
    };

    // Auto-run after a delay to ensure everything is loaded
    setTimeout(() => {
        console.log('🎯 Backend Integration & Custom Slot Tester loaded!');
        console.log('💡 Run: window.runBackendIntegrationTests()');
        console.log('🚀 Starting automatic comprehensive testing in 3 seconds...');
        
        setTimeout(async () => {
            try {
                await window.runBackendIntegrationTests();
            } catch (error) {
                console.error('❌ Testing failed:', error);
            }
        }, 3000);
    }, 1000);
}
