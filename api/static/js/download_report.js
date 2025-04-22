window.onload = function () {
    console.log("Window loaded, setting up download button...");

    let downloadBtn = document.getElementById("download-btn");
    downloadBtn.onclick = function () {
        console.log("Download button clicked, redirecting...");
        window.location.href = "/download_pdf";
    };

};
