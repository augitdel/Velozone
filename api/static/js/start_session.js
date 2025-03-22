// Flatpickr for date and time selection
flatpickr("#startDate", { dateFormat: "Y-m-d", altInput: true, altFormat: "F j, Y" });
flatpickr("#startTime", { enableTime: true, noCalendar: true, dateFormat: "H:i", time_24hr: true });

function startCompetition() {
    // Get form values
    const startDate = document.getElementById('startDate').value;
    const startTime = document.getElementById('startTime').value;
    const duration = document.getElementById('duration').value;
    const participants = document.getElementById('participants').value;

    // Check if all fields are filled in
    if (!startDate || !startTime || !duration || !participants) {
        document.getElementById('error').classList.remove('hidden');
        return; // Stop further execution if form is invalid
    }

    // Hide the error message if the form is valid
    document.getElementById('error').classList.add('hidden');
            
    // Send a POST request with the form data to Flask
    fetch('/start_session', {
        method: 'POST',
        body: new URLSearchParams({
            startDate: startDate,
            startTime: startTime,
            duration: duration,
            participants: participants
        }),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    })
    .then(response => {
        if (response.ok) {
            // After successful POST, display action buttons
            document.getElementById('actionButtons').classList.remove('hidden');
        } else {
            console.error("Error in starting competition.");
        }
    })
    .catch(error => console.error("Error:", error));
}
