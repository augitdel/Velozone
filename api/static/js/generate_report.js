document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generate-btn');
    const riderSelect = document.getElementById('rider-select');

    generateBtn.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent the default form submission

        const selectedRiderName = riderSelect.value;
        console.log('Selected rider (frontend):', selectedRiderName);

        // Send the POST request to the backend to trigger report generation
        fetch("/generate_report", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json' 
            },
            body: JSON.stringify({ rider_name: selectedRiderName })
        })
        .then(response => {
            if (!response.ok) {
                console.error('POST request failed:', response.status);
            }
            // Even if the POST request is still processing, immediately redirect to the download report page
            window.location.href = "/download_report";
        })
        .catch(error => {
            console.error('There was an error with the fetch operation:', error);
            // Optionally display an error message to the user
            window.location.href = "/download_report"; // Redirect even if there's a fetch error (you might want to adjust this)
        });
    });
});