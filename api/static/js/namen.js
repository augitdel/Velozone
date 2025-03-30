const transponderData = [
    ["FF30660", "Jesus"], ["GN87210", "Brian"], ["GR11874", "Mark"], ["GT49254", "Emily"], ["PX83485", "David"],
    ["RR01344", "Charles"], ["RZ04998", "Megan"], ["RZ13738", "Maria"], ["SC98900", "Charles"], ["SF16020", "Jessica"],
    ["CS34132", "Tracey"], ["CR48188", "Andrea"], ["RZ10761", "Heather"], ["KT68858", "Jason"], ["HC20410", "Michael"],
    ["NS43328", "Tyler"], ["RR15537", "Amanda"], ["RZ43503", "James"], ["LZ73964", "Kristin"], ["KP55121", "Lisa"],
    ["CW09719", "Michelle"], ["SF04172", "Joshua"], ["RR10973", "James"], ["HH54287", "Patricia"], ["RR18114", "Debbie"],
    ["KP31430", "Kathleen"], ["PF79070", "Brandy"], ["RF48933", "Debbie"], ["LR40395", "Shane"], ["RZ02081", "Robert"],
    ["GK67167", "George"], ["CX19285", "Tracie"], ["SC75193", "Christopher"], ["RZ39892", "Richard"], ["RX72266", "Victor"],
    ["FW08700", "Kevin"], ["VG76471", "Cody"], ["KR51169", "William"], ["NK39779", "Douglas"], ["RZ41573", "Jennifer"],
    ["RX45371", "Lisa"], ["SC90979", "Timothy"], ["GZ52385", "Sean"], ["SF17035", "Catherine"], ["CC16014", "Ryan"],
    ["CS75905", "Melinda"], ["CT28904", "Nicole"], ["CT87815", "Michelle"], ["CT92889", "David"], ["CT96975", "Tasha"],
    ["CX12515", "Randy"], ["CX49214", "Jessica"], ["FF79131", "Renee"], ["FN45797", "Sonya"], ["FV24748", "Kenneth"],
    ["GF09766", "Ashley"], ["GG14690", "Brittany"], ["GR26216", "Kristen"], ["GW62048", "Donald"], ["GX39059", "Jonathan"],
    ["HC00233", "Raymond"], ["HL04378", "Michael"], ["HL50250", "Russell"], ["HN13964", "Dana"], ["HS58961", "Tina"],
    ["HT59273", "Robert"], ["HW01751", "Pamela"], ["HW50253", "Cindy"], ["HW65477", "Christine"], ["HX16467", "Bryan"],
    ["HX21357", "Anthony"], ["HZ41945", "James"], ["HZ96035", "Amanda"], ["KF34985", "Julie"], ["KS34599", "Alexis"],
    ["KS47739", "Lydia"], ["KS56856", "Vicki"], ["KW24617", "Samantha"], ["LG28256", "Kristin"], ["LK78228", "William"],
    ["LK78317", "Rhonda"], ["LS87752", "Kathryn"], ["LT24518", "Danielle"], ["LZ00982", "Timothy"], ["NF50295", "Anna"],
    ["NL08606", "Carmen"], ["NN03951", "Keith"], ["NP45921", "Michael"], ["NR49073", "Robin"], ["NS41086", "Kathleen"],
    ["PH79943", "Jessica"], ["PH81273", "Matthew"], ["PP73332", "James"], ["PR96113", "Daniel"], ["PW09136", "Erika"],
    ["PZ34569", "Tom"], ["RK07262", "Stephen"], ["RP54841", "Patricia"], ["RR12260", "Hannah"], ["RR16125", "Jacob"],
    ["RR52678", "Bradley"], ["RR53564", "Holly"], ["RR60662", "Shannon"], ["RR62459", "Michael"], ["RS08357", "Audrey"],
    ["RW64613", "Michelle"], ["RX39522", "Michael"], ["RX45668", "Matthew"], ["RX46250", "Denise"], ["RX46307", "Hector"],
    ["RX74391", "Brittany"], ["RX79269", "Matthew"], ["RX82727", "Tracey"], ["RX94786", "Michelle"], ["RZ08899", "Diana"],
    ["RZ25025", "Elizabeth"], ["RZ42212", "Kaitlyn"], ["SC73747", "Dave"], ["SC87824", "Debbie"], ["SC89480", "Heather"],
    ["SC89632", "Michael"], ["SF25765", "Wayne"], ["SZ88337", "Daniel"], ["TP10652", "Michael"], ["TV24571", "Jessica"],
    ["VF36699", "Jeffrey"], ["SK16113", "Julia"], ["9992", "Brenda"]
];

// Open IndexedDB
let db;

function openDatabase() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open("TransponderDatabase", 1);

        request.onupgradeneeded = function (event) {
            db = event.target.result;
            if (!db.objectStoreNames.contains("transponders")) {
                const store = db.createObjectStore("transponders", { keyPath: "id" });
                store.createIndex("name", "name", { unique: false });
            }
        };

        request.onsuccess = function (event) {
            db = event.target.result;
            console.log("IndexedDB geopend");

            // Check of de database leeg is en vul deze indien nodig
            checkAndInitializeData();
            resolve(db);
        };

        request.onerror = function (event) {
            console.error("IndexedDB fout:", event.target.error.message);
            reject(event.target.error);
        };
    });
}

document.addEventListener("DOMContentLoaded", function () {
    openDatabase(); // Open the database when the DOM is loaded
    sendIndexedDBData()
});

async function initializeDatabase() {
    try {
        db = await openDatabase();
        console.log("Database opened successfully", db);

        // Only send data when the '/' page is opened
        if (window.location.pathname === "/") {
            await sendIndexedDBData();
        }
    } catch (error) {
        console.error("Error opening database:", error);
    }
}

function loadTransponderDataFromDB() {
    const tableBody = document.getElementById("transponderTableBody");
    tableBody.innerHTML = ""; // Clear table to remove old data

    if (!db) {
        console.error("IndexedDB is not initialized.");
        return;
    }

    const transaction = db.transaction("transponders", "readonly");
    const store = transaction.objectStore("transponders");

    store.openCursor().onsuccess = function (event) {
        const cursor = event.target.result;
        if (cursor) {
            const row = document.createElement("tr");
            row.innerHTML = `
            <td>${cursor.value.id}</td>
            <td class="transponder-name">
                ${cursor.value.name}
                <button class="btn btn-danger btn-sm remove-btn" onclick="removeRow('${cursor.value.id}')">
                    <i class="bi bi-trash"></i>
                </button>
            </td>`;

            // Hide remove button by default
            const removeBtn = row.querySelector(".remove-btn");
            removeBtn.style.display = "none";

            row.addEventListener("mouseenter", () => {
                removeBtn.style.display = "inline-block";
            });

            row.addEventListener("mouseleave", () => {
                removeBtn.style.display = "none";
            });

            tableBody.appendChild(row);
            cursor.continue();
        } else {
            console.log("Finished loading transponders from IndexedDB.");
        }
    };
}

function removeRow(transponderID) {
    if (!confirm("Are you sure you want to remove this transponder?")) return;

    if (!db) {
        console.error("IndexedDB is not initialized.");
        return;
    }

    console.log(`Attempting to remove transponder ID: ${transponderID}`);

    const transaction = db.transaction("transponders", "readwrite");
    const store = transaction.objectStore("transponders");
    const request = store.delete(transponderID);

    request.onsuccess = function () {
        console.log(`Transponder ${transponderID} removed from IndexedDB.`);
        loadTransponderDataFromDB(); // Reload data from IndexedDB
    };

    request.onerror = function (event) {
        console.error("Error removing transponder:", event.target.error);
    };
}


function saveTransponderData(data) {
    if (!db) {
        console.error("Database niet geïnitialiseerd. Wachten...");
        return;
    }

    const transaction = db.transaction("transponders", "readwrite");
    const store = transaction.objectStore("transponders");

    data.forEach(([id, name]) => {
        store.put({ id, name });
    });

    transaction.oncomplete = function () {
        console.log("Alle transponders zijn toegevoegd aan IndexedDB.");
        loadTransponderDataFromDB(); // Reload from DB after saving
    };

    transaction.onerror = function (event) {
        console.error("Fout bij opslaan van transponders:", event.target.error.message);
    };
}


async function updateTransponderName(item) {
    if (!db) {
        console.error("Database niet geïnitialiseerd. Wachten...");
        db = await openDatabase();
    }

    const transaction = db.transaction("transponders", "readwrite");
    const store = transaction.objectStore("transponders");

    const getRequest = store.get(item.id);
    getRequest.onsuccess = function () {
        if (getRequest.result) {
            const updateRequest = store.put(item);
            updateRequest.onsuccess = function () {
                console.log(`Transponder ${item.id} geüpdatet naar: ${item.name}`);
            };
            updateRequest.onerror = function (event) {
                console.error("Fout bij updaten van transponder:", event.target.error.message);
            };
        } else {
            console.warn(`Transponder ${item.id} niet gevonden in IndexedDB.`);
        }
    };
    getRequest.onerror = function (event) {
        console.error("Fout bij ophalen van transponder:", event.target.error.message);
    };
}

// Search function 
async function searchTransponder() {
    if (!db) {
        console.error("Database niet beschikbaar. Wachten...");
        db = await openDatabase();
    }

    const searchQuery = document.getElementById("transponderSearch").value.trim().toLowerCase();  // Maak de zoekterm lowercase
    console.log("Searching for:", searchQuery);

    const transaction = db.transaction("transponders", "readonly");
    const store = transaction.objectStore("transponders");

    const results = [];

    store.openCursor().onsuccess = function (event) {
        const cursor = event.target.result;
        if (cursor) {
            // Zoek naar een match voor zowel ID als Name, case-insensitive
            if (cursor.value.id.toString().toLowerCase().includes(searchQuery) || cursor.value.name.toLowerCase().includes(searchQuery)) {
                results.push(cursor.value);
            }
            cursor.continue();
        } else {
            if (results.length > 0) {
                populateTable(results);
                document.getElementById("error").classList.add("hidden");
            } else {
                document.getElementById("transponderTableBody").innerHTML = "";
                document.getElementById("error").classList.remove("hidden");
            }
        }
    };

    store.openCursor().onerror = function (event) {
        console.error("Error searching data in IndexedDB", event.target.error?.message || event.target.error);
    };
}

function populateTable(data) {
    const tableBody = document.getElementById("transponderTableBody");
    tableBody.innerHTML = ""; // Clear de bestaande inhoud

    data.forEach(item => {
        const row = tableBody.insertRow();
        const cell1 = row.insertCell(0);
        const cell2 = row.insertCell(1);

        cell1.innerText = item.id;  // Transponder ID (niet bewerkbaar)
        cell2.innerText = item.name;  // Transponder Naam (wel bewerkbaar)

        // Maak de naam cell bewerkbaar
        cell2.contentEditable = true;
        cell2.addEventListener("blur", function () {
            const newName = cell2.innerText.trim();

            if (newName === "") {
                cell2.innerText = item.name; // Herstel de originele naam
            } else if (newName !== item.name) {
                item.name = newName;
                updateTransponderName(item);
            }
        });

        // Voorkom ENTER om bewerking af te ronden
        cell2.addEventListener("keypress", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                cell2.blur();
            }
        });

        // Add remove button for searched items as well
        const removeCell = row.insertCell(2);
        const removeButton = document.createElement("button");
        removeButton.className = "btn btn-danger btn-sm remove-btn";
        removeButton.innerHTML = '<i class="bi bi-trash"></i>';
        removeButton.onclick = function() {
            removeRow(item.id);
        };
        removeCell.appendChild(removeButton);
    });
}

function addTransponder() {
    const newID = document.getElementById("newTransponderID").value.trim();
    const newName = document.getElementById("newTransponderName").value.trim();

    if (newID === "" || newName === "") {
        alert("Vul zowel een Transponder ID als een Naam in!");
        return;
    }

    const transaction = db.transaction("transponders", "readwrite");
    const store = transaction.objectStore("transponders");

    const newTransponder = { id: newID, name: newName };
    const request = store.put(newTransponder);

    request.onsuccess = function () {
        console.log("Nieuwe transponder toegevoegd:", newTransponder);
        loadTransponderDataFromDB(); // Reload from DB after adding
    };

    request.onerror = function (event) {
        console.error("Fout bij toevoegen transponder:", event.target.error.message);
    };

    // Velden leegmaken na toevoegen
    document.getElementById("newTransponderID").value = "";
    document.getElementById("newTransponderName").value = "";
}

window.onload = async function () {
    try {
        db = await openDatabase();
    } catch (error) {
        console.error("Error opening database:", error);
    }
};

// Connection with the Python Backend
async function sendIndexedDBData() {
    const dbName = "TransponderDatabase";
    const storeName = "transponders"; // Corrected store name

    return new Promise((resolve, reject) => {
        const request = indexedDB.open(dbName);

        request.onsuccess = function () {
            const db = request.result;
            const tx = db.transaction(storeName, "readonly");
            const store = tx.objectStore(storeName);
            const getAllRequest = store.getAll();
            // If data is fetched successfully --> send to HTTP endpoint
            getAllRequest.onsuccess = function () {
                fetch("http://127.0.0.1:5000/upload", { // Change URL when deploying
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(getAllRequest.result)
                })
                .then(response => response.json())
                .then(data => resolve(data))
                .catch(error => reject(error));
            };
            //  Data fetch failed
            getAllRequest.onerror = function () {
                reject("Failed to read IndexedDB");
            };
        };

        request.onerror = function () {
            reject("Failed to open IndexedDB");
        };
    });
}

