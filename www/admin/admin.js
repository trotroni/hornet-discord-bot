const TOKEN = "CHANGE_MOI";

function enable() {
    const code = document.getElementById("code").value;
    fetch(`/api/admin/set?code=${code}&token=${TOKEN}`)
        .then(r => r.json())
        .then(updateStatus)
        .catch(err => alert(err));
}

function disable() {
    fetch(`/api/admin/disable?token=${TOKEN}`)
        .then(r => r.json())
        .then(updateStatus)
        .catch(err => alert(err));
}

function updateStatus(data) {
    document.getElementById("status").innerText =
        "État serveur : " + (data.enabled ? `FORCÉ (${data.code})` : "NORMAL");
}
