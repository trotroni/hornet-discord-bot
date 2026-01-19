async function fetchLogs() {
    const res = await fetch('/logs');
    const logs = await res.json();
    const container = document.getElementById('logs-container');
    container.innerHTML = '';

    for (const date of Object.keys(logs).sort().reverse()) {
        const dateDiv = document.createElement('div');
        dateDiv.className = 'date-block';
        dateDiv.innerHTML = `<strong>Date: ${date}</strong>`;
        
        const times = logs[date];
        for (const hhmm of Object.keys(times).sort()) {
            const timeDiv = document.createElement('div');
            timeDiv.className = 'time-block';
            timeDiv.innerHTML = `<strong>${hhmm}</strong>`;
            
            const types = times[hhmm];
            for (const type of Object.keys(types)) {
                const typeDiv = document.createElement('div');
                typeDiv.className = 'type-block';
                typeDiv.innerHTML = `<strong>${type}</strong>: ${types[type].join(', ')}`;
                timeDiv.appendChild(typeDiv);
            }
            dateDiv.appendChild(timeDiv);
        }
        container.appendChild(dateDiv);
    }
}

// Rafraîchissement automatique toutes les 10s
setInterval(fetchLogs, 10000);
fetchLogs();