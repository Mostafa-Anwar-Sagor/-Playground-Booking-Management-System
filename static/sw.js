// Service Worker for Playground Booking PWA
const CACHE_NAME = 'playground-booking-v1';
const urlsToCache = [
    '/',
    '/static/css/tailwind.min.css',
    '/static/js/app.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            }
        )
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Background sync for offline form submissions
self.addEventListener('sync', (event) => {
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

async function doBackgroundSync() {
    // Handle offline form submissions when back online
    try {
        const pendingRequests = await getPendingRequests();
        for (const request of pendingRequests) {
            await fetch(request.url, {
                method: request.method,
                body: request.body,
                headers: request.headers
            });
        }
        await clearPendingRequests();
    } catch (error) {
        console.error('Background sync failed:', error);
    }
}

function getPendingRequests() {
    return new Promise((resolve) => {
        // Get pending requests from IndexedDB or localStorage
        const requests = JSON.parse(localStorage.getItem('pendingRequests') || '[]');
        resolve(requests);
    });
}

function clearPendingRequests() {
    localStorage.removeItem('pendingRequests');
}

// Push notifications
self.addEventListener('push', (event) => {
    const options = {
        body: event.data ? event.data.text() : 'New playground available!',
        icon: '/static/img/icon-192x192.png',
        badge: '/static/img/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: '1'
        },
        actions: [
            {
                action: 'explore',
                title: 'Explore',
                icon: '/static/img/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/img/xmark.png'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('Playground Booking', options)
    );
});

// Notification click
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});
