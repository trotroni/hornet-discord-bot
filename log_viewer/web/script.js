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
                typeDiv.innerHTML = `<strong>${type}</strong>: `;

                types[type].forEach(file => {
                    const fileLink = document.createElement('a');
                    fileLink.href = "#";
                    fileLink.textContent = file;
                    fileLink.style.marginRight = "10px";
                    fileLink.onclick = async () => {
                        const contentRes = await fetch(`/read_log?file=${encodeURIComponent(date + '/' + file)}`);
                        const content = await contentRes.text();
                        showLogContent(file, content);
                    };
                    typeDiv.appendChild(fileLink);
                });

                timeDiv.appendChild(typeDiv);
            }
            dateDiv.appendChild(timeDiv);
        }
        container.appendChild(dateDiv);
    }
}

// afficher le contenu du log dans une zone dédiée
function showLogContent(filename, content) {
    let logViewer = document.getElementById('log-viewer');
    if (!logViewer) {
        logViewer = document.createElement('pre');
        logViewer.id = 'log-viewer';
        logViewer.style.border = "1px solid #333";
        logViewer.style.padding = "10px";
        logViewer.style.marginTop = "20px";
        logViewer.style.maxHeight = "400px";
        logViewer.style.overflowY = "scroll";
        document.body.appendChild(logViewer);
    }
    logViewer.textContent = `=== ${filename} ===\n\n` + content;
}

setInterval(fetchLogs, 10000);
fetchLogs();