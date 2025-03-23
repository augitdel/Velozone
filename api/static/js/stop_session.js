let decision = null;
let decision_bool = null;

// Function to set decision (yes or no)
function setDecision(choice) {
    decision = choice;
    if (choice === 'yes') {
        document.getElementById('yesButton').classList.remove('btn-custom');
        document.getElementById('yesButton').classList.add('btn-yes');
        document.getElementById('noButton').classList.remove('btn-no');
        document.getElementById('noButton').classList.add('btn-custom');
        decision_bool = 'true';
        console.log(decision_bool);
    } else if (choice === 'no') {
        document.getElementById('noButton').classList.remove('btn-custom');
        document.getElementById('noButton').classList.add('btn-no');
        document.getElementById('yesButton').classList.remove('btn-yes');
        document.getElementById('yesButton').classList.add('btn-custom');
        decision_bool = 'false';
        console.log(decision_bool);
    }
}

// Function to stop the session
function stopCompetition() { 
    fetch("/stop_session", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
        decision: decision_bool
        })
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url; 
        } else {
            document.getElementById("stopMessage").classList.remove("hidden");
            document.getElementById("homeButton").classList.remove("hidden");
        }
    })
    .catch(error => console.error("Error stopping session:", error));
}