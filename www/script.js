let cpuChart, ramChart, cpuTempChart;
let logsTypeFilter = "nude-core-bot";
const MAX_POINTS = 60; // 60 secondes d'historique

/* =========================
   FETCH STATUS
========================= */
async function fetchStatus() {
    const res = await fetch('http://server64.taimen-goblin.ts.net:8080/api/status');
    const data = await res.json();

    document.getElementById('cpu-temp').textContent = data.cpu_temp;
    document.getElementById('cpu-perc').textContent = data.cpu_perc.join(", ");
    document.getElementById('ram-perc').textContent = data.ram_perc;

    document.getElementById('bot-core').textContent = data.bots.core;
    document.getElementById('bot-compta').textContent = data.bots.compta;
    document.getElementById('bot-server').textContent = data.bots.server;

    updateCharts(data);
}


/* =========================
   FETCH LOGS
========================= */
async function fetchLogs() {
    const res = await fetch('http://server64:8080/api/logs');
    const logs = await res.json();

    const container = document.getElementById('logs-container');
    container.innerHTML = '';

    const dateKeys = Object.keys(logs).sort().reverse();

    for (const date of dateKeys) {
        const dateDiv = document.createElement('div');
        dateDiv.className = 'date-block';
        dateDiv.innerHTML = `<strong>Date: ${date}</strong>`;

        const times = logs[date];

        for (const hhmm of Object.keys(times).sort().reverse()) {
            const timeDiv = document.createElement('div');
            timeDiv.className = 'time-block';
            timeDiv.innerHTML = `<strong>${hhmm}</strong>`;

            const types = times[hhmm];

            for (const type of Object.keys(types)) {
                if (type !== logsTypeFilter) continue;

                types[type].forEach(file => {
                    const link = document.createElement('a');
                    link.href = `/web/index.html?file=${encodeURIComponent(date + '/' + file)}`;
                    link.textContent = file;
                    link.style.marginRight = '10px';
                    timeDiv.appendChild(link);
                });
            }
            dateDiv.appendChild(timeDiv);
        }
        container.appendChild(dateDiv);
    }
}

/* =========================
   LOG FILTER BUTTONS
========================= */
document.querySelectorAll('#logs-buttons button').forEach(btn => {
    btn.onclick = () => {
        logsTypeFilter = btn.dataset.type;
        fetchLogs();
    };
});

/* =========================
   UPDATE CHARTS
========================= */
function updateCharts(data) {
    const time = new Date().toLocaleTimeString();

    /* ===== CPU % PER CORE ===== */
    if (!cpuChart) {
        const ctx = document.getElementById('cpuChart').getContext('2d');
        cpuChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [time],
                datasets: data.cpu_perc.map((c, i) => ({
                    label: `CPU ${i} – ${c}%`,
                    data: [c],
                    borderColor: `hsl(${i * 60}, 100%, 50%)`,
                    fill: false
                }))
            },
            options: {
                animation: false,
                scales: { y: { min: 0, max: 100 } }
            }
        });
    } else {
        cpuChart.data.labels.push(time);
        cpuChart.data.labels = cpuChart.data.labels.slice(-MAX_POINTS);

        cpuChart.data.datasets.forEach((ds, i) => {
            const value = data.cpu_perc[i];
            ds.label = `CPU ${i} – ${value}%`;
            ds.data.push(value);
            ds.data = ds.data.slice(-MAX_POINTS);
        });
        cpuChart.update();
    }

    /* ===== CPU TEMPERATURE ===== */
    if (!cpuTempChart) {
        const ctx = document.getElementById('cpuTempChart').getContext('2d');
        cpuTempChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [time],
                datasets: [{
                    label: `CPU Température – ${data.cpu_temp} °C`,
                    data: [data.cpu_temp],
                    borderColor: '#ff4d4d',
                    fill: false
                }]
            },
            options: {
                animation: false,
                scales: { y: { min: 0, max: 100 } }
            }
        });
    } else {
        const temp = data.cpu_temp;
        cpuTempChart.data.labels.push(time);
        cpuTempChart.data.labels = cpuTempChart.data.labels.slice(-MAX_POINTS);

        cpuTempChart.data.datasets[0].label = `CPU Température – ${temp} °C`;
        cpuTempChart.data.datasets[0].data.push(temp);
        cpuTempChart.data.datasets[0].data =
            cpuTempChart.data.datasets[0].data.slice(-MAX_POINTS);

        cpuTempChart.update();
    }

    /* ===== RAM ===== */
    if (!ramChart) {
        const ctx = document.getElementById('ramChart').getContext('2d');
        ramChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [time],
                datasets: [{
                    label: `RAM – ${data.ram_perc}%`,
                    data: [data.ram_perc],
                    borderColor: '#00ffff',
                    fill: false
                }]
            },
            options: {
                animation: false,
                scales: { y: { min: 0, max: 100 } }
            }
        });
    } else {
        const ram = data.ram_perc;
        ramChart.data.labels.push(time);
        ramChart.data.labels = ramChart.data.labels.slice(-MAX_POINTS);

        ramChart.data.datasets[0].label = `RAM – ${ram}%`;
        ramChart.data.datasets[0].data.push(ram);
        ramChart.data.datasets[0].data =
            ramChart.data.datasets[0].data.slice(-MAX_POINTS);

        ramChart.update();
    }
}

/* =========================
   COMMANDS
========================= */
function sendCommand(target) {
    fetch(`/api/restart?target=${target}`);
}

function refreshDashboard() {
    fetchStatus();
    fetchLogs();
}

/* =========================
   AUTO REFRESH (1s)
========================= */
setInterval(refreshDashboard, 1000);
refreshDashboard();
