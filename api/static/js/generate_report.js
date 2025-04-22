document.addEventListener('DOMContentLoaded', function () {
    const generateBtn = document.getElementById('generate-btn');
    const riderSelect = document.getElementById('rider-select');
    const loadingOverlay = document.getElementById('loadingOverlay');

    if (!generateBtn) return;

    generateBtn.addEventListener('click', function(event) {
        event.preventDefault();
    
        const selectedRiderName = riderSelect.value;
        console.log('Selected rider (frontend):', selectedRiderName);
    
        // Show loading screen
        const loadingScreen = document.getElementById('loading-screen');
        loadingScreen.classList.remove('d-none');
    
        fetch("/generate_report", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rider_name: selectedRiderName })
        })
        .then(response => {
            if (!response.ok) {
                console.error('POST request failed:', response.status);
            }
            window.location.href = "/download_report";
        })
        .catch(error => {
            console.error('Fetch error:', error);
            window.location.href = "/download_report";
        });
    });    
});