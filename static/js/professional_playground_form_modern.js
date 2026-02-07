/**
 * Professional Playground Form Manager - ULTRA MODERN VERSION
 * Advanced real-time booking system with dynamic slots and professional design
 */

// 🔧 Debug mode for troubleshooting
console.log('🔧 Professional Playground Form Script Loading...');

class ProfessionalPlaygroundForm {
    constructor() {
        console.log('🚀 Initializing Professional Playground Form...');
        
        // Validate environment
        if (typeof document === 'undefined') {
            console.error('❌ Document not available - running in non-browser environment');
            return;
        }
        
        console.log('✅ Environment validated - browser detected');
        
        this.currentStep = 1;
        this.totalSteps = 5;
        this.coverImages = [];
        this.galleryImages = [];
        this.sliderInterval = null;
        this.currentSlideIndex = 0;
        this.autoPlayInterval = 5000;
        this.isSliderPaused = false;
        
        // Real-time booking system
        this.timeSlots = [];
        this.bookingData = new Map();
        this.realTimeUpdates = true;
        this.websocket = null;
        
        // Advanced availability system
        this.availabilityColors = {
            available: '#10b981',
            booked: '#ef4444',
            pending: '#f59e0b',
            blocked: '#6b7280',
            premium: '#8b5cf6'
        };
        
        // Form state management
        this.formData = {};
        this.validationRules = {};
        this.autoSaveEnabled = true;
        
        // Initialize after all properties are set
        console.log('✅ Properties initialized - starting component setup');
        this.init();
    }

    init() {
        console.log('🚀 Initializing Ultra Modern Playground Form...');
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeComponents());
        } else {
            this.initializeComponents();
        }
    }

    initializeComponents() {
        console.log('🔧 Setting up all components...');
        
        try {
            // Core setup
            this.setupEventListeners();
            this.initializeFormValidation();
            this.initializeStepNavigation();
            this.setupImageUpload();
            this.setupRealTimeBooking();
            
            // External services (with error handling)
            try {
                this.initializeGoogleMaps();
            } catch (error) {
                console.warn('⚠️ Google Maps initialization failed:', error);
            }
            
            try {
                this.setupWebSocketConnection();
            } catch (error) {
                console.warn('⚠️ WebSocket setup failed:', error);
            }
            
            // Load any existing data
            this.loadDraftData();
            
            // Start real-time updates
            this.startRealTimeUpdates();
            
            console.log('✅ Ultra Modern Playground Form ready!');
            this.showNotification('🎯 Professional form loaded successfully!', 'success');
        } catch (error) {
            console.error('❌ Error during component initialization:', error);
            this.showNotification('⚠️ Some features may not work properly', 'warning');
        }
    }

    setupEventListeners() {
        console.log('🔗 Setting up modern event listeners...');
        
        // Global click handler with improved targeting
        document.addEventListener('click', (e) => {
            const target = e.target;
            const closest = (selector) => target.closest(selector);
            
            // Navigation buttons - FIXED SELECTORS
            if (closest('#next-step') || target.id === 'next-step') {
                e.preventDefault();
                this.nextStep();
                return;
            }
            
            if (closest('#prev-step') || target.id === 'prev-step') {
                e.preventDefault();
                this.prevStep();
                return;
            }
            
            if (closest('#submit-form') || target.id === 'submit-form') {
                e.preventDefault();
                this.submitForm();
                return;
            }
            
            // Image upload areas - FIXED SELECTORS
            if (closest('#main-image-upload') || closest('.image-upload-area[data-target="main"]')) {
                e.preventDefault();
                this.triggerImageUpload('main-image-input');
                return;
            }
            
            if (closest('#gallery-upload') || closest('.image-upload-area[data-target="gallery"]')) {
                e.preventDefault();
                this.triggerImageUpload('gallery-input');
                return;
            }
            
            // Time slots generation - FIXED SELECTORS
            if (closest('#generate-time-slots') || target.id === 'generate-time-slots') {
                e.preventDefault();
                this.generateAdvancedTimeSlots();
                return;
            }
            
            // Location buttons - FIXED SELECTORS
            if (closest('#search-location-btn') || target.id === 'search-location-btn') {
                e.preventDefault();
                this.searchOnMap();
                return;
            }
            
            // Draft management
            if (closest('#save-draft') || target.id === 'save-draft') {
                e.preventDefault();
                this.saveDraft();
                return;
            }
            
            if (closest('#load-draft') || target.id === 'load-draft') {
                e.preventDefault();
                this.loadDraft();
                return;
            }
        });

        // Enhanced input handlers for real-time updates
        document.addEventListener('input', (e) => {
            if (e.target.closest('#professionalPlaygroundForm')) {
                this.handleFormInput(e.target);
                if (this.autoSaveEnabled) {
                    this.debouncedSave();
                }
            }
        });

        // Form change handlers
        document.addEventListener('change', (e) => {
            if (e.target.matches('#price_per_hour, #opening_time, #closing_time')) {
                this.updatePricingAndSlots();
            }
        });

        console.log('✅ Modern event listeners configured');
    }

    // MODERN STEP NAVIGATION SYSTEM
    initializeStepNavigation() {
        console.log('🔄 Initializing step navigation...');
        this.updateStepDisplay();
        this.updateNavigationButtons();
    }

    nextStep() {
        console.log(`➡️ Attempting to move from step ${this.currentStep} to ${this.currentStep + 1}`);
        
        if (!this.validateCurrentStep()) {
            this.showNotification('Please complete all required fields', 'error');
            return;
        }
        
        if (this.currentStep < this.totalSteps) {
            this.currentStep++;
            this.updateStepDisplay();
            this.updateNavigationButtons();
            this.saveDraft();
            this.showNotification(`Advanced to step ${this.currentStep}`, 'success');
            
            // Trigger step-specific actions
            this.onStepChange(this.currentStep);
        }
    }

    prevStep() {
        console.log(`⬅️ Moving back from step ${this.currentStep} to ${this.currentStep - 1}`);
        
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateStepDisplay();
            this.updateNavigationButtons();
        }
    }

    updateStepDisplay() {
        // Hide all steps
        for (let i = 1; i <= this.totalSteps; i++) {
            const stepElement = document.querySelector(`[data-step="${i}"]`);
            if (stepElement) {
                stepElement.classList.remove('active');
                stepElement.style.display = 'none';
            }
        }
        
        // Show current step
        const currentStepElement = document.querySelector(`[data-step="${this.currentStep}"]`);
        if (currentStepElement) {
            currentStepElement.classList.add('active');
            currentStepElement.style.display = 'block';
        }
        
        // Update progress indicators
        document.querySelectorAll('.step-indicator').forEach((indicator, index) => {
            const stepNum = index + 1;
            indicator.classList.toggle('active', stepNum <= this.currentStep);
        });
        
        // Update step info
        const stepInfo = document.getElementById('currentStepInfo');
        if (stepInfo) {
            const stepNames = [
                'Basic Information',
                'Location & Contact', 
                'Operating Hours & Time Slots',
                'Images & Media',
                'Facilities & Final Review'
            ];
            stepInfo.textContent = `Step ${this.currentStep} of ${this.totalSteps}: ${stepNames[this.currentStep - 1]}`;
        }
        
        console.log(`✅ Updated display for step ${this.currentStep}`);
    }

    updateNavigationButtons() {
        const prevBtn = document.getElementById('prev-step');
        const nextBtn = document.getElementById('next-step');
        const submitBtn = document.getElementById('submit-form');
        
        if (prevBtn) {
            prevBtn.style.display = this.currentStep > 1 ? 'inline-flex' : 'none';
        }
        
        if (nextBtn) {
            nextBtn.style.display = this.currentStep < this.totalSteps ? 'inline-flex' : 'none';
        }
        
        if (submitBtn) {
            submitBtn.style.display = this.currentStep === this.totalSteps ? 'inline-flex' : 'none';
        }
    }

    onStepChange(step) {
        switch(step) {
            case 3:
                this.generateAdvancedTimeSlots();
                break;
            case 4:
                this.initializeImageUploads();
                break;
            case 5:
                this.generateFinalPreview();
                break;
        }
    }

    // ADVANCED REAL-TIME BOOKING SYSTEM
    setupRealTimeBooking() {
        console.log('⚡ Setting up real-time booking system...');
        
        // Initialize booking calendar
        this.bookingCalendar = new Map();
        
        // Set up real-time price updates
        this.priceUpdateInterval = setInterval(() => {
            this.updateDynamicPricing();
        }, 30000); // Update every 30 seconds
        
        // Initialize availability checker
        this.availabilityChecker = setInterval(() => {
            this.checkRealTimeAvailability();
        }, 10000); // Check every 10 seconds
    }

    setupWebSocketConnection() {
        // Mock WebSocket for real-time updates
        console.log('🔌 Setting up WebSocket connection...');
        
        // Simulate real-time booking updates
        this.mockRealTimeUpdates();
    }

    mockRealTimeUpdates() {
        setInterval(() => {
            if (this.timeSlots.length > 0 && this.realTimeUpdates) {
                // Randomly update slot status
                const randomSlot = this.timeSlots[Math.floor(Math.random() * this.timeSlots.length)];
                if (Math.random() > 0.95) { // 5% chance
                    const statuses = ['available', 'booked', 'pending'];
                    randomSlot.status = statuses[Math.floor(Math.random() * statuses.length)];
                    this.renderAdvancedTimeSlots();
                }
            }
        }, 5000);
    }

    startRealTimeUpdates() {
        console.log('🔄 Starting real-time updates...');
        this.realTimeUpdates = true;
    }

    generateAdvancedTimeSlots() {
        console.log('⚡ Generating advanced time slots...');
        
        const startTime = document.getElementById('opening_time')?.value || '06:00';
        const endTime = document.getElementById('closing_time')?.value || '22:00';
        const basePrice = parseFloat(document.getElementById('price_per_hour')?.value) || 50;
        
        if (!basePrice) {
            this.showNotification('Please set a base price per hour first', 'warning');
            return;
        }

        this.timeSlots = this.createAdvancedTimeSlots(startTime, endTime, basePrice);
        this.renderAdvancedTimeSlots();
        this.updateAdvancedStats();
        
        this.showNotification(`✨ Generated ${this.timeSlots.length} dynamic time slots with real-time pricing!`, 'success');
    }

    createAdvancedTimeSlots(startTime, endTime, basePrice) {
        const slots = [];
        const start = this.timeToMinutes(startTime);
        const end = this.timeToMinutes(endTime);
        const duration = 60; // 1 hour slots
        
        for (let time = start; time < end; time += duration) {
            if (time + duration > end) break;
            
            const slot = {
                id: `slot_${Date.now()}_${time}_${Math.random().toString(36).substr(2, 9)}`,
                startTime: this.minutesToTime(time),
                endTime: this.minutesToTime(time + duration),
                duration: duration,
                price: this.calculateAdvancedPrice(time, basePrice),
                status: this.getRandomStatus(),
                bookings: Math.floor(Math.random() * 3),
                popularity: Math.random() * 100,
                revenue: 0,
                lastUpdated: new Date().toISOString(),
                features: this.getSlotFeatures(time)
            };
            
            slots.push(slot);
        }
        
        return slots;
    }

    calculateAdvancedPrice(timeInMinutes, basePrice) {
        const hour = Math.floor(timeInMinutes / 60);
        const isWeekend = new Date().getDay() % 6 === 0;
        const isPeakHour = (hour >= 6 && hour <= 9) || (hour >= 17 && hour <= 21);
        const isNightTime = hour >= 20 || hour <= 6;
        
        let price = basePrice;
        let multiplier = 1;
        
        // Dynamic pricing based on time
        if (isPeakHour) multiplier += 0.3; // 30% peak surcharge
        if (isWeekend) multiplier += 0.2; // 20% weekend surcharge
        if (isNightTime) multiplier += 0.15; // 15% night lighting surcharge
        
        // Demand-based pricing
        const demand = Math.random();
        if (demand > 0.8) multiplier += 0.25; // High demand
        else if (demand > 0.6) multiplier += 0.15; // Medium demand
        
        price = price * multiplier;
        
        return price.toFixed(2);
    }

    getSlotFeatures(timeInMinutes) {
        const hour = Math.floor(timeInMinutes / 60);
        const features = [];
        
        if (hour >= 20 || hour <= 6) features.push('🌙 Night Lighting');
        if (hour >= 6 && hour <= 9) features.push('🌅 Morning Fresh');
        if (hour >= 17 && hour <= 21) features.push('🌆 Prime Time');
        if (Math.random() > 0.7) features.push('⚽ Equipment Included');
        if (Math.random() > 0.8) features.push('👥 Group Discount');
        
        return features;
    }

    renderAdvancedTimeSlots() {
        const container = document.getElementById('time-slots-container');
        if (!container || this.timeSlots.length === 0) return;

        const slotsHTML = this.timeSlots.map(slot => {
            const statusColor = this.availabilityColors[slot.status];
            const statusIcon = this.getStatusIcon(slot.status);
            const popularityWidth = Math.min(slot.popularity, 100);
            
            return `
                <div class="time-slot-card modern-slot" 
                     data-slot-id="${slot.id}"
                     style="border-left-color: ${statusColor};"
                     onclick="window.playgroundForm.toggleSlotStatus('${slot.id}')">
                    
                    <!-- Slot Header -->
                    <div class="slot-header">
                        <div class="slot-time">
                            <span class="status-icon">${statusIcon}</span>
                            <span class="time-range">${slot.startTime} - ${slot.endTime}</span>
                        </div>
                        <div class="slot-price">
                            <span class="price">$${slot.price}</span>
                            <span class="duration">${slot.duration}min</span>
                        </div>
                    </div>
                    
                    <!-- Popularity Bar -->
                    <div class="popularity-bar">
                        <div class="popularity-fill" style="width: ${popularityWidth}%; background: ${statusColor}"></div>
                        <span class="popularity-text">${Math.round(slot.popularity)}% demand</span>
                    </div>
                    
                    <!-- Slot Features -->
                    ${slot.features.length > 0 ? `
                        <div class="slot-features">
                            ${slot.features.map(feature => `<span class="feature-tag">${feature}</span>`).join('')}
                        </div>
                    ` : ''}
                    
                    <!-- Slot Status -->
                    <div class="slot-status">
                        <span class="status-badge status-${slot.status}">${slot.status.toUpperCase()}</span>
                        ${slot.bookings > 0 ? `<span class="booking-count">${slot.bookings} bookings</span>` : ''}
                        <span class="last-updated">Updated: ${new Date(slot.lastUpdated).toLocaleTimeString()}</span>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = `
            <div class="slots-header">
                <h4>⚡ Real-Time Booking Slots</h4>
                <div class="slots-controls">
                    <button type="button" onclick="window.playgroundForm.refreshSlots()" class="btn btn-secondary btn-sm">
                        🔄 Refresh
                    </button>
                    <button type="button" onclick="window.playgroundForm.toggleRealTimeUpdates()" class="btn btn-secondary btn-sm">
                        ${this.realTimeUpdates ? '⏸️ Pause' : '▶️ Resume'} Updates
                    </button>
                </div>
            </div>
            <div class="slots-grid">
                ${slotsHTML}
            </div>
        `;
    }

    getStatusIcon(status) {
        const icons = {
            available: '✅',
            booked: '❌',
            pending: '⏳',
            blocked: '🚫',
            premium: '⭐'
        };
        return icons[status] || '⚪';
    }

    toggleSlotStatus(slotId) {
        const slot = this.timeSlots.find(s => s.id === slotId);
        if (!slot) return;

        const statuses = ['available', 'booked', 'pending', 'blocked', 'premium'];
        const currentIndex = statuses.indexOf(slot.status);
        slot.status = statuses[(currentIndex + 1) % statuses.length];
        slot.lastUpdated = new Date().toISOString();
        
        this.renderAdvancedTimeSlots();
        this.updateAdvancedStats();
        this.saveDraft();
        
        this.showNotification(`Slot ${slot.startTime}-${slot.endTime} updated to ${slot.status}`, 'info');
    }

    refreshSlots() {
        this.generateAdvancedTimeSlots();
        this.showNotification('🔄 Slots refreshed with latest data', 'success');
    }

    toggleRealTimeUpdates() {
        this.realTimeUpdates = !this.realTimeUpdates;
        this.showNotification(`Real-time updates ${this.realTimeUpdates ? 'enabled' : 'disabled'}`, 'info');
    }

    updateAdvancedStats() {
        const statsContainer = document.getElementById('total-slots');
        if (!statsContainer) return;

        const stats = this.calculateAdvancedStats();
        
        // Update individual stat cards
        this.updateStatCard('total-slots', stats.totalSlots);
        this.updateStatCard('estimated-revenue', `$${stats.dailyRevenue}`);
        this.updateStatCard('facility-count', this.getFacilityCount());
        this.updateStatCard('completeness', `${stats.completeness}%`);
    }

    calculateAdvancedStats() {
        const totalSlots = this.timeSlots.length;
        const availableSlots = this.timeSlots.filter(s => s.status === 'available').length;
        const bookedSlots = this.timeSlots.filter(s => s.status === 'booked').length;
        const premiumSlots = this.timeSlots.filter(s => s.status === 'premium').length;
        
        const dailyRevenue = this.timeSlots.reduce((sum, slot) => {
            return sum + (slot.status === 'booked' ? parseFloat(slot.price) : 0);
        }, 0).toFixed(2);
        
        const occupancyRate = totalSlots > 0 ? ((bookedSlots / totalSlots) * 100).toFixed(1) : 0;
        const avgPrice = totalSlots > 0 ? 
            (this.timeSlots.reduce((sum, slot) => sum + parseFloat(slot.price), 0) / totalSlots).toFixed(2) : '0.00';
        
        const completeness = this.calculateFormCompleteness();

        return { 
            totalSlots, 
            availableSlots, 
            bookedSlots, 
            premiumSlots,
            dailyRevenue, 
            occupancyRate,
            avgPrice,
            completeness
        };
    }

    updateStatCard(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
            element.classList.add('stat-updated');
            setTimeout(() => element.classList.remove('stat-updated'), 500);
        }
    }

    calculateFormCompleteness() {
        const requiredFields = [
            'name', 'description', 'price_per_hour', 'capacity', 
            'address', 'opening_time', 'closing_time'
        ];
        
        let completedFields = 0;
        requiredFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field && field.value.trim()) {
                completedFields++;
            }
        });
        
        // Add image completion
        if (this.coverImages.length > 0) completedFields += 1;
        
        // Add time slots completion
        if (this.timeSlots.length > 0) completedFields += 1;
        
        const totalRequiredItems = requiredFields.length + 2; // +2 for images and time slots
        return Math.round((completedFields / totalRequiredItems) * 100);
    }

    getFacilityCount() {
        const facilities = document.querySelectorAll('input[name="facilities"]:checked');
        return facilities.length;
    }

    // IMAGE UPLOAD SYSTEM - ENHANCED
    triggerImageUpload(inputId) {
        console.log(`📸 Triggering image upload for: ${inputId}`);
        const input = document.getElementById(inputId);
        if (input) {
            input.click();
        }
    }

    setupImageUpload() {
        console.log('🖼️ Setting up advanced image upload system...');
        
        // Main image upload
        const mainInput = document.getElementById('main-image-input');
        if (mainInput) {
            mainInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleMainImageFiles(e.target.files);
                }
            });
        }

        // Gallery image upload
        const galleryInput = document.getElementById('gallery-input');
        if (galleryInput) {
            galleryInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleGalleryImageFiles(e.target.files);
                }
            });
        }

        this.setupDragAndDrop();
    }

    setupDragAndDrop() {
        const uploadAreas = document.querySelectorAll('.image-upload-area');
        
        uploadAreas.forEach(area => {
            area.addEventListener('dragover', (e) => {
                e.preventDefault();
                area.classList.add('drag-over');
            });

            area.addEventListener('dragleave', (e) => {
                e.preventDefault();
                area.classList.remove('drag-over');
            });

            area.addEventListener('drop', (e) => {
                e.preventDefault();
                area.classList.remove('drag-over');
                
                const files = e.dataTransfer.files;
                const target = area.getAttribute('data-target');
                
                if (files.length > 0) {
                    if (target === 'main') {
                        this.handleMainImageFiles(files);
                    } else if (target === 'gallery') {
                        this.handleGalleryImageFiles(files);
                    }
                }
            });
        });
    }

    handleMainImageFiles(files) {
        Array.from(files).forEach(file => {
            if (this.validateImageFile(file)) {
                this.processMainImage(file);
            }
        });
    }

    handleGalleryImageFiles(files) {
        Array.from(files).forEach(file => {
            if (this.validateImageFile(file)) {
                this.processGalleryImage(file);
            }
        });
    }

    validateImageFile(file) {
        const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        const maxSize = 10 * 1024 * 1024; // 10MB

        if (!validTypes.includes(file.type)) {
            this.showNotification(`Invalid file type: ${file.name}`, 'error');
            return false;
        }

        if (file.size > maxSize) {
            this.showNotification(`File too large: ${file.name} (max 10MB)`, 'error');
            return false;
        }

        return true;
    }

    processMainImage(file) {
        if (this.coverImages.length >= 5) {
            this.showNotification('Maximum 5 main images allowed', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const imageData = {
                id: this.generateId(),
                file: file,
                url: e.target.result,
                name: file.name,
                size: file.size,
                uploadTime: new Date().toISOString(),
                type: 'main'
            };
            
            this.coverImages.push(imageData);
            this.updateMainImageDisplay();
            this.showNotification(`Main image added: ${file.name}`, 'success');
            this.saveDraft();
        };
        reader.readAsDataURL(file);
    }

    processGalleryImage(file) {
        if (this.galleryImages.length >= 20) {
            this.showNotification('Maximum 20 gallery images allowed', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const imageData = {
                id: this.generateId(),
                file: file,
                url: e.target.result,
                name: file.name,
                size: file.size,
                uploadTime: new Date().toISOString(),
                type: 'gallery'
            };
            
            this.galleryImages.push(imageData);
            this.updateGalleryDisplay();
            this.showNotification(`Gallery image added: ${file.name}`, 'success');
            this.saveDraft();
        };
        reader.readAsDataURL(file);
    }

    updateMainImageDisplay() {
        const preview = document.getElementById('main-image-preview');
        if (!preview) return;

        if (this.coverImages.length === 0) {
            preview.innerHTML = '<div class="no-images">No main images uploaded</div>';
            return;
        }

        const imageHTML = this.coverImages.map((image, index) => `
            <div class="image-item" data-id="${image.id}">
                <img src="${image.url}" alt="${image.name}" class="preview-image">
                <div class="image-overlay">
                    <button type="button" onclick="window.playgroundForm.removeImage('${image.id}', 'main')" 
                            class="remove-btn">×</button>
                    <span class="image-name">${image.name}</span>
                </div>
            </div>
        `).join('');

        preview.innerHTML = `<div class="images-grid">${imageHTML}</div>`;
    }

    updateGalleryDisplay() {
        const preview = document.getElementById('gallery-preview');
        if (!preview) return;

        if (this.galleryImages.length === 0) {
            preview.innerHTML = '<div class="no-images">No gallery images uploaded</div>';
            return;
        }

        const imageHTML = this.galleryImages.map((image, index) => `
            <div class="gallery-item" data-id="${image.id}">
                <img src="${image.url}" alt="${image.name}" class="gallery-image">
                <div class="gallery-overlay">
                    <button type="button" onclick="window.playgroundForm.removeImage('${image.id}', 'gallery')" 
                            class="remove-btn">×</button>
                </div>
            </div>
        `).join('');

        preview.innerHTML = `<div class="gallery-grid">${imageHTML}</div>`;
    }

    removeImage(imageId, type) {
        if (type === 'main') {
            this.coverImages = this.coverImages.filter(img => img.id !== imageId);
            this.updateMainImageDisplay();
        } else if (type === 'gallery') {
            this.galleryImages = this.galleryImages.filter(img => img.id !== imageId);
            this.updateGalleryDisplay();
        }
        
        this.showNotification('Image removed successfully', 'success');
        this.saveDraft();
    }

    // GOOGLE MAPS INTEGRATION
    initializeGoogleMaps() {
        console.log('🗺️ Initializing Google Maps...');
        
        // Check if Google Maps is loaded
        if (typeof google === 'undefined' || !google.maps) {
            console.log('📍 Google Maps API not loaded, using fallback');
            this.setupMapFallback();
            return;
        }

        const mapContainer = document.getElementById('map');
        if (!mapContainer) {
            console.log('Map container not found');
            return;
        }

        this.map = new google.maps.Map(mapContainer, {
            zoom: 15,
            center: { lat: 23.8103, lng: 90.4125 }, // Default: Dhaka
            mapTypeControl: true,
            streetViewControl: true,
            fullscreenControl: true
        });

        this.marker = new google.maps.Marker({
            position: this.map.getCenter(),
            map: this.map,
            draggable: true,
            title: 'Playground Location'
        });

        this.geocoder = new google.maps.Geocoder();
        
        console.log('✅ Google Maps initialized successfully');
    }

    setupMapFallback() {
        const mapContainer = document.getElementById('map');
        if (mapContainer) {
            mapContainer.innerHTML = `
                <div class="map-fallback">
                    <h4>🗺️ Interactive Map</h4>
                    <p>Map will load when Google Maps API is available</p>
                    <button type="button" onclick="window.playgroundForm.retryMapLoad()" class="btn btn-secondary">
                        🔄 Retry Loading Map
                    </button>
                </div>
            `;
        }
    }

    retryMapLoad() {
        this.initializeGoogleMaps();
    }

    searchOnMap() {
        const query = document.getElementById('location-search')?.value?.trim();
        if (!query) {
            this.showNotification('Please enter a location to search', 'warning');
            return;
        }

        if (!this.geocoder) {
            this.showNotification('Map service not available', 'error');
            return;
        }

        this.geocoder.geocode({ address: query }, (results, status) => {
            if (status === 'OK' && results[0]) {
                const location = results[0].geometry.location;
                this.map.setCenter(location);
                this.marker.setPosition(location);
                this.showNotification(`Location found: ${results[0].formatted_address}`, 'success');
            } else {
                this.showNotification('Location not found', 'error');
            }
        });
    }

    // FORM VALIDATION SYSTEM
    initializeFormValidation() {
        console.log('✅ Setting up form validation...');
        this.setupValidationRules();
    }

    setupValidationRules() {
        this.validationRules = {
            name: { required: true, minLength: 3 },
            description: { required: true, minLength: 10 },
            price_per_hour: { required: true, min: 1 },
            capacity: { required: true, min: 1 },
            address: { required: true, minLength: 10 },
            opening_time: { required: true },
            closing_time: { required: true }
        };
    }

    validateCurrentStep() {
        const currentStepElement = document.querySelector(`[data-step="${this.currentStep}"]`);
        if (!currentStepElement) return true;

        const requiredFields = currentStepElement.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        const rules = this.validationRules[field.id] || {};
        
        // Clear previous errors
        this.clearFieldError(field);
        
        // Required validation
        if (rules.required && !value) {
            this.showFieldError(field, 'This field is required');
            return false;
        }
        
        // Length validation
        if (rules.minLength && value.length < rules.minLength) {
            this.showFieldError(field, `Minimum ${rules.minLength} characters required`);
            return false;
        }
        
        // Number validation
        if (rules.min && parseFloat(value) < rules.min) {
            this.showFieldError(field, `Minimum value is ${rules.min}`);
            return false;
        }
        
        // Email validation
        if (field.type === 'email' && value && !this.isValidEmail(value)) {
            this.showFieldError(field, 'Please enter a valid email address');
            return false;
        }
        
        return true;
    }

    showFieldError(field, message) {
        field.classList.add('error');
        
        const errorElement = document.getElementById(`${field.id}-error`);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.add('show');
        }
    }

    clearFieldError(field) {
        field.classList.remove('error');
        
        const errorElement = document.getElementById(`${field.id}-error`);
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.classList.remove('show');
        }
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // FORM SUBMISSION
    submitForm() {
        console.log('📤 Submitting professional playground form...');
        
        if (!this.validateAllSteps()) {
            this.showNotification('Please complete all required fields', 'error');
            return;
        }

        const formData = this.collectFormData();
        
        this.showNotification('Submitting your professional playground...', 'info');
        
        // Submit the form
        const form = document.getElementById('professionalPlaygroundForm');
        if (form) {
            form.submit();
        }
    }

    validateAllSteps() {
        for (let step = 1; step <= this.totalSteps; step++) {
            const stepElement = document.querySelector(`[data-step="${step}"]`);
            if (stepElement) {
                const requiredFields = stepElement.querySelectorAll('[required]');
                for (let field of requiredFields) {
                    if (!this.validateField(field)) {
                        this.currentStep = step;
                        this.updateStepDisplay();
                        return false;
                    }
                }
            }
        }
        return true;
    }

    collectFormData() {
        const formData = new FormData();
        
        // Collect all form fields
        const form = document.getElementById('professionalPlaygroundForm');
        if (form) {
            new FormData(form).forEach((value, key) => {
                formData.append(key, value);
            });
        }
        
        // Add images
        this.coverImages.forEach((image, index) => {
            formData.append(`cover_image_${index}`, image.file);
        });
        
        this.galleryImages.forEach((image, index) => {
            formData.append(`gallery_image_${index}`, image.file);
        });
        
        // Add time slots data
        formData.append('time_slots', JSON.stringify(this.timeSlots));
        
        return formData;
    }

    // UTILITY METHODS
    handleFormInput(field) {
        this.validateField(field);
        this.updateFormData(field);
    }

    updateFormData(field) {
        this.formData[field.id] = field.value;
    }

    updatePricingAndSlots() {
        if (this.timeSlots.length > 0) {
            this.generateAdvancedTimeSlots();
        }
    }

    debouncedSave() {
        clearTimeout(this.saveTimeout);
        this.saveTimeout = setTimeout(() => {
            this.saveDraft();
        }, 1000);
    }

    saveDraft() {
        const draftData = {
            currentStep: this.currentStep,
            formData: this.formData,
            coverImages: this.coverImages.map(img => ({ ...img, file: null })), // Don't save file objects
            galleryImages: this.galleryImages.map(img => ({ ...img, file: null })),
            timeSlots: this.timeSlots,
            timestamp: new Date().toISOString()
        };
        
        localStorage.setItem('playgroundFormDraft', JSON.stringify(draftData));
        console.log('💾 Draft saved');
    }

    loadDraftData() {
        const draftData = localStorage.getItem('playgroundFormDraft');
        if (draftData) {
            try {
                const data = JSON.parse(draftData);
                this.currentStep = data.currentStep || 1;
                this.formData = data.formData || {};
                this.timeSlots = data.timeSlots || [];
                
                // Restore form values
                Object.keys(this.formData).forEach(key => {
                    const field = document.getElementById(key);
                    if (field) {
                        field.value = this.formData[key];
                    }
                });
                
                this.updateStepDisplay();
                console.log('📁 Draft data loaded');
            } catch (error) {
                console.error('Error loading draft:', error);
            }
        }
    }

    loadDraft() {
        this.loadDraftData();
        this.showNotification('Draft loaded successfully', 'success');
    }

    generateFinalPreview() {
        const previewContainer = document.getElementById('dynamic-preview');
        if (!previewContainer) return;

        const formData = this.collectFormData();
        const stats = this.calculateAdvancedStats();
        
        const previewHTML = `
            <div class="final-preview">
                <div class="preview-header">
                    <h3>🎯 Your Professional Playground</h3>
                    <span class="completeness-badge">${stats.completeness}% Complete</span>
                </div>
                
                <div class="preview-content">
                    <div class="preview-main">
                        <h4>${document.getElementById('name')?.value || 'Playground Name'}</h4>
                        <p>${document.getElementById('description')?.value || 'Description not provided'}</p>
                        
                        <div class="preview-details">
                            <div class="detail-item">
                                <strong>💰 Price:</strong> $${document.getElementById('price_per_hour')?.value || '0'}/hour
                            </div>
                            <div class="detail-item">
                                <strong>👥 Capacity:</strong> ${document.getElementById('capacity')?.value || '0'} people
                            </div>
                            <div class="detail-item">
                                <strong>🕐 Hours:</strong> ${document.getElementById('opening_time')?.value || '00:00'} - ${document.getElementById('closing_time')?.value || '00:00'}
                            </div>
                            <div class="detail-item">
                                <strong>📍 Location:</strong> ${document.getElementById('address')?.value || 'Address not provided'}
                            </div>
                        </div>
                    </div>
                    
                    <div class="preview-stats">
                        <div class="stat-grid">
                            <div class="stat-item">
                                <span class="stat-number">${stats.totalSlots}</span>
                                <span class="stat-label">Time Slots</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number">${this.coverImages.length}</span>
                                <span class="stat-label">Main Images</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number">${this.galleryImages.length}</span>
                                <span class="stat-label">Gallery Images</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-number">${this.getFacilityCount()}</span>
                                <span class="stat-label">Facilities</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        previewContainer.innerHTML = previewHTML;
    }

    initializeImageUploads() {
        // Initialize image upload areas for step 4
        this.setupImageUpload();
    }

    timeToMinutes(timeString) {
        const [hours, minutes] = timeString.split(':').map(Number);
        return hours * 60 + minutes;
    }

    minutesToTime(minutes) {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
    }

    generateId() {
        return `id_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    getRandomStatus() {
        const statuses = ['available', 'booked', 'pending', 'blocked', 'premium'];
        const weights = [0.4, 0.25, 0.15, 0.1, 0.1];
        
        const random = Math.random();
        let cumulative = 0;
        
        for (let i = 0; i < statuses.length; i++) {
            cumulative += weights[i];
            if (random <= cumulative) {
                return statuses[i];
            }
        }
        
        return 'available';
    }

    updateDynamicPricing() {
        // Update pricing based on real-time factors
        if (this.timeSlots.length > 0) {
            this.timeSlots.forEach(slot => {
                const timeInMinutes = this.timeToMinutes(slot.startTime);
                const basePrice = parseFloat(document.getElementById('price_per_hour')?.value) || 50;
                slot.price = this.calculateAdvancedPrice(timeInMinutes, basePrice);
                slot.lastUpdated = new Date().toISOString();
            });
            
            this.renderAdvancedTimeSlots();
        }
    }

    checkRealTimeAvailability() {
        // Simulate real-time availability checks
        if (this.timeSlots.length > 0 && Math.random() > 0.9) {
            const randomSlot = this.timeSlots[Math.floor(Math.random() * this.timeSlots.length)];
            if (randomSlot.status === 'pending') {
                randomSlot.status = Math.random() > 0.5 ? 'booked' : 'available';
                randomSlot.lastUpdated = new Date().toISOString();
                this.renderAdvancedTimeSlots();
            }
        }
    }

    showNotification(message, type = 'info') {
        console.log(`📢 ${type.toUpperCase()}: ${message}`);
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <span class="notification-message">${message}</span>
            <button type="button" class="close-btn" onclick="this.parentElement.remove()">×</button>
        `;
        
        // Add to notifications container
        let container = document.getElementById('notifications-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notifications-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
}

// 🌐 Expose class globally for better debugging and access
console.log('📤 Exposing ProfessionalPlaygroundForm to global scope...');
window.ProfessionalPlaygroundForm = ProfessionalPlaygroundForm;

// 🚀 Auto-initialize form with error handling
try {
    console.log('🔄 Auto-initializing playground form...');
    
    // Check if DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            console.log('📄 DOM ready - creating form instance');
            window.playgroundForm = new ProfessionalPlaygroundForm();
        });
    } else {
        console.log('📄 DOM already ready - creating form instance immediately');
        window.playgroundForm = new ProfessionalPlaygroundForm();
    }
    
    console.log('✅ Form initialization completed successfully');
} catch (error) {
    console.error('❌ Error during form initialization:', error);
}

console.log('🎯 Professional Playground Form Script Loaded Successfully');
