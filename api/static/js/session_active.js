const sessionIndicator = document.getElementById('session-indicator');
function checkSessionStatus() {
    fetch('/api/sessions/active')
        .then(response => response.json())
        .then(data => {
            if (data.isActive) {
                sessionIndicator.classList.add('active');
                sessionIndicator.classList.remove('inactive');
            } else {
                sessionIndicator.classList.add('inactive');
                sessionIndicator.classList.remove('active');
            }
        })
        .catch(error => console.error('Error checking session status:', error));
}

// Check session status every 3 seconds (adjust the interval as needed)
setInterval(checkSessionStatus, 3000);

// Initial check when the page loads
checkSessionStatus();