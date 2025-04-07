document.addEventListener('DOMContentLoaded', function() {
    // Function to fetch leaderboard data
    function fetchLeaderboardData() {
        fetch('/api/sessions/renew_data')  // Replace with your actual endpoint
            .then(response => response.json())
            .then(data => updateLeaderboard(data))
            .then(console.log(data))
            .catch(error => console.error('Error fetching leaderboard data:', error));
    }

    // Function to update the leaderboard on the page
    function updateLeaderboard(data) {
        // Update the "Average Lap Time" section

        const transponder_names = data.transponder_names;
        if (transponder_names.length === 0) {
            console.log("No transponder names found.");
        }
        else {
            
        }

        const averagesList = document.querySelector('.average-times .column');
        if (averagesList) {
            averagesList.innerHTML = ''; // Clear existing list
            const averages = data.averages || [];
            if (averages.length === 0) {
                averagesList.innerHTML = '<li>No data available</li>';
            } else {
                averages.forEach(item => {
                    const listItem = document.createElement('li');
                    // Find the coresponding name in the dict:
                    listItem.textContent = `${transponder_names[item[1]] ?? item[1]} -- ${item[2]}s`;
                    // listItem.textContent = `${item[1]} -- ${item[2]}s`;
                    averagesList.appendChild(listItem);
                });
            }
        }

        // Update the "Fastest Laps" section
        const fastestLapsList = document.querySelector('.top-laps ol');
        if (fastestLapsList) {
            fastestLapsList.innerHTML = ''; // Clear existing list
            const topLaps = data.top_laps || [];
            if (topLaps.length === 0) {
                fastestLapsList.innerHTML = '<li>No data available</li>';
            } else {
                topLaps.forEach(lap => {
                    const listItem = document.createElement('li');
                    listItem.textContent = `${lap[0]} -- ${lap[1]}s`;
                    fastestLapsList.appendChild(listItem);
                });
            }
        }

        // Update the "Badman Lap" section
        const badmanLap = document.querySelector('.worst-lap p');
        if (badmanLap) {
            if (data.badman_lap && data.badman_lap.length > 0) {
                badmanLap.textContent = `${data.badman_lap[0][0]} -- ${data.badman_lap[0][1]}s`;
            } else {
                badmanLap.textContent = 'No data available';
            }
        }

        // Update the "Diesel Engine" section
        const diesel = document.querySelector('.diesel-engine p');
        if (diesel) {
            if (data.diesel && data.diesel.length > 0) {
                diesel.textContent = `${data.diesel[0][0]} -- ${data.diesel[0][2]}s`;
            } else {
                diesel.textContent = 'No data available';
            }
        }

        // Update the "Electrical Engine" section
        const electricalEngine = document.querySelector('.electrical-engine p');
        if (electricalEngine) {
            if (data.electrical && data.electrical.length > 0) {
                electricalEngine.textContent = `${data.electrical[0][0]} -- ${data.electrical[0][2]}s`;
            } else {
                electricalEngine.textContent = 'No data available';
            }
        }
    }

    // Initial data load
    fetchLeaderboardData();

    // Set interval to refresh data every 5 seconds
    setInterval(fetchLeaderboardData, 5000); // Refresh every 5 seconds
});