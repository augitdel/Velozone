function stopCompetition() {
    const generatePDF = document.getElementById("generatePDF").checked;

    fetch("/stop_session", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ generatePDF: generatePDF ? "on" : "off" })
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url; // Redirect naar home of andere pagina
        } else {
            document.getElementById("stopMessage").classList.remove("hidden");
            document.getElementById("homeButton").classList.remove("hidden");
        }
    })
    .catch(error => console.error("Error stopping session:", error));
}
