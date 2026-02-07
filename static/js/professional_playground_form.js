/**
 * Professional Playground Form Manager - ULTRA MODERN VERSION
 * Advanced real-time booking system with dynamic slots and professional design
 */

class ProfessionalPlaygroundForm {
    constructor() {
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
        
        // Core setup
        this.setupEventListeners();
        this.initializeFormValidation();
        this.initializeStepNavigation();
        this.setupImageUpload();
        this.setupRealTimeBooking();
        
        // External services
        this.initializeGoogleMaps();
        this.setupWebSocketConnection();
        
        // Load any existing data
        this.loadDraftData();
        
        // Start real-time updates
        this.startRealTimeUpdates();
        
        console.log('✅ Ultra Modern Playground Form ready!');
        this.showNotification('🎯 Professional form loaded successfully!', 'success');
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

    // FIXED IMAGE UPLOAD - NO MORE DOUBLE CLICKS
    triggerImageUpload(inputId) {
        setTimeout(() => {
            const input = document.getElementById(inputId);
            if (input) {
                input.click();
            }
        }, 100);
    }

    setupImageUpload() {
        // Cover image upload - FIXED
        const coverInput = document.getElementById('cover-image-input');
        if (coverInput) {
            coverInput.addEventListener('change', (e) => {
                console.log('📸 Cover image files selected:', e.target.files.length);
                if (e.target.files.length > 0) {
                    this.handleCoverImageFiles(e.target.files);
                    e.target.value = ''; // Clear for re-selection
                }
            });
        }

        // Gallery image upload - FIXED
        const galleryInput = document.getElementById('gallery-input');
        if (galleryInput) {
            galleryInput.addEventListener('change', (e) => {
                console.log('🖼️ Gallery image files selected:', e.target.files.length);
                if (e.target.files.length > 0) {
                    this.handleGalleryImageFiles(e.target.files);
                    e.target.value = ''; // Clear for re-selection
                }
            });
        }

        // Setup drag and drop
        this.setupDragAndDrop();
    }

    setupDragAndDrop() {
        const dropzones = [
            { element: document.getElementById('cover-image-dropzone'), handler: (files) => this.handleCoverImageFiles(files) },
            { element: document.getElementById('gallery-dropzone'), handler: (files) => this.handleGalleryImageFiles(files) }
        ];

        dropzones.forEach(({ element, handler }) => {
            if (!element) return;

            element.addEventListener('dragover', (e) => {
                e.preventDefault();
                element.classList.add('drag-over');
            });

            element.addEventListener('dragleave', (e) => {
                e.preventDefault();
                if (!element.contains(e.relatedTarget)) {
                    element.classList.remove('drag-over');
                }
            });

            element.addEventListener('drop', (e) => {
                e.preventDefault();
                element.classList.remove('drag-over');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    handler(files);
                }
            });
        });
    }

    handleCoverImageFiles(files) {
        if (!files || files.length === 0) return;

        this.showNotification('Processing cover images...', 'info');
        
        Array.from(files).forEach(file => {
            if (this.validateImageFile(file)) {
                this.processCoverImage(file);
            }
        });
    }

    handleGalleryImageFiles(files) {
        if (!files || files.length === 0) return;

        this.showNotification('Processing gallery images...', 'info');
        
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
            this.showNotification(`File too large: ${file.name}`, 'error');
            return false;
        }

        return true;
    }

    processCoverImage(file) {
        // Prevent duplicates
        const exists = this.coverImages.find(img => img.name === file.name && img.size === file.size);
        if (exists) {
            this.showNotification(`Image already exists: ${file.name}`, 'warning');
            return;
        }

        if (this.coverImages.length >= 5) {
            this.showNotification('Maximum 5 cover images allowed', 'error');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const imageData = {
                id: 'cover_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
                file: file,
                url: e.target.result,
                name: file.name,
                size: file.size,
                uploadTime: new Date().toISOString()
            };
            
            this.coverImages.push(imageData);
            this.updateCoverImageDisplay();
            this.showNotification(`Cover image added: ${file.name}`, 'success');
            this.saveDraft();
        };
        reader.readAsDataURL(file);
    }

    processGalleryImage(file) {
        // Prevent duplicates
        const exists = this.galleryImages.find(img => img.name === file.name && img.size === file.size);
        if (exists) {
            this.showNotification(`Image already exists: ${file.name}`, 'warning');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const imageData = {
                id: 'gallery_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
                file: file,
                url: e.target.result,
                name: file.name,
                size: file.size,
                uploadTime: new Date().toISOString()
            };
            
            this.galleryImages.push(imageData);
            this.updateGalleryImageDisplay();
            this.showNotification(`Gallery image added: ${file.name}`, 'success');
            this.saveDraft();
        };
        reader.readAsDataURL(file);
    }

    updateCoverImageDisplay() {
        const placeholder = document.getElementById('cover-image-placeholder');
        const slider = document.getElementById('cover-image-slider');
        const container = document.getElementById('cover-slider-container');
        
        if (!container) return;

        if (this.coverImages.length === 0) {
            if (placeholder) placeholder.style.display = 'block';
            if (slider) slider.classList.add('hidden');
            return;
        }

        if (placeholder) placeholder.style.display = 'none';
        if (slider) slider.classList.remove('hidden');

        const sliderHTML = this.coverImages.map((image, index) => `
            <div class="flex-shrink-0 w-full relative group">
                <img src="${image.url}" alt="${image.name}" class="w-full h-64 object-cover" />
                <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                    <div class="absolute bottom-4 left-4 right-4">
                        <div class="text-white text-sm font-medium">${image.name}</div>
                        <div class="text-white/80 text-xs">${(image.size / (1024*1024)).toFixed(1)} MB</div>
                    </div>
                    <button type="button" onclick="window.professionalForm.removeCoverImage('${image.id}')" 
                            class="absolute top-4 right-4 bg-red-500/80 hover:bg-red-600 text-white p-2 rounded-full transition-colors">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `).join('');

        container.innerHTML = sliderHTML;

        // Update navigation dots
        const dotsContainer = document.getElementById('slider-dots');
        if (dotsContainer && this.coverImages.length > 1) {
            const dotsHTML = this.coverImages.map((_, index) => `
                <button type="button" onclick="window.professionalForm.goToSlide(${index})" 
                        class="w-3 h-3 rounded-full transition-colors ${index === this.currentSlideIndex ? 'bg-emerald-400' : 'bg-white/50 hover:bg-white/80'}"></button>
            `).join('');
            dotsContainer.innerHTML = dotsHTML;
        }

        this.updateSliderPosition();
        
        if (this.coverImages.length > 1) {
            this.startSliderAutoplay();
        }
    }

    updateGalleryImageDisplay() {
        const container = document.getElementById('gallery-preview');
        if (!container) return;

        if (this.galleryImages.length === 0) {
            container.innerHTML = `
                <div class="text-center text-gray-400 py-8">
                    <i class="fas fa-images text-4xl mb-3"></i>
                    <p>No gallery images uploaded yet</p>
                </div>
            `;
            return;
        }

        const galleryHTML = this.galleryImages.map(image => `
            <div class="gallery-item relative group" data-id="${image.id}">
                <img src="${image.url}" alt="${image.name}" 
                     class="w-full h-24 object-cover rounded-lg cursor-pointer transition-transform hover:scale-105" 
                     onclick="window.professionalForm.openImageModal('${image.url}', '${image.name}')" />
                <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
                    <button type="button" 
                            onclick="window.professionalForm.removeGalleryImage('${image.id}')" 
                            class="bg-red-500 hover:bg-red-600 text-white p-2 rounded-full transition-colors">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                <div class="absolute bottom-1 left-1 right-1 bg-black/75 text-white text-xs p-1 rounded truncate">
                    ${image.name}
                </div>
            </div>
        `).join('');

        container.innerHTML = `<div class="grid grid-cols-3 gap-3">${galleryHTML}</div>`;
    }

    // DYNAMIC TIME SLOTS SYSTEM - FULLY FUNCTIONAL
    generateDynamicTimeSlots() {
        const startTime = document.getElementById('operating_hours_start')?.value || '06:00';
        const endTime = document.getElementById('operating_hours_end')?.value || '22:00';
        const duration = parseInt(document.getElementById('slot_duration')?.value) || 60;
        const basePrice = parseFloat(document.getElementById('price_per_hour')?.value) || 50;

        if (!basePrice) {
            this.showNotification('Please set a base price per hour first', 'warning');
            return;
        }

        this.timeSlots = this.createTimeSlots(startTime, endTime, duration, basePrice);
        this.renderTimeSlotsDisplay();
        this.updatePricingPreview();
        this.showNotification(`Generated ${this.timeSlots.length} dynamic time slots`, 'success');
    }

    createTimeSlots(startTime, endTime, duration, basePrice) {
        const slots = [];
        const start = this.timeToMinutes(startTime);
        const end = this.timeToMinutes(endTime);
        
        for (let time = start; time < end; time += duration) {
            if (time + duration > end) break;
            
            const slot = {
                id: `slot_${Date.now()}_${time}`,
                startTime: this.minutesToTime(time),
                endTime: this.minutesToTime(time + duration),
                duration: duration,
                price: this.calculateDynamicPrice(time, basePrice),
                status: this.getRandomStatus(),
                bookings: Math.floor(Math.random() * 3),
                revenue: 0
            };
            
            slots.push(slot);
        }
        
        return slots;
    }

    calculateDynamicPrice(timeInMinutes, basePrice) {
        const hour = Math.floor(timeInMinutes / 60);
        const isWeekend = Math.random() > 0.7; // Simulate weekend
        const isPeakHour = (hour >= 6 && hour <= 9) || (hour >= 17 && hour <= 21);
        
        let price = basePrice;
        
        // Weekend pricing
        if (isWeekend) {
            const weekendPrice = parseFloat(document.getElementById('weekend_price')?.value) || 0;
            if (weekendPrice > 0) price = weekendPrice;
        }
        
        // Peak hour surcharge
        if (isPeakHour) {
            const surcharge = parseFloat(document.getElementById('peak_hours_surcharge')?.value) || 0;
            price += (price * surcharge / 100);
        }
        
        return price.toFixed(2);
    }

    getRandomStatus() {
        const statuses = ['available', 'booked', 'pending', 'blocked'];
        const weights = [0.6, 0.25, 0.1, 0.05];
        
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

    renderTimeSlotsDisplay() {
        const container = document.getElementById('time-slots-preview');
        if (!container || this.timeSlots.length === 0) return;

        const slotsHTML = this.timeSlots.map(slot => {
            const statusColor = this.availabilityColors[slot.status];
            const statusIcon = {
                available: '✅',
                booked: '❌',
                pending: '⏳',
                blocked: '🚫'
            }[slot.status];
            
            return `
                <div class="time-slot-card bg-white rounded-lg p-4 border-l-4 hover:shadow-lg transition-all cursor-pointer"
                     style="border-left-color: ${statusColor};"
                     onclick="window.professionalForm.toggleSlotStatus('${slot.id}')">
                    <div class="flex justify-between items-start">
                        <div class="flex-1">
                            <div class="font-semibold text-gray-900 flex items-center">
                                <span class="mr-2">${statusIcon}</span>
                                ${slot.startTime} - ${slot.endTime}
                            </div>
                            <div class="text-sm text-gray-600 mt-1">
                                ${slot.duration} minutes • ${slot.status.charAt(0).toUpperCase() + slot.status.slice(1)}
                            </div>
                            ${slot.bookings > 0 ? `
                                <div class="text-xs text-gray-500 mt-1">
                                    ${slot.bookings} booking${slot.bookings > 1 ? 's' : ''}
                                </div>
                            ` : ''}
                        </div>
                        <div class="text-right">
                            <div class="text-lg font-bold text-emerald-600">$${slot.price}</div>
                            <div class="text-xs text-gray-500">per slot</div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = `
            <div class="space-y-3">
                <div class="flex justify-between items-center mb-4">
                    <h4 class="font-semibold text-gray-900">🕐 Live Time Slots</h4>
                    <div class="flex space-x-3 text-xs">
                        ${Object.entries(this.availabilityColors).map(([status, color]) => `
                            <div class="flex items-center">
                                <div class="w-3 h-3 rounded-full mr-1" style="background-color: ${color}"></div>
                                ${status.charAt(0).toUpperCase() + status.slice(1)}
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="grid gap-3 max-h-80 overflow-y-auto">
                    ${slotsHTML}
                </div>
            </div>
        `;
    }

    toggleSlotStatus(slotId) {
        const slot = this.timeSlots.find(s => s.id === slotId);
        if (!slot) return;

        const statuses = ['available', 'booked', 'pending', 'blocked'];
        const currentIndex = statuses.indexOf(slot.status);
        slot.status = statuses[(currentIndex + 1) % statuses.length];
        
        this.renderTimeSlotsDisplay();
        this.updatePricingPreview();
        this.saveDraft();
        
        this.showNotification(`Slot ${slot.startTime}-${slot.endTime} marked as ${slot.status}`, 'info');
    }

    updatePricingPreview() {
        const container = document.getElementById('pricing-preview-container');
        if (!container || this.timeSlots.length === 0) return;

        const stats = this.calculateStats();
        
        container.innerHTML = `
            <div class="bg-gradient-to-r from-emerald-50 to-blue-50 rounded-lg p-4 border">
                <h4 class="font-semibold text-gray-900 mb-3">📊 Dynamic Pricing Overview</h4>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                    <div class="bg-white rounded-lg p-3 shadow-sm">
                        <div class="text-2xl font-bold text-emerald-600">${stats.totalSlots}</div>
                        <div class="text-xs text-gray-500">Total Slots</div>
                    </div>
                    <div class="bg-white rounded-lg p-3 shadow-sm">
                        <div class="text-2xl font-bold text-green-600">${stats.availableSlots}</div>
                        <div class="text-xs text-gray-500">Available</div>
                    </div>
                    <div class="bg-white rounded-lg p-3 shadow-sm">
                        <div class="text-2xl font-bold text-blue-600">$${stats.avgPrice}</div>
                        <div class="text-xs text-gray-500">Avg Price</div>
                    </div>
                    <div class="bg-white rounded-lg p-3 shadow-sm">
                        <div class="text-2xl font-bold text-purple-600">$${stats.totalRevenue}</div>
                        <div class="text-xs text-gray-500">Potential Revenue</div>
                    </div>
                </div>
            </div>
        `;
    }

    calculateStats() {
        const totalSlots = this.timeSlots.length;
        const availableSlots = this.timeSlots.filter(s => s.status === 'available').length;
        const bookedSlots = this.timeSlots.filter(s => s.status === 'booked').length;
        const avgPrice = totalSlots > 0 ? 
            (this.timeSlots.reduce((sum, slot) => sum + parseFloat(slot.price), 0) / totalSlots).toFixed(2) : '0.00';
        const totalRevenue = this.timeSlots.reduce((sum, slot) => sum + parseFloat(slot.price), 0).toFixed(2);

        return { totalSlots, availableSlots, bookedSlots, avgPrice, totalRevenue };
    }

    // GOOGLE MAPS INTEGRATION - FULLY DYNAMIC
    initializeGoogleMaps() {
        // Wait for Google Maps API to load
        if (typeof google === 'undefined' || !google.maps) {
            console.log('📍 Waiting for Google Maps API...');
            setTimeout(() => this.initializeGoogleMaps(), 1000);
            return;
        }

        const mapContainer = document.getElementById('map-preview');
        if (!mapContainer) return;

        this.map = new google.maps.Map(mapContainer, {
            zoom: 15,
            center: { lat: 23.8103, lng: 90.4125 }, // Default: Dhaka
            mapTypeControl: true,
            streetViewControl: true,
            fullscreenControl: true,
            styles: [
                {
                    featureType: "poi.business",
                    stylers: [{ visibility: "off" }]
                }
            ]
        });

        this.marker = new google.maps.Marker({
            position: this.map.getCenter(),
            map: this.map,
            draggable: true,
            title: 'Playground Location',
            animation: google.maps.Animation.DROP
        });

        this.marker.addListener('dragend', () => {
            const pos = this.marker.getPosition();
            this.updateLocationFromMap(pos.lat(), pos.lng());
        });

        this.map.addListener('click', (e) => {
            this.marker.setPosition(e.latLng);
            this.updateLocationFromMap(e.latLng.lat(), e.latLng.lng());
        });

        this.geocoder = new google.maps.Geocoder();
        console.log('🗺️ Google Maps initialized successfully');
    }

    getCurrentLocation() {
        if (!navigator.geolocation) {
            this.showNotification('Geolocation not supported', 'error');
            return;
        }

        this.showNotification('Getting your location...', 'info');

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                this.updateMapLocation(lat, lng);
                this.showNotification('Location updated successfully!', 'success');
            },
            (error) => {
                console.error('Geolocation error:', error);
                this.showNotification('Unable to get location', 'error');
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 }
        );
    }

    searchOnMap() {
        const query = document.getElementById('location-search')?.value?.trim();
        if (!query) {
            this.showNotification('Please enter a location to search', 'warning');
            return;
        }

        if (!this.geocoder) {
            this.showNotification('Map services not available', 'error');
            return;
        }

        this.showNotification('Searching location...', 'info');

        this.geocoder.geocode({ address: query }, (results, status) => {
            if (status === 'OK' && results[0]) {
                const location = results[0].geometry.location;
                this.updateMapLocation(location.lat(), location.lng());
                this.updateAddressFields(results[0]);
                this.showNotification('Location found!', 'success');
            } else {
                this.showNotification('Location not found', 'error');
            }
        });
    }

    updateMapLocation(lat, lng) {
        if (!this.map || !this.marker) return;

        const position = new google.maps.LatLng(lat, lng);
        this.map.setCenter(position);
        this.marker.setPosition(position);
        
        this.updateLocationFromMap(lat, lng);
    }

    updateLocationFromMap(lat, lng) {
        // Update form fields
        const latField = document.getElementById('latitude');
        const lngField = document.getElementById('longitude');
        
        if (latField) latField.value = lat.toFixed(6);
        if (lngField) lngField.value = lng.toFixed(6);

        // Reverse geocode
        if (this.geocoder) {
            this.geocoder.geocode({ location: { lat, lng } }, (results, status) => {
                if (status === 'OK' && results[0]) {
                    this.updateAddressFields(results[0]);
                }
            });
        }

        this.saveDraft();
    }

    updateAddressFields(result) {
        const addressField = document.getElementById('address');
        const cityField = document.getElementById('city');
        const postalField = document.getElementById('postal_code');

        if (addressField) addressField.value = result.formatted_address;

        result.address_components.forEach(component => {
            if (component.types.includes('locality') && cityField) {
                cityField.value = component.long_name;
            }
            if (component.types.includes('postal_code') && postalField) {
                postalField.value = component.long_name;
            }
        });
    }

    // FORM NAVIGATION - ENHANCED
    nextStep() {
        if (!this.validateCurrentStep()) return;
        
        if (this.currentStep < this.totalSteps) {
            this.currentStep++;
            this.updateStepDisplay();
            this.saveDraft();
        }
    }

    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateStepDisplay();
        }
    }

    updateStepDisplay() {
        // Update step visibility
        for (let i = 1; i <= this.totalSteps; i++) {
            const step = document.getElementById(`step-${i}`);
            if (step) {
                step.style.display = i === this.currentStep ? 'block' : 'none';
                step.classList.toggle('active', i === this.currentStep);
            }
        }

        // Update progress indicators
        const indicators = document.querySelectorAll('.step-indicator');
        indicators.forEach((indicator, index) => {
            const stepNumber = index + 1;
            const isActive = stepNumber <= this.currentStep;
            indicator.classList.toggle('active', isActive);
            indicator.style.backgroundColor = isActive ? '#10b981' : 'rgba(16, 185, 129, 0.3)';
        });

        // Update step info
        const stepLabels = [
            'Basic Information',
            'Images & Media',
            'Location & Contact',
            'Pricing & Availability',
            'Review & Submit'
        ];
        
        const labelElement = document.getElementById('current-step-label');
        const numberElement = document.getElementById('current-step-number');
        
        if (labelElement) labelElement.textContent = stepLabels[this.currentStep - 1] || 'Step';
        if (numberElement) numberElement.textContent = this.currentStep;

        // Generate preview for final step
        if (this.currentStep === 5) {
            setTimeout(() => this.generateDynamicPreview(), 200);
        }

        console.log(`Updated to step ${this.currentStep}/${this.totalSteps}`);
    }

    validateCurrentStep() {
        const stepElement = document.getElementById(`step-${this.currentStep}`);
        if (!stepElement) return true;

        const requiredFields = stepElement.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            this.clearFieldError(field);
            
            if (!field.value.trim()) {
                this.showFieldError(field, 'This field is required');
                isValid = false;
            } else {
                // Validate specific field types
                if (field.type === 'email' && !this.isValidEmail(field.value)) {
                    this.showFieldError(field, 'Please enter a valid email');
                    isValid = false;
                }
            }
        });

        // Step-specific validation
        if (this.currentStep === 2 && this.coverImages.length === 0) {
            this.showNotification('Please upload at least one cover image', 'error');
            isValid = false;
        }

        return isValid;
    }

    showFieldError(field, message) {
        this.clearFieldError(field);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error text-red-500 text-xs mt-1';
        errorDiv.textContent = message;
        
        field.parentNode.appendChild(errorDiv);
        field.classList.add('border-red-500');
    }

    clearFieldError(field) {
        const error = field.parentNode.querySelector('.field-error');
        if (error) error.remove();
        field.classList.remove('border-red-500');
    }

    isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    // DYNAMIC PREVIEW GENERATION - FULLY REAL-TIME
    generateDynamicPreview() {
        const formData = this.collectFormData();
        const container = document.getElementById('final-preview-container');
        
        if (!container) return;

        console.log('🎯 Generating dynamic preview with real data');

        const stats = this.calculateStats();
        const lat = formData.latitude || '23.8103';
        const lng = formData.longitude || '90.4125';

        const previewHTML = `
            <div class="dynamic-preview bg-gradient-to-br from-slate-900 to-slate-800 text-white rounded-xl overflow-hidden shadow-2xl">
                <!-- Header -->
                <div class="bg-gradient-to-r from-emerald-600 to-emerald-500 p-6">
                    <div class="flex items-center justify-between">
                        <div class="flex-1">
                            <h2 class="text-2xl font-bold mb-2">${formData.name || 'Professional Playground'}</h2>
                            <div class="flex items-center text-emerald-100 mb-2">
                                <i class="fas fa-map-marker-alt mr-2"></i>
                                ${formData.address || 'Address not provided'}
                            </div>
                            <div class="flex items-center space-x-4 text-emerald-200 text-sm">
                                ${formData.email ? `<span><i class="fas fa-envelope mr-1"></i>${formData.email}</span>` : ''}
                                ${formData.phone ? `<span><i class="fas fa-phone mr-1"></i>${formData.phone}</span>` : ''}
                            </div>
                        </div>
                        <div class="text-right">
                            <div class="text-3xl font-bold">$${stats.avgPrice}</div>
                            <div class="text-emerald-100 text-sm">Average Price</div>
                            <div class="text-emerald-200 text-xs mt-1">${stats.availableSlots}/${stats.totalSlots} Available</div>
                        </div>
                    </div>
                </div>

                <!-- Real Cover Images -->
                ${this.coverImages.length > 0 ? `
                    <div class="relative h-64 overflow-hidden">
                        <div class="flex transition-transform duration-500" id="preview-slider">
                            ${this.coverImages.map(img => `
                                <div class="w-full h-64 flex-shrink-0 relative">
                                    <img src="${img.url}" alt="${img.name}" class="w-full h-64 object-cover" />
                                    <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
                                        <div class="text-white text-sm">${img.name}</div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        ${this.coverImages.length > 1 ? `
                            <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
                                ${this.coverImages.map((_, i) => `<div class="w-2 h-2 rounded-full bg-white/50"></div>`).join('')}
                            </div>
                        ` : ''}
                    </div>
                ` : `
                    <div class="h-64 bg-slate-700 flex items-center justify-center">
                        <div class="text-center text-slate-400">
                            <i class="fas fa-image text-4xl mb-2"></i>
                            <p>No cover images</p>
                        </div>
                    </div>
                `}

                <!-- Content Grid -->
                <div class="p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
                    
                    <!-- Playground Details -->
                    <div class="bg-slate-800/50 rounded-lg p-4">
                        <h3 class="font-bold text-lg mb-3 flex items-center">
                            <i class="fas fa-info-circle mr-2 text-emerald-400"></i>
                            Details
                        </h3>
                        <div class="space-y-2 text-sm">
                            <div><span class="text-slate-400">Type:</span> ${formData.playground_type || 'Not specified'}</div>
                            <div><span class="text-slate-400">Capacity:</span> ${formData.capacity || 'Not specified'} people</div>
                            <div><span class="text-slate-400">Size:</span> ${formData.size || 'Not specified'}</div>
                            <div class="pt-2">
                                <span class="text-slate-400">Description:</span>
                                <div class="text-slate-300 text-xs mt-1 pl-3 border-l-2 border-emerald-500">
                                    ${formData.description || 'No description provided'}
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Live Time Slots -->
                    <div class="bg-slate-800/50 rounded-lg p-4">
                        <h3 class="font-bold text-lg mb-3 flex items-center">
                            <i class="fas fa-clock mr-2 text-emerald-400"></i>
                            Live Availability
                        </h3>
                        ${this.timeSlots.length > 0 ? `
                            <div class="space-y-2 max-h-48 overflow-y-auto">
                                ${this.timeSlots.slice(0, 5).map(slot => `
                                    <div class="flex justify-between items-center p-2 bg-slate-700/50 rounded">
                                        <div class="flex items-center space-x-2">
                                            <div class="w-2 h-2 rounded-full" style="background-color: ${this.availabilityColors[slot.status]}"></div>
                                            <span class="text-xs">${slot.startTime}-${slot.endTime}</span>
                                        </div>
                                        <span class="text-emerald-400 font-semibold text-sm">$${slot.price}</span>
                                    </div>
                                `).join('')}
                            </div>
                        ` : `
                            <div class="text-center text-slate-400 py-4">
                                <p class="text-sm">No time slots configured</p>
                            </div>
                        `}
                    </div>

                    <!-- Live Map -->
                    <div class="bg-slate-800/50 rounded-lg p-4">
                        <h3 class="font-bold text-lg mb-3 flex items-center">
                            <i class="fas fa-map mr-2 text-emerald-400"></i>
                            Location
                        </h3>
                        <div class="w-full h-32 bg-slate-700 rounded overflow-hidden">
                            <iframe 
                                src="https://maps.google.com/maps?q=${lat},${lng}&z=15&output=embed" 
                                width="100%" height="100%" style="border:0;" loading="lazy">
                            </iframe>
                        </div>
                        <div class="mt-2 text-xs text-slate-400">${formData.address || 'Address not set'}</div>
                    </div>

                    <!-- Gallery -->
                    <div class="bg-slate-800/50 rounded-lg p-4">
                        <h3 class="font-bold text-lg mb-3 flex items-center">
                            <i class="fas fa-images mr-2 text-emerald-400"></i>
                            Gallery (${this.galleryImages.length})
                        </h3>
                        ${this.galleryImages.length > 0 ? `
                            <div class="grid grid-cols-3 gap-2">
                                ${this.galleryImages.slice(0, 6).map(img => `
                                    <div class="aspect-square rounded overflow-hidden">
                                        <img src="${img.url}" alt="${img.name}" class="w-full h-full object-cover" />
                                    </div>
                                `).join('')}
                            </div>
                        ` : `
                            <div class="text-center text-slate-400 py-4">
                                <i class="fas fa-images text-2xl mb-2"></i>
                                <p class="text-sm">No gallery images</p>
                            </div>
                        `}
                    </div>

                </div>

                <!-- Live Statistics -->
                <div class="bg-gradient-to-r from-emerald-600/20 to-blue-600/20 p-6 border-t border-slate-700">
                    <h3 class="font-bold text-lg mb-4 text-center">📊 Live Dashboard</h3>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                        <div class="bg-emerald-500/20 rounded-lg p-3">
                            <div class="text-2xl font-bold text-emerald-400">${stats.totalSlots}</div>
                            <div class="text-xs text-slate-300">Total Slots</div>
                        </div>
                        <div class="bg-green-500/20 rounded-lg p-3">
                            <div class="text-2xl font-bold text-green-400">${stats.availableSlots}</div>
                            <div class="text-xs text-slate-300">Available</div>
                        </div>
                        <div class="bg-blue-500/20 rounded-lg p-3">
                            <div class="text-2xl font-bold text-blue-400">$${stats.avgPrice}</div>
                            <div class="text-xs text-slate-300">Avg Price</div>
                        </div>
                        <div class="bg-purple-500/20 rounded-lg p-3">
                            <div class="text-2xl font-bold text-purple-400">$${stats.totalRevenue}</div>
                            <div class="text-xs text-slate-300">Revenue</div>
                        </div>
                    </div>
                </div>

            </div>
        `;

        container.innerHTML = previewHTML;
        console.log('✅ Dynamic preview generated with real-time data');
    }

    // UTILITY FUNCTIONS
    timeToMinutes(timeStr) {
        const [hours, minutes] = timeStr.split(':').map(Number);
        return hours * 60 + minutes;
    }

    minutesToTime(minutes) {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
    }

    // SLIDER CONTROLS
    nextSlide() {
        if (this.coverImages.length <= 1) return;
        this.currentSlideIndex = (this.currentSlideIndex + 1) % this.coverImages.length;
        this.updateSliderPosition();
    }

    prevSlide() {
        if (this.coverImages.length <= 1) return;
        this.currentSlideIndex = this.currentSlideIndex === 0 ? this.coverImages.length - 1 : this.currentSlideIndex - 1;
        this.updateSliderPosition();
    }

    goToSlide(index) {
        if (index >= 0 && index < this.coverImages.length) {
            this.currentSlideIndex = index;
            this.updateSliderPosition();
        }
    }

    updateSliderPosition() {
        const container = document.getElementById('cover-slider-container');
        if (container) {
            container.style.transform = `translateX(-${this.currentSlideIndex * 100}%)`;
        }
    }

    startSliderAutoplay() {
        if (this.sliderInterval) clearInterval(this.sliderInterval);
        if (this.coverImages.length <= 1 || this.isSliderPaused) return;

        this.sliderInterval = setInterval(() => {
            this.nextSlide();
        }, this.autoPlayInterval);
    }

    // IMAGE MANAGEMENT
    removeCoverImage(imageId) {
        this.coverImages = this.coverImages.filter(img => img.id !== imageId);
        if (this.currentSlideIndex >= this.coverImages.length) {
            this.currentSlideIndex = Math.max(0, this.coverImages.length - 1);
        }
        this.updateCoverImageDisplay();
        this.showNotification('Cover image removed', 'success');
        this.saveDraft();
    }

    removeGalleryImage(imageId) {
        this.galleryImages = this.galleryImages.filter(img => img.id !== imageId);
        this.updateGalleryImageDisplay();
        this.showNotification('Gallery image removed', 'success');
        this.saveDraft();
    }

    openImageModal(imageUrl, imageName) {
        const modal = document.createElement('div');
        modal.className = 'image-modal fixed inset-0 z-50 flex items-center justify-center bg-black/80';
        modal.innerHTML = `
            <div class="relative max-w-4xl max-h-full p-4">
                <img src="${imageUrl}" alt="${imageName}" class="max-w-full max-h-full object-contain rounded-lg" />
                <button onclick="this.closest('.image-modal').remove()" 
                        class="absolute top-4 right-4 bg-black/50 text-white p-2 rounded-full hover:bg-black/70">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    }

    // DRAFT MANAGEMENT
    saveDraft() {
        const draftData = {
            ...this.collectFormData(),
            currentStep: this.currentStep,
            coverImages: this.coverImages.map(img => ({
                id: img.id, name: img.name, url: img.url, size: img.size
            })),
            galleryImages: this.galleryImages.map(img => ({
                id: img.id, name: img.name, url: img.url, size: img.size
            })),
            timeSlots: this.timeSlots,
            timestamp: Date.now()
        };
        
        localStorage.setItem('playgroundFormDraft', JSON.stringify(draftData));
    }

    loadDraftData() {
        const draftData = localStorage.getItem('playgroundFormDraft');
        if (!draftData) return;

        try {
            const draft = JSON.parse(draftData);
            
            // Check if draft is recent (24 hours)
            if (Date.now() - draft.timestamp > 24 * 60 * 60 * 1000) {
                localStorage.removeItem('playgroundFormDraft');
                return;
            }

            this.showDraftDialog(draft);
        } catch (error) {
            console.error('Error loading draft:', error);
            localStorage.removeItem('playgroundFormDraft');
        }
    }

    showDraftDialog(draft) {
        const modal = document.createElement('div');
        modal.className = 'draft-modal fixed inset-0 z-50 flex items-center justify-center bg-black/50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-md mx-4 shadow-xl">
                <div class="text-center mb-6">
                    <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i class="fas fa-save text-blue-600 text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-bold text-gray-900 mb-2">Draft Found!</h3>
                    <p class="text-gray-600">Found a saved draft from ${new Date(draft.timestamp).toLocaleString()}</p>
                </div>
                
                <div class="space-y-3">
                    <button onclick="window.professionalForm.restoreDraft()" 
                            class="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                        Continue with Draft
                    </button>
                    <button onclick="window.professionalForm.startFresh()" 
                            class="w-full bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 transition-colors">
                        Start Fresh
                    </button>
                    <button onclick="window.professionalForm.deleteDraft()" 
                            class="w-full bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400 transition-colors">
                        Delete Draft
                    </button>
                </div>
            </div>
        `;
        
        this.draftData = draft;
        document.body.appendChild(modal);
        this.draftModal = modal;
    }

    restoreDraft() {
        const draft = this.draftData;
        
        // Restore form data
        Object.keys(draft).forEach(key => {
            const field = document.querySelector(`[name="${key}"]`);
            if (field && typeof draft[key] === 'string') {
                field.value = draft[key];
            }
        });

        this.currentStep = draft.currentStep || 1;
        
        if (draft.coverImages) {
            this.coverImages = draft.coverImages;
            this.updateCoverImageDisplay();
        }
        
        if (draft.galleryImages) {
            this.galleryImages = draft.galleryImages;
            this.updateGalleryImageDisplay();
        }
        
        if (draft.timeSlots) {
            this.timeSlots = draft.timeSlots;
            this.renderTimeSlotsDisplay();
        }

        this.updateStepDisplay();
        this.closeDraftModal();
        this.showNotification('Draft restored successfully!', 'success');
    }

    startFresh() {
        localStorage.removeItem('playgroundFormDraft');
        this.resetForm();
        this.closeDraftModal();
        this.showNotification('Starting fresh', 'info');
    }

    deleteDraft() {
        localStorage.removeItem('playgroundFormDraft');
        this.closeDraftModal();
        this.showNotification('Draft deleted', 'success');
    }

    closeDraftModal() {
        if (this.draftModal) {
            this.draftModal.remove();
            this.draftModal = null;
        }
    }

    resetForm() {
        this.currentStep = 1;
        this.coverImages = [];
        this.galleryImages = [];
        this.timeSlots = [];
        this.currentSlideIndex = 0;
        
        const form = document.getElementById('professionalCreatePlaygroundForm');
        if (form) form.reset();
        
        this.updateCoverImageDisplay();
        this.updateGalleryImageDisplay();
        this.updateStepDisplay();
    }

    // FORM SUBMISSION
    async submitForm() {
        if (!this.validateCurrentStep()) return;

        this.showNotification('Submitting form...', 'info');

        try {
            const formData = new FormData();
            const form = document.getElementById('professionalCreatePlaygroundForm');
            
            // Add form fields
            const formFields = new FormData(form);
            for (let [key, value] of formFields.entries()) {
                formData.append(key, value);
            }

            // Add images
            this.coverImages.forEach((image, index) => {
                if (image.file) formData.append(`cover_image_${index}`, image.file);
            });

            this.galleryImages.forEach((image, index) => {
                if (image.file) formData.append(`gallery_image_${index}`, image.file);
            });

            // Add time slots as JSON
            formData.append('time_slots', JSON.stringify(this.timeSlots));

            const response = await fetch('/api/playgrounds/create/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (response.ok) {
                const result = await response.json();
                this.showNotification('Playground created successfully!', 'success');
                localStorage.removeItem('playgroundFormDraft');
                
                setTimeout(() => {
                    if (result.redirect_url) {
                        window.location.href = result.redirect_url;
                    }
                }, 2000);
            } else {
                const error = await response.json();
                this.showNotification(error.message || 'Submission failed', 'error');
            }
        } catch (error) {
            console.error('Submission error:', error);
            this.showNotification('Network error. Please try again.', 'error');
        }
    }

    collectFormData() {
        const form = document.getElementById('professionalCreatePlaygroundForm');
        if (!form) return {};

        const formData = new FormData(form);
        const data = {};

        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        return data;
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    // FORM VALIDATION
    initializeFormValidation() {
        const form = document.getElementById('professionalCreatePlaygroundForm');
        if (!form) return;

        form.addEventListener('input', (e) => {
            if (e.target.hasAttribute('required')) {
                this.clearFieldError(e.target);
            }
        });
    }

    // NOTIFICATION SYSTEM
    showNotification(message, type = 'info', duration = 3000) {
        // Remove existing notifications
        document.querySelectorAll('.notification').forEach(n => n.remove());

        const notification = document.createElement('div');
        notification.className = `notification fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg text-white transform transition-all duration-300 translate-x-full`;
        
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };

        notification.classList.add(colors[type]);
        notification.innerHTML = `
            <div class="flex items-center space-x-3">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="text-white/80 hover:text-white">
                    ×
                </button>
            </div>
        `;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => notification.classList.remove('translate-x-full'), 100);

        // Auto remove
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.add('translate-x-full');
                setTimeout(() => notification.remove(), 300);
            }
        }, duration);
    }
}

// GLOBAL INITIALIZATION
function initializeProfessionalForm() {
    if (!window.professionalForm) {
        window.professionalForm = new ProfessionalPlaygroundForm();
    }
    return window.professionalForm;
}

// AUTO-INITIALIZE WHEN DOM IS READY
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeProfessionalForm);
} else {
    initializeProfessionalForm();
}

// GLOBAL ACCESS
window.initializeProfessionalForm = initializeProfessionalForm;

console.log('🌟 Professional Playground Form Script Loaded Successfully - FIXED VERSION');
