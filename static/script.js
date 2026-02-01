

// Initialize charts for each video
const chartConfigs = {};
for (let i = 1; i <= 4; i++) {
    const ctx = document.getElementById(`vehicleChart${i}`).getContext('2d');
    chartConfigs[i] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: `Vehicle Count (Camera ${i})`,
                data: [],
                borderColor: 'rgba(75, 192, 192, 1)',
                tension: 0.3,
                fill: false
            }]
        },
        options: {
            scales: {
                x: { title: { display: true, text: 'Time' } },
                y: { title: { display: true, text: 'Vehicles' }, beginAtZero: true }
            }
        }
    });

    // Listen for vehicle count updates
}
async function fetchVehicleCounts() {
    const res = await fetch("/get_vehicle_counts");
    const data = await res.json();

    for (let i = 1; i <= 4; i++) {
        document.getElementById(`vehicleCount${i}`).innerText = data[i];
    }

    updateCharts(data);
}

function updateCharts(data) {
    const timeLabel = new Date().toLocaleTimeString();

    for (let i = 1; i <= 4; i++) {
        const chart = chartConfigs[i];

        chart.data.labels.push(timeLabel);
        chart.data.datasets[0].data.push(data[i]);

        // keep only last 20 points
        if (chart.data.labels.length > 20) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }

        chart.update();
    }
}


// Function to update traffic lights on frontend
function updateLights(lights) {
    for (let i = 1; i <= 4; i++) {
        const redLight = document.getElementById(`red${i}`);
        const greenLight = document.getElementById(`green${i}`);
        const statusText = document.getElementById(`lightStatus${i}`);

        if (lights[i] === "GREEN") {
            greenLight.classList.add("active");
            redLight.classList.remove("active");
            statusText.textContent = "🟢 Green";
        } else {
            redLight.classList.add("active");
            greenLight.classList.remove("active");
            statusText.textContent = "🔴 Red";
        }
    }
}
async function fetchLightStatus() {
    const res = await fetch("/light_status");
    const data = await res.json();
    updateLights(data);
}



// Fallback polling in case SocketIO misses updates
async function fetchLightStatus() {
    try {
        const response = await fetch("/light_status");
        if (!response.ok) return;
        const data = await response.json();
        updateLights(data);
    } catch (err) {
        console.error("Error fetching light status:", err);
    }
}
setInterval(fetchLightStatus, 2000);
fetchLightStatus(); // Initial call

// Download CSV functionality
function downloadCSV(videoId) {
    window.location.href = `/download_logs/${videoId}`;
}
setInterval(() => {
    fetchVehicleCounts();
    fetchLightStatus();
}, 2000);

fetchVehicleCounts();
fetchLightStatus();
