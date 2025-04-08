document.addEventListener('DOMContentLoaded', function() {
    let currentIndex = 0;
    let averagesInterval;

    // Function to fetch leaderboard data
    function initialFetchLeaderboardData() {
        fetch('/api/sessions/renew_data')
        .then(response => response.json())
        .then(data => getDynamicInterval(data.participants))
        .catch(error => console.error('Error fetching leaderboard data:', error));
    }

    function fetchLeaderboardData() {
        fetch('/api/sessions/renew_data')  // Replace with your actual endpoint
            .then(response => response.json())
            .then(data => updateLeaderboard(data))
            .catch(error => console.error('Error fetching leaderboard data:', error));
    }

    function getTransponderName(id, data) {
        return data.transponder_names?.[id] ?? id;
    }
    // TODO: Update the querySelector to match the correct element in your HTML
    // Function to update the leaderboard on the page
    function updateLeaderboard(data) {
        console.log(data);

        // Update the "Average Lap Time" section with gradual display
        const averagesList = document.querySelector('.average-times .column');      // Update here!
        if (averagesList) {
            const averages = data.averages || [];
            if (averages.length === 0) {
                averagesList.innerHTML = '<li>No data available</li>';
            } else {
                // Gradual update of the averages list (10 items per batch)
                clearInterval(averagesInterval); // Clear previous interval
                currentIndex = 0; 
                displayBatch(averages, data, averagesList);

                averagesInterval = setInterval(() => {
                    if (currentIndex < data.participants) {
                        displayBatch(averages, data, averagesList);
                    } else { clearInterval(averagesInterval); }
                }, 5000); 
            }
        }

        // Update the "Fastest Laps" section
        const fastestLapsList = document.querySelector('.top-laps ol');  // Update here!
        if (fastestLapsList) {
            fastestLapsList.innerHTML = ''; 
            const topLaps = data.top_laps || [];
            if (topLaps.length === 0) {
                fastestLapsList.innerHTML = '<li>No data available</li>';
            } else {
                topLaps.forEach(lap => {
                    const listItem = document.createElement('li');
                    listItem.textContent = `${getTransponderName(lap[0], data)} -- ${lap[1]}s`;
                    fastestLapsList.appendChild(listItem);
                });
            }
        }

        // Update the "Badman Lap" section
        const badmanLap = document.querySelector('.worst-lap p');  // Update here!
        if (badmanLap) {
            badmanLap.textContent = '';
            if (data.badman_lap && data.badman_lap.length > 0) {
                badmanLap.textContent = `${getTransponderName(data.badman_lap[0][0], data)} -- ${data.badman_lap[0][1]}s`;
            } else {
                badmanLap.textContent = 'No data available';
            }
        }

        // Update the "Diesel Engine" section
        const diesel = document.querySelector('.diesel-engine p');  // Update here!
        if (diesel) {
            diesel.textContent = '';
            if (data.diesel && data.diesel.length > 0) {
                diesel.textContent = `${getTransponderName(data.diesel[0][0], data)} -- ${data.diesel[0][1]}s`;
            } else {
                diesel.textContent = 'No data available';
            }
        }

        // Update the "Electrical Engine" section
        const electricalEngine = document.querySelector('.electrical-engine p');  // Update here!
        if (electricalEngine) {
            electricalEngine.textContent = '';
            if (data.electrical && data.electrical.length > 0) {
                electricalEngine.textContent = `${getTransponderName(data.electrical[0][0], data)} -- ${data.electrical[0][1]}s`;
            } else {
                electricalEngine.textContent = 'No data available';
            }
        }
    }

    // Helper function to display a batch of 10 items
    function displayBatch(averages, data, averagesList) {
        averagesList.innerHTML = ''; // Clear existing list before adding new batch
        // Get the next 10 items
        const batch = averages.slice(currentIndex, currentIndex + 10);
        if (batch.length > 0) {
            batch.forEach(item => {
                const listItem = document.createElement('li');
                listItem.textContent = `${getTransponderName(item[0], data)} -- ${item[1]}s`;
                averagesList.appendChild(listItem);
            });
            currentIndex += 10;
        }
        if (currentIndex >= data.participants) {
            currentIndex = 0; // Reset index when we reach the end
        }
    }

    // Initial data load
    fetchLeaderboardData();

    // Set interval to refresh data every [x] seconds
    setInterval(fetchLeaderboardData, 10000); // Refresh every 10 seconds
});
