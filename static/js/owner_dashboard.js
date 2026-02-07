/**
 * Owner Dashboard JavaScript
 * Handles all real-time functionality, API calls, and user interactions
 */

class OwnerDashboard {
    constructor() {
        this.updateInterval = null;
        this.notificationInterval = null;
        this.wsConnection = null;
        this.currentPlaygroundId = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.startRealTimeUpdates();
        this.initializeWebSocket();
    }
    
    setupEventListeners() {
        // Dashboard refresh
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.refreshDashboard();
            }
        });
        
        // Search functionality
        const searchInput = document.getElementById('dashboardSearch');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(this.handleSearch.bind(this), 300));
        }
        
        // Filter handlers
        document.querySelectorAll('[data-filter]').forEach(filter => {
            filter.addEventListener('change', this.handleFilterChange.bind(this));
        });
        
        // Quick action buttons
        document.querySelectorAll('[data-action]').forEach(button => {
            button.addEventListener('click', this.handleQuickAction.bind(this));
        });
    }
    
    loadInitialData() {
        this.loadDashboardStats();
        this.loadTodaysSchedule();
        this.loadPendingBookings();
        this.loadNotifications();
        this.loadPlaygrounds();
    }
    
    startRealTimeUpdates() {
        // Update dashboard stats every 30 seconds
        this.updateInterval = setInterval(() => {
            this.loadDashboardStats();
            this.updateTimeSlots();
        }, 30000);
        
        // Update notifications every 15 seconds
        this.notificationInterval = setInterval(() => {
            this.loadNotifications();
        }, 15000);
    }
    
    initializeWebSocket() {
        // WebSocket for real-time updates
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/owner/dashboard/`;
        
        try {
            this.wsConnection = new WebSocket(wsUrl);
            
            this.wsConnection.onopen = () => {
                console.log('WebSocket connected');
                this.showNotification('Connected to real-time updates', 'success');
            };
            
            this.wsConnection.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.wsConnection.onclose = () => {
                console.log('WebSocket disconnected');
                // Attempt to reconnect after 5 seconds
                setTimeout(() => {
                    this.initializeWebSocket();
                }, 5000);
            };
            
            this.wsConnection.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        } catch (error) {
            console.log('WebSocket not available, using polling fallback');
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'booking_update':
                this.handleBookingUpdate(data.data);
                break;
            case 'new_booking':
                this.handleNewBooking(data.data);
                break;
            case 'payment_update':
                this.handlePaymentUpdate(data.data);
                break;
            case 'notification':
                this.handleNewNotification(data.data);
                break;
            default:
                console.log('Unknown WebSocket message type:', data.type);
        }
    }
    
    async loadDashboardStats() {
        try {
            const response = await this.apiCall('/api/owner/dashboard-stats/');
            if (response.success) {
                this.updateDashboardStats(response.stats, response.revenue);
                this.updateRecentActivity(response.recent_activity);
            }
        } catch (error) {
            console.error('Error loading dashboard stats:', error);
        }
    }
    
    updateDashboardStats(stats, revenue) {
        // Update stat cards
        this.updateStatCard('totalPlaygrounds', stats.total_playgrounds);
        this.updateStatCard('monthlyBookings', stats.monthly_bookings);
        this.updateStatCard('pendingBookings', stats.pending_bookings);
        this.updateStatCard('monthlyRevenue', '₹' + (revenue.monthly_revenue || 0).toLocaleString());
        
        // Update progress bars and growth indicators
        this.updateGrowthIndicators(stats, revenue);
    }
    
    updateStatCard(elementId, value, trend = null) {
        const element = document.getElementById(elementId);
        if (element) {
            // Animate number change
            this.animateNumber(element, value);
            
            // Update trend indicator if provided
            if (trend) {
                const trendElement = element.parentElement.querySelector('.trend-indicator');
                if (trendElement) {
                    trendElement.textContent = trend;
                    trendElement.className = `trend-indicator ${trend > 0 ? 'positive' : trend < 0 ? 'negative' : 'neutral'}`;
                }
            }
        }
    }
    
    animateNumber(element, targetValue) {
        const currentValue = parseInt(element.textContent.replace(/[^0-9]/g, '')) || 0;
        const isString = typeof targetValue === 'string';
        const target = isString ? parseInt(targetValue.replace(/[^0-9]/g, '')) : targetValue;
        
        if (currentValue === target) return;
        
        const duration = 1000; // 1 second
        const steps = 20;
        const increment = (target - currentValue) / steps;
        const stepDuration = duration / steps;
        
        let current = currentValue;
        const timer = setInterval(() => {
            current += increment;
            
            if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
                current = target;
                clearInterval(timer);
            }
            
            if (isString) {
                const prefix = targetValue.match(/^[^0-9]*/)[0];
                const suffix = targetValue.match(/[^0-9]*$/)[0];
                element.textContent = prefix + Math.round(current).toLocaleString() + suffix;
            } else {
                element.textContent = Math.round(current).toLocaleString();
            }
        }, stepDuration);
    }
    
    async loadTodaysSchedule() {
        try {
            const response = await this.apiCall('/api/owner/todays-schedule/');
            if (response.success) {
                this.updateTodaysSchedule(response.schedule);
            }
        } catch (error) {
            console.error('Error loading today\'s schedule:', error);
        }
    }
    
    updateTodaysSchedule(schedule) {
        const container = document.getElementById('todaysSchedule');
        if (!container) return;
        
        if (schedule.length === 0) {
            container.innerHTML = this.getEmptyState('calendar-times', 'No bookings for today');
            return;
        }
        
        container.innerHTML = schedule.map(booking => {
            const statusClass = this.getStatusClass(booking.status);
            return `
                <div class="schedule-item bg-white/5 border border-white/10 rounded-xl p-4 hover:bg-white/10 transition-all duration-300">
                    <div class="flex justify-between items-start mb-2">
                        <h4 class="font-semibold text-white">${booking.playground_name}</h4>
                        <span class="status-badge ${statusClass}">${booking.status}</span>
                    </div>
                    <p class="text-gray-300 text-sm">${booking.user_name}</p>
                    <div class="flex justify-between items-center mt-2">
                        <span class="text-blue-300 text-sm">
                            <i class="fas fa-clock mr-1"></i>
                            ${booking.start_time} - ${booking.end_time}
                        </span>
                        <span class="text-green-300 font-medium">₹${booking.amount}</span>
                    </div>
                    <div class="mt-2 flex space-x-2">
                        <button onclick="viewBookingDetails('${booking.id}')" class="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded">
                            View Details
                        </button>
                        ${booking.status === 'pending' ? `
                            <button onclick="quickApprove('${booking.id}')" class="text-xs bg-green-500/20 text-green-300 px-2 py-1 rounded">
                                Quick Approve
                            </button>
                        ` : ''}
                    </div>
                </div>
            `;
        }).join('');
    }
    
    async loadPendingBookings() {
        try {
            const response = await this.apiCall('/api/owner/pending-bookings/');
            if (response.success) {
                this.updatePendingBookings(response.bookings);
                this.updatePendingCount(response.count);
            }
        } catch (error) {
            console.error('Error loading pending bookings:', error);
        }
    }
    
    updatePendingBookings(bookings) {
        const container = document.getElementById('pendingBookingsList');
        if (!container) return;
        
        if (bookings.length === 0) {
            container.innerHTML = this.getEmptyState('check-circle', 'All caught up!', 'text-green-400');
            return;
        }
        
        container.innerHTML = bookings.map(booking => `
            <div class="pending-booking bg-white/5 border border-white/10 rounded-xl p-4 hover:bg-white/10 transition-all duration-300">
                <div class="flex justify-between items-start mb-2">
                    <h4 class="font-semibold text-white">${booking.playground_name}</h4>
                    <span class="text-yellow-300 text-sm">
                        <i class="fas fa-clock"></i> Pending
                    </span>
                </div>
                <p class="text-gray-300 text-sm">${booking.user_name}</p>
                <p class="text-blue-300 text-sm">${booking.booking_date} • ${booking.start_time}-${booking.end_time}</p>
                ${booking.special_requests ? `
                    <p class="text-yellow-200 text-xs mt-1 italic">
                        <i class="fas fa-comment"></i> ${booking.special_requests.substring(0, 50)}...
                    </p>
                ` : ''}
                <div class="flex justify-between items-center mt-3">
                    <span class="text-green-300 font-medium">₹${booking.final_amount}</span>
                    <div class="flex space-x-2">
                        <button onclick="approveBooking(${booking.id})" class="approve-btn bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-xs font-medium transition-colors">
                            <i class="fas fa-check mr-1"></i>Approve
                        </button>
                        <button onclick="rejectBooking(${booking.id})" class="reject-btn bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-xs font-medium transition-colors">
                            <i class="fas fa-times mr-1"></i>Reject
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    updatePendingCount(count) {
        const badge = document.getElementById('pendingCount');
        if (badge) {
            badge.textContent = count;
            badge.classList.toggle('hidden', count === 0);
        }
        
        // Update notification badge
        const notificationBadge = document.getElementById('notificationBadge');
        if (notificationBadge && count > 0) {
            notificationBadge.textContent = count;
            notificationBadge.classList.remove('hidden');
        }
    }
    
    async loadNotifications() {
        try {
            const response = await this.apiCall('/api/owner/notifications/');
            if (response.success) {
                this.updateNotifications(response.notifications, response.unread_count);
            }
        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    }
    
    updateNotifications(notifications, unreadCount) {
        const badge = document.getElementById('notificationBadge');
        const list = document.getElementById('notificationList');
        
        if (badge) {
            if (unreadCount > 0) {
                badge.textContent = unreadCount;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
        }
        
        if (list) {
            if (notifications.length === 0) {
                list.innerHTML = '<p class="text-gray-500 text-center py-4">No notifications</p>';
            } else {
                list.innerHTML = notifications.map(notification => `
                    <div class="notification-item p-3 rounded-lg bg-gray-50 border-l-4 ${this.getNotificationBorderColor(notification.type)} hover:bg-gray-100 transition-colors cursor-pointer"
                         onclick="markNotificationAsRead('${notification.id}')">
                        <div class="flex justify-between items-start mb-1">
                            <h4 class="font-medium text-gray-800">${notification.title}</h4>
                            <span class="text-xs text-gray-500">${this.formatTime(notification.created_at)}</span>
                        </div>
                        <p class="text-sm text-gray-600">${notification.message}</p>
                        ${!notification.is_read ? '<div class="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>' : ''}
                    </div>
                `).join('');
            }
        }
    }
    
    getNotificationBorderColor(type) {
        switch (type) {
            case 'booking_confirmed':
                return 'border-green-500';
            case 'booking_rejected':
                return 'border-red-500';
            case 'pending_bookings':
                return 'border-yellow-500';
            case 'payment_received':
                return 'border-blue-500';
            default:
                return 'border-gray-500';
        }
    }
    
    async loadPlaygrounds() {
        try {
            const response = await this.apiCall('/api/owner/playgrounds/');
            if (response.success) {
                this.updatePlaygroundsList(response.playgrounds);
            }
        } catch (error) {
            console.error('Error loading playgrounds:', error);
        }
    }
    
    updateTimeSlots() {
        // Update time slot availability in real-time
        this.loadRealTimeAvailability();
    }
    
    async loadRealTimeAvailability() {
        try {
            const response = await this.apiCall('/api/owner/real-time-availability/');
            if (response.success) {
                this.updateAvailabilityDisplay(response.availability);
            }
        } catch (error) {
            console.error('Error loading real-time availability:', error);
        }
    }
    
    updateAvailabilityDisplay(availability) {
        // Update availability indicators on the dashboard
        availability.forEach(slot => {
            const element = document.querySelector(`[data-slot-id="${slot.id}"]`);
            if (element) {
                element.classList.toggle('available', slot.is_available);
                element.classList.toggle('booked', !slot.is_available);
            }
        });
    }
    
    // Booking management methods
    async approveBooking(bookingId, ownerNotes = '') {
        try {
            const response = await this.apiCall(`/api/owner/approve-booking/${bookingId}/`, 'POST', {
                owner_notes: ownerNotes
            });
            
            if (response.success) {
                this.showNotification('Booking approved successfully!', 'success');
                this.refreshBookingData();
                this.playNotificationSound('success');
            } else {
                this.showNotification(response.message || 'Error approving booking', 'error');
            }
        } catch (error) {
            console.error('Error approving booking:', error);
            this.showNotification('Error approving booking', 'error');
        }
    }
    
    async rejectBooking(bookingId, reason = '') {
        try {
            const response = await this.apiCall(`/api/owner/reject-booking/${bookingId}/`, 'POST', {
                rejection_reason: reason
            });
            
            if (response.success) {
                this.showNotification('Booking rejected successfully!', 'success');
                this.refreshBookingData();
            } else {
                this.showNotification(response.message || 'Error rejecting booking', 'error');
            }
        } catch (error) {
            console.error('Error rejecting booking:', error);
            this.showNotification('Error rejecting booking', 'error');
        }
    }
    
    refreshBookingData() {
        this.loadDashboardStats();
        this.loadTodaysSchedule();
        this.loadPendingBookings();
    }
    
    refreshDashboard() {
        this.loadInitialData();
    }
    
    // Utility methods
    async apiCall(url, method = 'GET', data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        };
        
        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        return await response.json();
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    
    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg text-white transform translate-x-full transition-transform duration-300 ${this.getNotificationClass(type)}`;
        
        notification.innerHTML = `
            <div class="flex items-center space-x-2">
                <i class="fas ${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-white/80 hover:text-white">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);
        
        // Auto-hide notification
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.parentElement.removeChild(notification);
                }
            }, 300);
        }, duration);
    }
    
    getNotificationClass(type) {
        switch (type) {
            case 'success':
                return 'bg-green-500';
            case 'error':
                return 'bg-red-500';
            case 'warning':
                return 'bg-yellow-500';
            default:
                return 'bg-blue-500';
        }
    }
    
    getNotificationIcon(type) {
        switch (type) {
            case 'success':
                return 'fa-check-circle';
            case 'error':
                return 'fa-exclamation-circle';
            case 'warning':
                return 'fa-exclamation-triangle';
            default:
                return 'fa-info-circle';
        }
    }
    
    getStatusClass(status) {
        switch (status) {
            case 'confirmed':
                return 'bg-green-100 text-green-800';
            case 'pending':
                return 'bg-yellow-100 text-yellow-800';
            case 'completed':
                return 'bg-blue-100 text-blue-800';
            case 'cancelled':
                return 'bg-red-100 text-red-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    }
    
    getEmptyState(icon, message, iconClass = 'text-gray-400') {
        return `
            <div class="text-center py-6">
                <i class="fas fa-${icon} ${iconClass} text-3xl mb-3"></i>
                <p class="text-gray-300">${message}</p>
            </div>
        `;
    }
    
    formatTime(timestamp) {
        return new Date(timestamp).toLocaleDateString();
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    playNotificationSound(type) {
        // Play subtle notification sound
        try {
            const audio = new Audio(`/static/sounds/notification-${type}.mp3`);
            audio.volume = 0.3;
            audio.play().catch(() => {
                // Ignore audio play errors (browser restrictions)
            });
        } catch (error) {
            // Ignore audio errors
        }
    }
    
    // Event handlers
    handleSearch(event) {
        const query = event.target.value.toLowerCase();
        // Implement search functionality
        console.log('Searching for:', query);
    }
    
    handleFilterChange(event) {
        const filter = event.target.dataset.filter;
        const value = event.target.value;
        // Implement filter functionality
        console.log('Filter changed:', filter, value);
    }
    
    handleQuickAction(event) {
        const action = event.target.dataset.action;
        switch (action) {
            case 'refresh':
                this.refreshDashboard();
                break;
            case 'export':
                this.exportData();
                break;
            default:
                console.log('Unknown action:', action);
        }
    }
    
    // WebSocket event handlers
    handleBookingUpdate(data) {
        this.refreshBookingData();
        this.showNotification(`Booking ${data.status}`, 'info');
    }
    
    handleNewBooking(data) {
        this.refreshBookingData();
        this.showNotification(`New booking received for ${data.playground_name}`, 'success');
        this.playNotificationSound('new-booking');
    }
    
    handlePaymentUpdate(data) {
        this.refreshBookingData();
        this.showNotification(`Payment ${data.status} for booking ${data.booking_id}`, 'info');
    }
    
    handleNewNotification(data) {
        this.loadNotifications();
        this.showNotification(data.message, 'info');
    }
    
    // Cleanup
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        if (this.notificationInterval) {
            clearInterval(this.notificationInterval);
        }
        
        if (this.wsConnection) {
            this.wsConnection.close();
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.ownerDashboard = new OwnerDashboard();
});

// Global functions for template compatibility
function approveBooking(bookingId) {
    const ownerNotes = prompt('Add any notes for the customer (optional):');
    window.ownerDashboard.approveBooking(bookingId, ownerNotes || '');
}

function rejectBooking(bookingId) {
    const reason = prompt('Please provide a reason for rejection:');
    if (reason) {
        window.ownerDashboard.rejectBooking(bookingId, reason);
    }
}

function quickApprove(bookingId) {
    if (confirm('Are you sure you want to approve this booking?')) {
        window.ownerDashboard.approveBooking(bookingId);
    }
}

function viewBookingDetails(bookingId) {
    // Open booking details modal
    console.log('Viewing booking details for:', bookingId);
}

function markNotificationAsRead(notificationId) {
    // Mark notification as read
    console.log('Marking notification as read:', notificationId);
}

// Real-time features
function enableRealTimeMode() {
    document.body.classList.add('real-time-mode');
    console.log('Real-time mode enabled');
}

function disableRealTimeMode() {
    document.body.classList.remove('real-time-mode');
    console.log('Real-time mode disabled');
}

// Export functionality
function exportDashboardData() {
    console.log('Exporting dashboard data...');
    // Implement export functionality
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.ownerDashboard) {
        window.ownerDashboard.destroy();
    }
});
