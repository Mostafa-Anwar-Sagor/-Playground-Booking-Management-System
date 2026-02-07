// partner_register.js
// Handles dynamic country/state/city dropdowns and file input validation for partner registration

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const countrySelect = document.getElementById('country');
    const stateSelect = document.getElementById('state');
    const citySelect = document.getElementById('city');
    const galleryInput = document.getElementById('gallery');
    const videosInput = document.getElementById('videos');
    const galleryLabel = document.querySelector('label[for="gallery"]');
    const videosLabel = document.querySelector('label[for="videos"]');

    // Helper to clear and populate select
    function populateSelect(select, items, placeholder) {
        select.innerHTML = '';
        const option = document.createElement('option');
        option.value = '';
        option.textContent = placeholder;
        select.appendChild(option);
        items.forEach(item => {
            const opt = document.createElement('option');
            opt.value = item.id;
            opt.textContent = item.name;
            select.appendChild(opt);
        });
    }

    // Country -> State
    if (countrySelect) {
        countrySelect.addEventListener('change', function() {
            const countryId = this.value;
            if (!countryId) {
                populateSelect(stateSelect, [], 'Select state');
                populateSelect(citySelect, [], 'Select city');
                return;
            }
            fetch(`/playgrounds/ajax/get-states/?country_id=${countryId}`)
                .then(res => res.json())
                .then(data => {
                    populateSelect(stateSelect, data.states, 'Select state');
                    populateSelect(citySelect, [], 'Select city');
                });
        });
    }

    // State -> City
    if (stateSelect) {
        stateSelect.addEventListener('change', function() {
            const stateId = this.value;
            if (!stateId) {
                populateSelect(citySelect, [], 'Select city');
                return;
            }
            fetch(`/playgrounds/ajax/get-cities/?state_id=${stateId}`)
                .then(res => res.json())
                .then(data => {
                    populateSelect(citySelect, data.cities, 'Select city');
                });
        });
    }

    // Gallery images validation (max 6)
    if (galleryInput) {
        galleryInput.addEventListener('change', function() {
            if (this.files.length > 6) {
                alert('You can upload a maximum of 6 images.');
                this.value = '';
            }
        });
    }

    // Videos validation (optional, max 2, max 5min each)
    if (videosInput) {
        videosInput.addEventListener('change', function() {
            if (this.files.length > 2) {
                alert('You can upload a maximum of 2 videos.');
                this.value = '';
                return;
            }
            // Check video duration (max 5min = 300s)
            const files = Array.from(this.files);
            let checked = 0;
            files.forEach(file => {
                const url = URL.createObjectURL(file);
                const video = document.createElement('video');
                video.preload = 'metadata';
                video.onloadedmetadata = function() {
                    URL.revokeObjectURL(url);
                    if (video.duration > 300) {
                        alert('Each video must be 5 minutes (300 seconds) or less.');
                        videosInput.value = '';
                    }
                    checked++;
                };
                video.src = url;
            });
        });
    }
});
