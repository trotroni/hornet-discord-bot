let cpuChart, ramChart, logsBarChart, errorsBarChart;
let logsTypeFilter = "nude-core-bot";

async function fetchStatus() {
    const res = await fetch('/api/status');
    const data = await res.json();
    document.getElementById('status-text').textContent =
        `CPU Temp: ${data.cpu_temp}°C, CPU: [${data.cpu_perc.join(", ")}]%, RAM: ${data.ram_perc}%, Bots: Core:${data.bots.core} Compta:${data.bots.compta} Server:${data.bots.server}`;
    updateCharts(data);
}

async function fetchLogs() {
    const res = await fetch('/api/logs');
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
                if(type !== logsTypeFilter) continue;
                types[type].forEach(file=>{
                    const link = document.createElement('a');
                    link.href = `/web/index.html?file=${encodeURIComponent(date+'/'+file)}`;
                    link.textContent = file;
                    link.style.marginRight='10px';
                    timeDiv.appendChild(link);
                });
            }
            dateDiv.appendChild(timeDiv);
        }
        container.appendChild(dateDiv);
    }
}

document.querySelectorAll('#logs-buttons button').forEach(btn=>{
    btn.onclick=()=>{
        logsTypeFilter=btn.dataset.type;
        fetchLogs();
    }
});

function updateCharts(data){
    // cpuChart & ramChart
    const time = new Date().toLocaleTimeString();
    if(!cpuChart){
        const ctx=document.getElementById('cpuChart').getContext('2d');
        cpuChart=new Chart(ctx,{type:'line',data:{labels:[time],datasets:data.cpu_perc.map((c,i)=>({label:'CPU'+i,data:[c],borderColor:`hsl(${i*60},100%,50%)`,fill:false}))},options:{animation:false,scales:{y:{min:0,max:100}}}});
    } else {
        cpuChart.data.labels.push(time);
        cpuChart.data.labels=cpuChart.data.labels.slice(-24);
        cpuChart.data.datasets.forEach((ds,i)=>{ds.data.push(data.cpu_perc[i]); ds.data=ds.data.slice(-24);});
        cpuChart.update();
    }

    if(!ramChart){
        const ctx=document.getElementById('ramChart').getContext('2d');
        ramChart=new Chart(ctx,{type:'line',data:{labels:[time],datasets:[{label:'RAM %',data:[data.ram_perc],borderColor:'#0ff',fill:false}]},options:{animation:false,scales:{y:{min:0,max:100}}}});
    } else {
        ramChart.data.labels.push(time);
        ramChart.data.labels=ramChart.data.labels.slice(-24);
        ramChart.data.datasets[0].data.push(data.ram_perc);
        ramChart.data.datasets[0].data=ramChart.data[0].slice(-24);
        ramChart.update();
    }
}

function sendCommand(target){
    fetch(`/api/restart?target=${target}`);
}

function refreshDashboard(){
    fetchStatus();
    fetchLogs();
}

// rafraîchissement automatique
setInterval(refreshDashboard,5000);
refreshDashboard();