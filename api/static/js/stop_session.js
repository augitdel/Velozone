let decision = null;
let decision_bool = null;

function stopCompetition() {
    fetch('/stop_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ decision: 'true' })
    })
    .then(response => response.text()) // Controleer of de server reageert
    .then(data => {
        console.log("Server response:", data);
        window.location.href = "/home"; // Redirect pas na verwerking
    })
    .catch(error => console.error("Error stopping session:", error));
}

function showStopConfirmation() {
    if (confirm("Are you sure you want to stop the session?")) {
        stopCompetition();
    }
}
