// Quick Test Script for Playground Form
function quickFillForm() {
    console.log('🚀 Quick filling form with test data...');
    
    // Step 1: Playground Type & Sports
    setTimeout(() => {
        const playgroundType = document.getElementById('playground_type');
        if (playgroundType) {
            playgroundType.value = 'indoor';
            playgroundType.dispatchEvent(new Event('change'));
            console.log('✅ Playground type set to indoor');
        }
    }, 500);
    
    setTimeout(() => {
        const sportsSelect = document.getElementById('sport_types');
        if (sportsSelect && sportsSelect.options.length > 1) {
            // Select first available sport
            for (let i = 1; i < Math.min(4, sportsSelect.options.length); i++) {
                sportsSelect.options[i].selected = true;
            }
            sportsSelect.dispatchEvent(new Event('change'));
            console.log('✅ Sports selected');
        }
    }, 2000);
    
    // Step 2: Basic Info
    setTimeout(() => {
        const fields = {
            'name': 'Elite Sports Complex',
            'description': 'A premium indoor sports facility with state-of-the-art equipment and professional amenities.',
            'contact_person': 'John Doe',
            'contact_number': '+880123456789',
            'email': 'john@elitesports.com',
            'address': '123 Sports Street, Dhanmondi, Dhaka'
        };
        
        Object.entries(fields).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.value = value;
                element.dispatchEvent(new Event('input'));
            }
        });
        
        console.log('✅ Basic info filled');
    }, 3000);
    
    // Location selection
    setTimeout(() => {
        const countrySelect = document.getElementById('country');
        if (countrySelect) {
            // Look for Bangladesh
            for (let option of countrySelect.options) {
                if (option.text.includes('Bangladesh') || option.value === 'BD') {
                    countrySelect.value = option.value;
                    countrySelect.dispatchEvent(new Event('change'));
                    console.log('✅ Country selected: Bangladesh');
                    break;
                }
            }
        }
    }, 4000);
    
    setTimeout(() => {
        const stateSelect = document.getElementById('state');
        if (stateSelect && stateSelect.options.length > 1) {
            // Select Dhaka division
            for (let option of stateSelect.options) {
                if (option.text.includes('Dhaka')) {
                    stateSelect.value = option.value;
                    stateSelect.dispatchEvent(new Event('change'));
                    console.log('✅ State selected: Dhaka');
                    break;
                }
            }
        }
    }, 5000);
    
    setTimeout(() => {
        const citySelect = document.getElementById('city');
        if (citySelect && citySelect.options.length > 1) {
            // Select Dhaka city
            for (let option of citySelect.options) {
                if (option.text.includes('Dhaka')) {
                    citySelect.value = option.value;
                    citySelect.dispatchEvent(new Event('change'));
                    console.log('✅ City selected: Dhaka');
                    break;
                }
            }
        }
    }, 6000);
    
    // Step 3: Operating details
    setTimeout(() => {
        const fields = {
            'capacity': '20',
            'price_per_hour': '1500',
            'opening_time': '06:00',
            'closing_time': '22:00',
            'slot_duration': '60'
        };
        
        Object.entries(fields).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.value = value;
                element.dispatchEvent(new Event('input'));
            }
        });
        
        // Enable today
        const today = new Date().getDay();
        const dayNames = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
        const todayName = dayNames[today];
        
        const todayCheckbox = document.getElementById(`${todayName}_enabled`);
        if (todayCheckbox) {
            todayCheckbox.checked = true;
            todayCheckbox.dispatchEvent(new Event('change'));
        }
        
        console.log('✅ Operating details filled');
    }, 7000);
    
    // Generate slots
    setTimeout(() => {
        const generateBtn = document.getElementById('generate-all-slots');
        if (generateBtn) {
            generateBtn.click();
            console.log('✅ Time slots generated');
        }
    }, 8000);
    
    console.log('⏱️ Form filling in progress... Check console for updates');
}

// Auto-run if on localhost
if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
    // Add fill button
    document.addEventListener('DOMContentLoaded', () => {
        const fillBtn = document.createElement('button');
        fillBtn.innerHTML = '🎯 Fill Test Data';
        fillBtn.style.cssText = `
            position: fixed;
            top: 50px;
            right: 10px;
            z-index: 10000;
            background: #3b82f6;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        `;
        fillBtn.onclick = quickFillForm;
        document.body.appendChild(fillBtn);
    });
}

// Export for manual use
window.quickFillForm = quickFillForm;
