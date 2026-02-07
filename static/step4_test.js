// Step 4 Media Gallery Test Script
console.log('🧪 STEP 4 MEDIA GALLERY FUNCTIONALITY TEST');
console.log('==========================================');

function testStep4MediaGallery() {
    console.log('\n🎯 Testing Step 4 Media Gallery...');
    
    // Test 1: Check if PlaygroundSystemDebug exists
    console.log('\n1. Testing PlaygroundSystemDebug object...');
    if (window.PlaygroundSystemDebug) {
        console.log('✅ PlaygroundSystemDebug object found');
        
        // Test media gallery object
        if (window.PlaygroundSystemDebug.mediaGallery) {
            console.log('✅ Media Gallery object found');
            
            // Test initialization
            if (typeof window.PlaygroundSystemDebug.mediaGallery.init === 'function') {
                console.log('✅ Media Gallery init function found');
            } else {
                console.log('❌ Media Gallery init function NOT found');
            }
            
            // Test core functions
            const coreFunctions = [
                'setupCoverImages',
                'setupGalleryImages', 
                'handleCoverUpload',
                'handleGalleryUpload',
                'clearCoverImages',
                'clearGalleryImages',
                'processCoverImages',
                'processGalleryImages',
                'validateImageFile',
                'uploadToBackend',
                'updateCoverDisplay',
                'updateGalleryDisplay'
            ];
            
            console.log('\n2. Testing core media gallery functions...');
            coreFunctions.forEach(funcName => {
                if (typeof window.PlaygroundSystemDebug.mediaGallery[funcName] === 'function') {
                    console.log(`✅ ${funcName} function found`);
                } else {
                    console.log(`❌ ${funcName} function NOT found`);
                }
            });
            
        } else {
            console.log('❌ Media Gallery object NOT found');
        }
    } else {
        console.log('❌ PlaygroundSystemDebug object NOT found');
    }
    
    // Test 2: Check if main PlaygroundSystem has media gallery reference
    console.log('\n3. Testing PlaygroundSystem integration...');
    if (window.PlaygroundSystem && window.PlaygroundSystem.mediaGallery) {
        console.log('✅ PlaygroundSystem.mediaGallery connected');
    } else {
        console.log('❌ PlaygroundSystem.mediaGallery NOT connected');
    }
    
    // Test 3: Check DOM elements
    console.log('\n4. Testing Step 4 DOM elements...');
    const requiredElements = [
        'cover-images',
        'gallery-images', 
        'cover-upload-area',
        'gallery-upload-area',
        'cover-preview',
        'gallery-preview',
        'video-url',
        'virtual-tour-url'
    ];
    
    requiredElements.forEach(elementId => {
        const element = document.getElementById(elementId);
        if (element) {
            console.log(`✅ ${elementId} element found`);
        } else {
            console.log(`❌ ${elementId} element NOT found`);
        }
    });
    
    // Test 4: Check global test functions
    console.log('\n5. Testing global test functions...');
    if (typeof window.testFileUpload === 'function') {
        console.log('✅ testFileUpload function found');
    } else {
        console.log('❌ testFileUpload function NOT found');
    }
    
    if (typeof window.testMediaGallery === 'function') {
        console.log('✅ testMediaGallery function found');
    } else {
        console.log('❌ testMediaGallery function NOT found');
    }
    
    console.log('\n🎯 STEP 4 TEST COMPLETED!');
    console.log('==========================================');
    
    return {
        systemDebugExists: !!window.PlaygroundSystemDebug,
        mediaGalleryExists: !!(window.PlaygroundSystemDebug && window.PlaygroundSystemDebug.mediaGallery),
        playgroundSystemConnected: !!(window.PlaygroundSystem && window.PlaygroundSystem.mediaGallery),
        testFunctionsAvailable: !!(window.testFileUpload && window.testMediaGallery)
    };
}

// Auto-run test when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', testStep4MediaGallery);
} else {
    testStep4MediaGallery();
}
