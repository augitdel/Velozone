function checkPDF() {
    fetch('/check_pdf_status')
        .then(response => response.json())
        .then(data => {
            if (data.status === "ready") {
                // Hide loader and text
                document.getElementById("loading-text").style.display = "none";
                document.getElementById("bike-loader").style.display = "none"; 
                document.getElementById("title").textContent = "Report Generation DONE!"
                // Show download button
                let downloadBtn = document.getElementById("download-btn");
                downloadBtn.style.display = "block";
                downloadBtn.onclick = function() {
                    window.location.href = "/download_pdf";
                };
            } else {
                setTimeout(checkPDF, 2000); // Retry after 2 seconds
            }
            
        });
}

window.onload = function () {
    checkPDF();
};