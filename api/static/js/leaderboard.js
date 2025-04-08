document.addEventListener('DOMContentLoaded', function() {
    let currentIndex = 0;
    let averagesInterval;

    
    // function initialFetchLeaderboardData() {
    //     fetch('/api/sessions/renew_data')
    //     .then(response => response.json())
    //     .then(data => getDynamicInterval(data.participants))
    //     .catch(error => console.error('Error fetching leaderboard data:', error));
    // }

    // Function to fetch leaderboard data
    function fetchLeaderboardData() {
        fetch('/api/sessions/renew_data')  // Replace with your actual endpoint
            .then(response => response.json())
            .then(data => updateLeaderboard(data))
            .catch(error => console.error('Error fetching leaderboard data:', error));
    }

    function getTransponderName(id, data) {
        return data.transponder_names?.[id] ?? id;
    }
    function updateLeaderboard(data) {
        console.log(data);

        const averagesList = document.querySelector('.list-averages');
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
        const fastestLapsList = document.querySelector('.list-fastestlaps');
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
        const badmanLap = document.querySelector('.worst-lap');  
        if (badmanLap) {
            badmanLap.textContent = '';
            if (data.slow_lap && data.slow_lap.length > 0) {
                console.log(`data.slow_lap = ${data.slow_lap}`)
                badmanLap.textContent = `${getTransponderName(data.slow_lap[0][0], data)} -- ${data.slow_lap[0][1]}s`;
            } else {
                badmanLap.textContent = 'No data available';
            }
        }

        // Update the "Diesel Engine" section
        const diesel = document.querySelector('.diesel');  
        if (diesel) {
            diesel.textContent = '';
            if (data.diesel && data.diesel.length > 0) {
                diesel.textContent = `${getTransponderName(data.diesel[0][0], data)} -- ${data.diesel[0][1]}s`;
            } else {
                diesel.textContent = 'No data available';
            }
        }

        // Update the "Electrical Engine" section
        const electricalEngine = document.querySelector('.electrical');  
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
