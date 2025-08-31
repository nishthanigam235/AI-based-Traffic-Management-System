const socket = io("http://localhost:5000");

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
    socket.on(`vehicle_count_${i}`, (data) => {
        document.getElementById(`vehicleCount${i}`).textContent = data.count;
        const now = new Date().toLocaleTimeString();
        const chart = chartConfigs[i];
        chart.data.labels.push(now);
        chart.data.datasets[0].data.push(data.count);

        if (chart.data.labels.length > 20) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }
        chart.update();
    });
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

// Listen for real-time traffic light updates via SocketIO
socket.on("traffic_lights", (data) => {
    updateLights(data);
});

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
