// Flatpickr alleen voor tijdselectie
flatpickr("#startTime", { enableTime: true, noCalendar: true, dateFormat: "H:i", time_24hr: true });

function startCompetition() {
    // Huidige datum genereren in "YYYY-MM-DD" formaat
    const today = new Date().toISOString().split("T")[0];
    
    // Form-waarden ophalen
    const groupName = document.getElementById("groupName").value;
    const startTime = document.getElementById("startTime").value;
    const duration = document.getElementById("duration").value;
    const participants = document.getElementById("participants").value;

    // Check of alle velden zijn ingevuld
    if (!startTime || !duration || !participants) {
        document.getElementById("error").classList.remove("hidden");
        return;
    }

    // Verberg foutmelding als alles correct is ingevuld
    document.getElementById("error").classList.add("hidden");

    // POST-verzoek naar de Flask backend
    fetch("/start_session", {
        method: "POST",
        body: new URLSearchParams({
            startDate: today,  // Automatisch gegenereerde datum
            startTime: startTime,
            duration: duration,
            participants: participants,
            groupName: groupName
        }),
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        }
    })
    .then(response => {
        if (response.ok) {
            document.getElementById("actionButtons").classList.remove("hidden");
        } else {
            console.error("Fout bij starten van de wedstrijd.");
        }
    })
    .catch(error => console.error("Error:", error));
}

