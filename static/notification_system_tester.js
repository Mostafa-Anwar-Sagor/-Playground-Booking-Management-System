/**
 * 🎯 NOTIFICATION SYSTEM TESTING SCRIPT
 * Professional validation of the enhanced notification system
 */

class NotificationSystemTester {
    constructor() {
        this.testResults = [];
    }

    async runAllTests() {
        console.log('🚀 TESTING PROFESSIONAL NOTIFICATION SYSTEM');
        console.log('═'.repeat(60));
        
        this.testBasicFunctionality();
        this.testPositioning();
        this.testMultipleNotifications();
        this.testNotificationTypes();
        this.testCloseButton();
        this.testAutoHide();
        
        this.generateReport();
    }

    testBasicFunctionality() {
        console.log('\n📋 Testing Basic Functionality...');
        
        try {
            // Test if notification manager exists
            const hasManager = !!window.notificationManager;
            this.logTest('Notification Manager Exists', hasManager);
            
            // Test if global showNotification function exists
            const hasGlobalFunction = typeof window.showNotification === 'function';
            this.logTest('Global showNotification Function', hasGlobalFunction);
            
            // Test notification creation
            if (hasGlobalFunction) {
                const notification = window.showNotification('Test notification', 'info', 1000);
                this.logTest('Notification Creation', !!notification);
            }
            
        } catch (error) {
            this.logTest('Basic Functionality', false, error.message);
        }
    }

    testPositioning() {
        console.log('\n📍 Testing Positioning...');
        
        try {
            // Create a test notification
            const notification = window.showNotification('Position test notification', 'info', 2000);
            
            setTimeout(() => {
                const notificationElement = document.querySelector('.professional-notification');
                if (notificationElement) {
                    const computedStyle = window.getComputedStyle(notificationElement);
                    const top = computedStyle.top;
                    const right = computedStyle.right;
                    
                    // Check if positioned correctly (should be calc(4rem + 10px))
                    const correctTop = top.includes('calc') || top === '74px'; // 4rem (64px) + 10px = 74px
                    const correctRight = right === '20px';
                    
                    this.logTest('Correct Top Position (below navbar)', correctTop, `Top: ${top}`);
                    this.logTest('Correct Right Position', correctRight, `Right: ${right}`);
                    
                    // Test z-index
                    const zIndex = parseInt(computedStyle.zIndex);
                    this.logTest('Proper Z-Index (≥1000)', zIndex >= 1000, `Z-Index: ${zIndex}`);
                    
                } else {
                    this.logTest('Notification Element Found', false);
                }
            }, 200);
            
        } catch (error) {
            this.logTest('Positioning Test', false, error.message);
        }
    }

    testMultipleNotifications() {
        console.log('\n📚 Testing Multiple Notifications...');
        
        try {
            // Clear existing notifications
            if (window.notificationManager) {
                window.notificationManager.clear();
            }
            
            // Create multiple notifications
            window.showNotification('First notification', 'info', 3000);
            
            setTimeout(() => {
                window.showNotification('Second notification', 'success', 3000);
            }, 100);
            
            setTimeout(() => {
                window.showNotification('Third notification', 'warning', 3000);
            }, 200);
            
            setTimeout(() => {
                const notifications = document.querySelectorAll('.professional-notification');
                this.logTest('Multiple Notifications Created', notifications.length >= 2, `Count: ${notifications.length}`);
                
                if (notifications.length >= 2) {
                    // Check stacking
                    const firstTop = window.getComputedStyle(notifications[0]).top;
                    const secondTop = window.getComputedStyle(notifications[1]).top;
                    
                    this.logTest('Notifications Stack Properly', firstTop !== secondTop, 
                        `First: ${firstTop}, Second: ${secondTop}`);
                }
            }, 500);
            
        } catch (error) {
            this.logTest('Multiple Notifications Test', false, error.message);
        }
    }

    testNotificationTypes() {
        console.log('\n🎨 Testing Notification Types...');
        
        const types = ['success', 'error', 'warning', 'info'];
        
        types.forEach((type, index) => {
            setTimeout(() => {
                try {
                    window.showNotification(`Test ${type} notification`, type, 2000);
                    
                    setTimeout(() => {
                        const notification = document.querySelector('.professional-notification:last-child');
                        if (notification) {
                            const hasGradient = notification.style.background.includes('gradient');
                            this.logTest(`${type} Notification Styling`, hasGradient, 
                                `Background: ${notification.style.background.substring(0, 50)}...`);
                        }
                    }, 100);
                    
                } catch (error) {
                    this.logTest(`${type} Notification`, false, error.message);
                }
            }, index * 300);
        });
    }

    testCloseButton() {
        console.log('\n❌ Testing Close Button...');
        
        try {
            const notification = window.showNotification('Test close button', 'info', 5000);
            
            setTimeout(() => {
                const notificationElement = document.querySelector('.professional-notification:last-child');
                if (notificationElement) {
                    const closeButton = notificationElement.querySelector('button');
                    const hasCloseButton = !!closeButton;
                    
                    this.logTest('Close Button Exists', hasCloseButton);
                    
                    if (hasCloseButton) {
                        // Test close button functionality
                        closeButton.click();
                        
                        setTimeout(() => {
                            const stillExists = document.body.contains(notificationElement);
                            this.logTest('Close Button Works', !stillExists);
                        }, 400);
                    }
                }
            }, 200);
            
        } catch (error) {
            this.logTest('Close Button Test', false, error.message);
        }
    }

    testAutoHide() {
        console.log('\n⏰ Testing Auto-Hide...');
        
        try {
            const notification = window.showNotification('Auto-hide test', 'info', 1000);
            
            setTimeout(() => {
                const notificationElement = document.querySelector('.professional-notification:last-child');
                if (notificationElement) {
                    this.logTest('Notification Initially Visible', true);
                    
                    setTimeout(() => {
                        const stillVisible = document.body.contains(notificationElement);
                        this.logTest('Auto-Hide Works', !stillVisible);
                    }, 1200);
                }
            }, 200);
            
        } catch (error) {
            this.logTest('Auto-Hide Test', false, error.message);
        }
    }

    logTest(testName, passed, details = null) {
        const icon = passed ? '✅' : '❌';
        const message = `${icon} ${testName}`;
        
        console.log(message);
        if (details) {
            console.log(`   📋 Details: ${details}`);
        }

        this.testResults.push({
            name: testName,
            passed,
            details,
            timestamp: new Date().toISOString()
        });
    }

    generateReport() {
        setTimeout(() => {
            console.log('\n' + '═'.repeat(60));
            console.log('📊 NOTIFICATION SYSTEM TEST REPORT');
            console.log('═'.repeat(60));

            const totalTests = this.testResults.length;
            const passedTests = this.testResults.filter(test => test.passed).length;
            const failedTests = totalTests - passedTests;
            const successRate = totalTests > 0 ? ((passedTests / totalTests) * 100).toFixed(1) : 0;

            console.log(`\n📈 SUMMARY:`);
            console.log(`   ✅ Passed: ${passedTests}`);
            console.log(`   ❌ Failed: ${failedTests}`);
            console.log(`   📊 Success Rate: ${successRate}%`);

            if (successRate >= 90) {
                console.log(`\n🎉 EXCELLENT! Notification system is working perfectly!`);
                console.log(`✅ Positioned 10px below navbar as requested`);
                console.log(`✅ Professional styling and functionality`);
                console.log(`✅ Multiple notification support with proper stacking`);
            } else if (successRate >= 75) {
                console.log(`\n✅ GOOD! Notification system is mostly working well.`);
            } else {
                console.log(`\n⚠️ NEEDS ATTENTION! Some notification features need improvement.`);
            }

            console.log('\n' + '═'.repeat(60));
        }, 3000); // Wait for all async tests to complete
    }
}

// Global access and auto-execution
if (typeof window !== 'undefined') {
    window.NotificationSystemTester = NotificationSystemTester;
    
    window.testNotificationSystem = function() {
        const tester = new NotificationSystemTester();
        return tester.runAllTests();
    };

    // Auto-run after page load
    setTimeout(() => {
        console.log('🎯 Notification System Tester loaded!');
        console.log('💡 Run: window.testNotificationSystem()');
        console.log('🚀 Starting automatic testing in 2 seconds...');
        
        setTimeout(() => {
            try {
                window.testNotificationSystem();
            } catch (error) {
                console.error('❌ Testing failed:', error);
            }
        }, 2000);
    }, 1000);
}
