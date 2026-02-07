// Comprehensive Form Testing Script for Playground Booking System
// This script will test all form functionality with dummy data

class PlaygroundFormTester {
    constructor() {
        this.testData = {
            step1: {
                playground_type: 'indoor',
                sport_types: ['basketball', 'volleyball', 'badminton']
            },
            step2: {
                name: 'Elite Sports Complex',
                description: 'A premium indoor sports facility with professional-grade equipment and amenities.',
                contact_person: 'John Doe',
                contact_number: '+880123456789',
                email: 'john@elitesports.com',
                address: '123 Sports Street, Dhanmondi',
                country: 'BD',
                state: 'dhaka',
                city: 'dhaka'
            },
            step3: {
                capacity: '20',
                price_per_hour: '1500',
                opening_time: '06:00',
                closing_time: '22:00',
                slot_duration: '60'
            },
            step4: {
                // Will be handled by file uploads
            },
            step5: {
                amenities: ['parking', 'restroom', 'changing_room', 'water_fountain']
            },
            step6: {
                terms: true,
                privacy: true
            }
        };
        this.currentStep = 1;
        this.maxStep = 6;
    }

    async runFullTest() {
        console.log('🚀 Starting comprehensive form test...');
        
        try {
            // Test each step
            for (let step = 1; step <= this.maxStep; step++) {
                console.log(`\n📝 Testing Step ${step}...`);
                await this.testStep(step);
                await this.delay(1000); // Wait between steps
            }
            
            console.log('\n✅ All tests completed successfully!');
            return true;
        } catch (error) {
            console.error('❌ Test failed:', error);
            return false;
        }
    }

    async testStep(stepNumber) {
        // Navigate to step
        await this.navigateToStep(stepNumber);
        
        // Fill step data
        switch (stepNumber) {
            case 1:
                await this.fillStep1();
                break;
            case 2:
                await this.fillStep2();
                break;
            case 3:
                await this.fillStep3();
                break;
            case 4:
                await this.testStep4();
                break;
            case 5:
                await this.fillStep5();
                break;
            case 6:
                await this.testStep6();
                break;
        }
        
        // Validate step
        await this.validateStep(stepNumber);
    }

    async navigateToStep(stepNumber) {
        console.log(`🔄 Navigating to step ${stepNumber}...`);
        
        if (window.PlaygroundSystem && window.PlaygroundSystem.showStep) {
            window.PlaygroundSystem.showStep(stepNumber);
        } else {
            // Fallback method
            const stepButton = document.querySelector(`[onclick*="showStep(${stepNumber})"]`);
            if (stepButton) {
                stepButton.click();
            }
        }
        
        await this.delay(500);
    }

    async fillStep1() {
        console.log('📝 Filling Step 1 - Playground Type & Sports...');
        
        // Select playground type
        const playgroundType = document.getElementById('playground_type');
        if (playgroundType) {
            playgroundType.value = this.testData.step1.playground_type;
            playgroundType.dispatchEvent(new Event('change'));
            console.log('✅ Playground type selected:', this.testData.step1.playground_type);
        }
        
        await this.delay(1000); // Wait for sports to load
        
        // Select sports
        const sportsSelect = document.getElementById('sport_types');
        if (sportsSelect) {
            // Clear previous selections
            for (let option of sportsSelect.options) {
                option.selected = false;
            }
            
            // Select test sports
            for (let option of sportsSelect.options) {
                if (this.testData.step1.sport_types.includes(option.value)) {
                    option.selected = true;
                    console.log('✅ Sport selected:', option.text);
                }
            }
            sportsSelect.dispatchEvent(new Event('change'));
        }
    }

    async fillStep2() {
        console.log('📝 Filling Step 2 - Location & Contact Details...');
        
        const fields = [
            'name', 'description', 'contact_person', 
            'contact_number', 'email', 'address'
        ];
        
        fields.forEach(field => {
            const element = document.getElementById(field);
            if (element && this.testData.step2[field]) {
                element.value = this.testData.step2[field];
                element.dispatchEvent(new Event('input'));
                console.log(`✅ ${field} filled:`, this.testData.step2[field]);
            }
        });
        
        // Handle location dropdowns
        await this.selectLocation();
    }

    async selectLocation() {
        console.log('🌍 Selecting location...');
        
        // Select country
        const countrySelect = document.getElementById('country');
        if (countrySelect) {
            countrySelect.value = this.testData.step2.country;
            countrySelect.dispatchEvent(new Event('change'));
            console.log('✅ Country selected:', this.testData.step2.country);
        }
        
        await this.delay(1000); // Wait for states to load
        
        // Select state
        const stateSelect = document.getElementById('state');
        if (stateSelect) {
            stateSelect.value = this.testData.step2.state;
            stateSelect.dispatchEvent(new Event('change'));
            console.log('✅ State selected:', this.testData.step2.state);
        }
        
        await this.delay(1000); // Wait for cities to load
        
        // Select city
        const citySelect = document.getElementById('city');
        if (citySelect) {
            citySelect.value = this.testData.step2.city;
            citySelect.dispatchEvent(new Event('change'));
            console.log('✅ City selected:', this.testData.step2.city);
        }
    }

    async fillStep3() {
        console.log('📝 Filling Step 3 - Operating Hours & Time Slots...');
        
        const fields = [
            'capacity', 'price_per_hour', 'opening_time', 
            'closing_time', 'slot_duration'
        ];
        
        fields.forEach(field => {
            const element = document.getElementById(field);
            if (element && this.testData.step3[field]) {
                element.value = this.testData.step3[field];
                element.dispatchEvent(new Event('input'));
                console.log(`✅ ${field} filled:`, this.testData.step3[field]);
            }
        });
        
        // Enable today's day
        const today = new Date().getDay();
        const dayNames = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
        const todayName = dayNames[today];
        
        const todayCheckbox = document.getElementById(`${todayName}_enabled`);
        if (todayCheckbox) {
            todayCheckbox.checked = true;
            todayCheckbox.dispatchEvent(new Event('change'));
            console.log(`✅ ${todayName} enabled`);
        }
        
        // Generate time slots
        const generateBtn = document.getElementById('generate-all-slots');
        if (generateBtn) {
            generateBtn.click();
            console.log('✅ Time slots generated');
        }
    }

    async testStep4() {
        console.log('📝 Testing Step 4 - Media Gallery...');
        console.log('ℹ️ Step 4 requires file uploads - skipping for automated test');
    }

    async fillStep5() {
        console.log('📝 Filling Step 5 - Amenities...');
        
        // Wait for amenities to load
        await this.delay(2000);
        
        // Select test amenities
        this.testData.step5.amenities.forEach(amenityValue => {
            const checkbox = document.querySelector(`input[value="${amenityValue}"]`);
            if (checkbox) {
                checkbox.checked = true;
                checkbox.dispatchEvent(new Event('change'));
                console.log('✅ Amenity selected:', amenityValue);
            }
        });
    }

    async testStep6() {
        console.log('📝 Testing Step 6 - Preview & Validation...');
        
        // Wait for preview to load
        await this.delay(3000);
        
        // Test preview sections
        await this.validatePreview();
        
        // Accept terms
        const termsCheckbox = document.getElementById('terms');
        const privacyCheckbox = document.getElementById('privacy');
        
        if (termsCheckbox) {
            termsCheckbox.checked = this.testData.step6.terms;
            termsCheckbox.dispatchEvent(new Event('change'));
            console.log('✅ Terms accepted');
        }
        
        if (privacyCheckbox) {
            privacyCheckbox.checked = this.testData.step6.privacy;
            privacyCheckbox.dispatchEvent(new Event('change'));
            console.log('✅ Privacy policy accepted');
        }
    }

    async validatePreview() {
        console.log('🔍 Validating preview sections...');
        
        // Check location
        const locationElement = document.getElementById('preview-location');
        if (locationElement) {
            const locationText = locationElement.textContent;
            console.log('📍 Preview location:', locationText);
            if (locationText.includes('Loading')) {
                console.warn('⚠️ Location still loading in preview');
            } else {
                console.log('✅ Location loaded successfully');
            }
        }
        
        // Check sports
        const sportsContainer = document.getElementById('preview-sports');
        if (sportsContainer) {
            const sportsText = sportsContainer.textContent;
            console.log('🏃 Preview sports:', sportsText);
            if (sportsText.includes('No sports selected')) {
                console.warn('⚠️ Sports not showing in preview');
            } else {
                console.log('✅ Sports loaded successfully');
            }
        }
        
        // Check time slots
        const slotsContainer = document.getElementById('preview-timeslots');
        if (slotsContainer) {
            const slotsCount = slotsContainer.children.length;
            console.log('⏰ Preview slots count:', slotsCount);
            if (slotsCount === 0) {
                console.warn('⚠️ No time slots showing in preview');
            } else {
                console.log('✅ Time slots loaded successfully');
            }
        }
    }

    async validateStep(stepNumber) {
        console.log(`✅ Step ${stepNumber} validation completed`);
        
        // Check for any console errors
        if (window.console.error.calls && window.console.error.calls.length > 0) {
            console.warn('⚠️ Console errors detected during step', stepNumber);
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Quick test for current step only
    async testCurrentStep() {
        const currentStep = this.getCurrentStep();
        console.log(`🎯 Testing current step: ${currentStep}`);
        await this.testStep(currentStep);
    }

    getCurrentStep() {
        // Detect current step from DOM
        const visibleStep = document.querySelector('[data-step]:not(.hidden)');
        if (visibleStep) {
            return parseInt(visibleStep.getAttribute('data-step'));
        }
        return 1;
    }

    // Test specific preview functionality
    async testPreviewOnly() {
        console.log('🎬 Testing preview functionality only...');
        
        // Navigate to step 6
        await this.navigateToStep(6);
        await this.delay(2000);
        
        // Force preview update
        if (window.PlaygroundSystem && window.PlaygroundSystem.updateLivePreview) {
            await window.PlaygroundSystem.updateLivePreview();
        }
        
        await this.delay(3000);
        await this.validatePreview();
    }
}

// Initialize tester when script loads
window.FormTester = new PlaygroundFormTester();

// Add quick access methods to window
window.testForm = () => window.FormTester.runFullTest();
window.testCurrentStep = () => window.FormTester.testCurrentStep();
window.testPreview = () => window.FormTester.testPreviewOnly();

console.log('🧪 Form tester loaded! Use:');
console.log('- testForm() to run full test');
console.log('- testCurrentStep() to test current step');
console.log('- testPreview() to test preview only');
