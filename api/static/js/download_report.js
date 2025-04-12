function checkPDF() {
    console.log("Checking PDF status..."); // Debugging log

    fetch('/check_pdf_status')
        .then(response => {
            console.log("Response received", response);
            return response.json();
        })
        .then(data => {
            console.log("Data received", data);

            if (data.status === "ready") {
                document.getElementById("loading-text").style.display = "none";
                document.getElementById("bike-loader").style.display = "none"; 
                document.getElementById("title").textContent = "Report Generation DONE!";

                let downloadBtn = document.getElementById("download-btn");
                downloadBtn.style.display = "block";
                downloadBtn.onclick = function() {
                    window.location.href = "/download_pdf";
                };
            } else {
                console.log("PDF not ready, retrying...");
                setTimeout(checkPDF, 2000); // Retry after 2 seconds
            }
        })
        .catch(error => console.error("Error fetching PDF status:", error));
}

window.onload = function () {
    console.log("Window loaded, starting checkPDF()...");
    checkPDF();
};