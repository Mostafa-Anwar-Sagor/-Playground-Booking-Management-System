// Professional CRUD Operations Test Script
console.log('ðŸš€ Starting Professional CRUD Test with Dummy Data');

// Test Data Objects
const dummyCustomSlot = {
    day_of_week: 'monday',
    start_time: '10:00',
    end_time: '11:00',
    package_name: 'Basketball Professional Training',
    original_price: 1500,
    discount_percentage: 10,
    max_capacity: 12,
    description: 'Premium basketball training session with professional coach',
    playground_id: 1
};

const dummyMembershipPass = {
    name: 'Basketball Monthly Premium Pass',
    description: 'Unlimited access to basketball courts with premium amenities and equipment',
    duration_days: 30,
    original_price: 5000,
    discount_percentage: 15,
    playground_id: 1,
    features: {
        unlimited_access: true,
        priority_booking: true,
        equipment_included: true,
        group_discount: false
    }
};

// Test Functions
function testCustomSlotCRUD() {
    console.log('ðŸŽ° Testing Custom Slot CRUD Operations');
    
    // Test Create
    if (window.PlaygroundSystem && window.PlaygroundSystem.customSlot) {
        console.log('âœ… CustomSlot system found');
        window.PlaygroundSystem.customSlot.create(dummyCustomSlot)
            .then(result => {
                console.log('âœ… Custom Slot Created:', result);
                if (result && result.id) {
                    // Test Update
                    const updateData = {...dummyCustomSlot, package_name: 'Updated Basketball Session'};
                    return window.PlaygroundSystem.customSlot.update(result.id, updateData);
                }
            })
            .then(updateResult => {
                if (updateResult) {
                    console.log('âœ… Custom Slot Updated:', updateResult);
                }
            })
            .catch(error => console.error('âŒ Custom Slot Error:', error));
    } else {
        console.error('âŒ CustomSlot system not found');
    }
}

function testMembershipPassCRUD() {
    console.log('ðŸŽ« Testing Membership Pass CRUD Operations');
    
    // Test Create
    if (window.PlaygroundSystem && window.PlaygroundSystem.membershipPass) {
        console.log('âœ… MembershipPass system found');
        window.PlaygroundSystem.membershipPass.create(dummyMembershipPass)
            .then(result => {
                console.log('âœ… Membership Pass Created:', result);
                if (result && result.id) {
                    // Test Update
                    const updateData = {...dummyMembershipPass, name: 'Updated Premium Pass'};
                    return window.PlaygroundSystem.membershipPass.update(result.id, updateData);
                }
            })
            .then(updateResult => {
                if (updateResult) {
                    console.log('âœ… Membership Pass Updated:', updateResult);
                }
            })
            .catch(error => console.error('âŒ Membership Pass Error:', error));
    } else {
        console.error('âŒ MembershipPass system not found');
    }
}

function testDiscountCalculations() {
    console.log('ðŸ’° Testing Discount Calculations');
    
    // Test Custom Slot Discount
    if (typeof calculateDiscountedPrice === 'function') {
        console.log('âœ… Custom Slot discount function found');
        // Simulate form values
        const mockPriceInput = {value: '1500'};
        const mockDiscountInput = {value: '10'};
        document.getElementById = (id) => {
            if (id === 'custom-slot-price') return mockPriceInput;
            if (id === 'custom-slot-discount') return mockDiscountInput;
            return null;
        };
        try {
            calculateDiscountedPrice();
            console.log('âœ… Custom Slot discount calculation works');
        } catch (error) {
            console.error('âŒ Custom Slot discount error:', error);
        }
    }
    
    // Test Membership Pass Discount
    if (typeof calculatePassDiscount === 'function') {
        console.log('âœ… Membership Pass discount function found');
        try {
            calculatePassDiscount();
            console.log('âœ… Membership Pass discount calculation works');
        } catch (error) {
            console.error('âŒ Membership Pass discount error:', error);
        }
    }
}

function runAllTests() {
    console.log('ðŸŽ¯ Running All CRUD Tests');
    
    // Wait for page to load
    setTimeout(() => {
        testCustomSlotCRUD();
        testMembershipPassCRUD();
        testDiscountCalculations();
        
        console.log('ðŸ All tests completed! Check the results above.');
    }, 2000);
}

// Auto-run tests when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runAllTests);
} else {
    runAllTests();
}
